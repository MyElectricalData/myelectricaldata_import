import logging

import pytest
from conftest import setenv, contains_logline

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
PER_JOB_METHODS = ["get_gateway_status", "get_tempo", "get_ecowatt"]


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
        with setenv(**{envvar_to_true: "true"}):
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

    count_enabled_jobs = len([j for j in job.usage_points if j.enable])

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
    from dependencies import get_version

    expected_logs = ""
    # FIXME: header_generate() assumes job.usage_point_config is populated from a side effect
    for job.usage_point_config in job.usage_points:
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
        ("get_contract", "models.query_contract.Contract.get", "Récupération des informations contractuelles"),
        ("get_addresses", "models.query_address.Address.get", "Récupération des coordonnées postales"),
        ("get_consumption", "models.query_daily.Daily.get", "Récupération de la consommation journalière"),
        ("get_consumption_detail", "models.query_detail.Detail.get", "Récupération de la consommation détaillée"),
        ("get_production", "models.query_daily.Daily.get", "Récupération de la production journalière"),
        ("get_production_detail", "models.query_detail.Detail.get", "Récupération de la production détaillée"),
        (
            "get_consumption_max_power",
            "models.query_power.Power.get",
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
    """
    This test covers all methods that call "get" methods from query objects:
    - without checking for their return value
    - without calling set_error_log on failure
    """

    m = mocker.patch(patch)
    m_set_error_log = mocker.patch("models.database.Database.set_error_log")
    mocker.patch("models.jobs.Job.header_generate")

    m.side_effect = side_effect
    m.return_value = return_value

    conf = job.config.usage_point_id_config(job.usage_point_id)
    enabled_usage_points = [up for up in job.usage_points if up.enable]
    if not job.usage_point_id:
        expected_count = len(enabled_usage_points)
    else:
        expected_count = 1
        # FIXME: If job has usage_point_id, get_account_status() expects
        # job.usage_point_config.usage_point_id to be populated from a side effect
        job.usage_point_config = UsagePoints(
            usage_point_id=job.usage_point_id,
            consumption=conf.get("consumption"),
            consumption_detail=conf.get("consumption_detail"),
            production=conf.get("production"),
            production_detail=conf.get("production_detail"),
        )

    res = getattr(job, method)()

    if method == "get_consumption_max_power" and job.usage_point_id is None:
        # FIXME: This method uses self.usage_point_id instead of usage_point_id
        # assert contains_logline(caplog, "[PDL1] {details.upper()} :", logging.INFO)
        pass
    else:
        assert contains_logline(caplog, f"[PDL1] {details.upper()} :", logging.INFO)

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
