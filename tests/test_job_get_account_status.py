import pytest
from test_jobs import job

from db_schema import UsagePoints
from tests.conftest import contains_logline
import logging


@pytest.mark.parametrize(
    "status_response, status_code",
    [
        ({"incomplete": "response"}, 200),
        ({"detail": "truthy response"}, 300),
        ({"detail": "falsy response"}, 500),
        (
            {
                "consent_expiration_date": "2099-01-01T00:00:00",
                "call_number": 42,
                "quota_limit": 42,
                "quota_reached": 42,
                "quota_reset_at": "2099-01-01T00:00:00.000000",
                "ban": False,
            },
            200,
        ),
    ],
)
def test_get_account_status(mocker, job, caplog, status_response, status_code, requests_mock):
    from config import URL

    m_set_error_log = mocker.patch("models.database.Database.set_error_log")
    m_usage_point_update = mocker.patch("models.database.Database.usage_point_update")
    mocker.patch("models.jobs.Job.header_generate")
    requests_mocks = list()

    if job.usage_point_id:
        rm = requests_mock.get(
            f"{URL}/valid_access/{job.usage_point_id}/cache", json=status_response, status_code=status_code
        )
        requests_mocks.append(rm)
        expected_count = 1
        # FIXME: If job has usage_point_id, get_account_status() expects
        # job.usage_point_config.usage_point_id to be populated from a side effect
        job.usage_point_config = UsagePoints(usage_point_id=job.usage_point_id)
        enabled_usage_points = [job.usage_point_config]
    else:
        enabled_usage_points = [up for up in job.usage_points if up.enable]
        for u in enabled_usage_points:
            rm = requests_mock.get(
                f"{URL}/valid_access/{u.usage_point_id}/cache", json=status_response, status_code=status_code
            )
            requests_mocks.append(rm)
        expected_count = len(enabled_usage_points)

    res = job.get_account_status()

    assert contains_logline(caplog, "[PDL1] RÉCUPÉRATION DES INFORMATIONS DU COMPTE :", logging.INFO)
    is_complete = {
        "consent_expiration_date",
        "call_number",
        "quota_limit",
        "quota_reached",
        "quota_reset_at",
        "ban",
    }.issubset(set(status_response.keys()))
    is_truthy_response = 200 <= status_code < 400

    if is_truthy_response:
        if status_code != 200:
            # If the status code is truthy, but not 200, the contents of response['detail'] are logged
            assert contains_logline(caplog, status_response["detail"], logging.ERROR)

        if not is_complete:
            # If some fields are missing from a truthy response, an exception is thrown and an error message is
            # displayed
            assert contains_logline(caplog, "Erreur lors de la récupération des informations du compte", logging.ERROR)

            # db.usage_point_update is not called
            assert 0 == m_usage_point_update.call_count
            # FIXME: db.set_error_log is not called, because returned errors are missing status_code and
            #  description.detail
            # assert 1 == m_set_error_log.call_count

        if is_complete and status_code == 200:
            # Successful case: db is updated & set_error_log is called with None
            assert 1 == m_usage_point_update.call_count
            assert expected_count == m_set_error_log.call_count
            for u in enabled_usage_points:
                m_set_error_log.assert_called_once_with(u.usage_point_id, None)

    if not is_truthy_response:
        # FIXME: If response(500), no error is displayed
        # assert contains_logline(caplog, "Erreur lors de la récupération des informations du compte", logging.ERROR)

        # db.set_error_log is called
        assert expected_count == m_set_error_log.call_count
        for u in enabled_usage_points:
            m_set_error_log.assert_called_once_with(u.usage_point_id, f"{status_code} - {status_response['detail']}")

    # Ensuring {URL}/valid_access/{usage_point_id} is called exactly as many times as enabled usage_points
    # and only once per enabled usage_point
    for rm in requests_mocks:
        assert len(rm.request_history) == 1
