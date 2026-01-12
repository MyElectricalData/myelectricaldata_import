import logging

import pytest

from conftest import contains_logline
from db_schema import UsagePoints

EXPORT_METHODS = ["export_influxdb", "export_home_assistant_ws", "export_home_assistant", "export_mqtt"]
PER_USAGE_POINT_METHODS = [
    "get_account_status",
    "get_contract",
    "get_addresses",
    "get_consumption",
    "get_consumption_detail",
    "get_production",
    "get_production_detail",
    "get_consumption_max_power",
    "stat_price",
] + EXPORT_METHODS
PER_JOB_METHODS = ["get_tempo", "get_ecowatt"]


@pytest.fixture(params=[None, "pdl1"])
def job(request):
    from models.jobs import Job

    print(f"Using job with usage point id = {request.param}")
    job = Job(request.param)
    job.wait_job_start = 1
    yield job


@pytest.mark.parametrize("envvar_to_true", [None, "DEV", "DEBUG"])
def test_boot(mocker, caplog, job, envvar_to_true):
    m = mocker.patch("models.jobs.Job.job_import_data")

    if envvar_to_true:
        mocker.patch("models.jobs.APP_CONFIG.dev", True)
        res = job.boot()
    else:
        res = job.boot()

    assert res is None
    if envvar_to_true:
        assert 0 == m.call_count, "job_import_data should not be called"
        assert contains_logline(caplog, "=> Import job disable", logging.WARNING)
    else:
        assert "" == caplog.text
        m.assert_called_once()


def test_job_import_data(mocker, job, caplog):
    mockers = {}
    for method in PER_JOB_METHODS + PER_USAGE_POINT_METHODS:
        mockers[method] = mocker.patch(f"models.jobs.Job.{method}")

    mocker.patch("database.DB.lock_status", return_value=False)
    mocker.patch("database.DB.lock")
    mocker.patch("database.DB.unlock")

    count_enabled_jobs = len([j for j in job.usage_points_all if getattr(j, "enable", False)])

    res = job.job_import_data(target=None)

    # FIXME: Logline says 10s regardless of job.wait_job_start
    # assert contains_logline(caplog, f"DÉMARRAGE DU JOB D'IMPORTATION DANS {job.wait_job_start}S", logging.INFO)
    assert res["status"] is True

    for method, m in mockers.items():
        if method in PER_JOB_METHODS:
            assert m.call_count == 1
        else:
            assert m.call_count == count_enabled_jobs
        m.reset_mock()


def test_header_generate(job, caplog):
    from utils import get_version

    expected_logs = ""
    # FIXME: header_generate() assumes job.usage_point_config is populated from a side effect
    for job.usage_point_config in job.usage_points_all:
        assert {
            "Authorization": job.usage_point_config.token,
            "Content-Type": "application/json",
            "call-service": "myelectricaldata",
            "version": get_version(),
        } == job.header_generate()
    assert expected_logs == caplog.text


@pytest.mark.parametrize(
    "method, patch, details",
    [
        (
            "get_contract",
            "external_services.myelectricaldata.contract.Contract.get",
            "Récupération des informations contractuelles",
        ),
        (
            "get_addresses",
            "external_services.myelectricaldata.address.Address.get",
            "Récupération des coordonnées postales",
        ),
        (
            "get_consumption",
            "external_services.myelectricaldata.daily.Daily.get",
            "Récupération de la consommation journalière",
        ),
        (
            "get_consumption_detail",
            "external_services.myelectricaldata.detail.Detail.get",
            "Récupération de la consommation détaillée",
        ),
        (
            "get_production",
            "external_services.myelectricaldata.daily.Daily.get",
            "Récupération de la production journalière",
        ),
        (
            "get_production_detail",
            "external_services.myelectricaldata.detail.Detail.get",
            "Récupération de la production détaillée",
        ),
        (
            "get_consumption_max_power",
            "external_services.myelectricaldata.power.Power.get",
            "Récupération de la puissance maximum journalière",
        ),
    ],
)
@pytest.mark.parametrize(
    "return_value",
    [
        {},
        {"any_key": "any_value"},
        {"error": "only"},
        {"error": "with all fields", "status_code": "5xx", "description": {"detail": "proper error"}},
    ],
)
@pytest.mark.parametrize("side_effect", [None, Exception("Mocker: call failed")])
def test_get_no_return_check(mocker, job, caplog, side_effect, return_value, method, patch, details):
    """This test covers all methods that call "get" methods from query objects:
    - without checking for their return value
    - without calling set_error_log on failure
    """
    m = mocker.patch(patch)
    m_set_error_log = mocker.patch("database.usage_points.DatabaseUsagePoints.set_error_log")
    mocker.patch("models.jobs.Job.header_generate")

    m.side_effect = side_effect
    m.return_value = return_value

    enabled_usage_points = [up for up in job.usage_points_all if getattr(up, "enable", False)]
    if not job.usage_point_id:
        expected_count = len(enabled_usage_points)
    else:
        expected_count = 1
        # We no longer have access to the config helper, so just set the known flags manually.
        job.usage_point_config = UsagePoints(
            usage_point_id=job.usage_point_id,
            consumption=True,
            consumption_detail=True,
            production=True,
            production_detail=True,
        )

    res = getattr(job, method)()

    if method == "get_consumption_max_power" and job.usage_point_id is None:
        # FIXME: This method uses self.usage_point_id instead of usage_point_id
        # assert contains_logline(caplog, "[PDL1] {details.upper()} :", logging.INFO)
        pass
    else:
        assert contains_logline(caplog, f"[PDL1] {details.upper()}", logging.INFO)

    if side_effect:
        # When get() throws an exception, no error is displayed
        assert contains_logline(caplog, f"Erreur lors de la {details.lower()}", logging.ERROR)
        assert contains_logline(caplog, str(side_effect), logging.ERROR)
    elif return_value:
        # FIXME: No matter what get() returns, the method will never log an error
        # assert contains_logline(caplog, f"Erreur lors de la {details.lower()}", logging.ERROR)
        # assert contains_logline(caplog, 'status_code', logging.ERROR)
        pass

    # Ensuring method is called exactly as many times as enabled usage_points
    assert expected_count == m.call_count

    # set_error_log is never called
    m_set_error_log.assert_not_called()
