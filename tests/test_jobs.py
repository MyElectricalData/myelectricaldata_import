import pytest
from db_schema import UsagePoints
from conftest import setenv

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
        assert "WARNING  root:jobs.py:50 => Import job disable\n" == caplog.text
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
    assert "INFO     root:dependencies.py:88 DÉMARRAGE DU JOB D'IMPORTATION DANS 10S\n" in caplog.text
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
    "method, patch, details, line_no",
    [
        ("get_contract", "models.query_contract.Contract.get", "Récupération des informations contractuelles", 221),
        ("get_addresses", "models.query_address.Address.get", "Récupération des coordonnées postales", 242),
        ("get_consumption", "models.query_daily.Daily.get", "Récupération de la consommation journalière", 266),
        ("get_consumption_detail", "models.query_detail.Detail.get", "Récupération de la consommation détaillée", 290),
        ("get_production", "models.query_daily.Daily.get", "Récupération de la production journalière", 318),
        ("get_production_detail", "models.query_detail.Detail.get", "Récupération de la production détaillée", 346),
        (
                "get_consumption_max_power",
                "models.query_power.Power.get",
                "Récupération de la puissance maximum journalière",
                367,
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
def test_get_no_return_check(mocker, job, caplog, side_effect, return_value, method, patch, details, line_no):
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
        # This method uses self.usage_point_id instead of usage_point_id
        assert f"INFO     root:dependencies.py:88 [NONE] {details.upper()} :" in caplog.text
    else:
        assert f"INFO     root:dependencies.py:88 [PDL1] {details.upper()} :" in caplog.text

    if side_effect:
        # When get() throws an exception, no error is displayed
        assert f"ERROR    root:jobs.py:{line_no} Erreur lors de la {details.lower()}" in caplog.text
        assert f"ERROR    root:jobs.py:{line_no + 1} {side_effect}" in caplog.text
    elif return_value:
        # No matter what get() returns, the method will never log an error
        assert f"ERROR    root:jobs.py:{line_no} Erreur lors de la {details.lower()}" not in caplog.text
        assert f"ERROR    root:jobs.py:{line_no + 1} 'status_code'" not in caplog.text

    # Ensuring method is called exactly as many times as enabled usage_points
    assert expected_count == m.call_count

    # set_error_log is never called
    m_set_error_log.assert_not_called()
