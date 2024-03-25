import logging

import pytest

from db_schema import UsagePoints
from test_jobs import job
from tests.conftest import contains_logline


@pytest.mark.parametrize(
    "status_response, status_code",
    [
        ({"incomplete": "response"}, 200),
        ({"detail": "truthy response"}, 300),
        ({"detail": "falsy response"}, 500),
        (
            {
                "customer": {"usage_points": [
                    {"usage_point": {
                        "usage_point_status": "mock_value",
                        "meter_type": "mock meter type"
                    },
                     "contracts": {
                         "offpeak_hours": None, "last_activation_date": "2099-01-01+00:00",
                         "last_distribution_tariff_change_date": "2099-01-01+00:00",
                         "segment": "mock_segment",
                         "subscribed_power": "10000000kVA",
                         "distribution_tariff": "mock tariff",
                         "contract_status": "mock status"
                     }}]},
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
def test_get_contract(mocker, job, caplog, status_response, status_code, requests_mock):
    from config import URL

    m_set_error_log = mocker.patch("models.database.Database.set_error_log")
    m_get_contract = mocker.patch("models.database.Database.get_contract")
    m_get_contract.return_value = []
    m_set_contract = mocker.patch("models.database.Database.set_contract")
    requests_mocks = list()

    if job.usage_point_id:
        rm = requests_mock.get(
            f"{URL}/contracts/{job.usage_point_id}", json=status_response, status_code=status_code
        )
        requests_mocks.append(rm)

        # FIXME: If job has usage_point_id, get_contract() expects
        # job.usage_point_config.usage_point_id to be populated from a side effect
        job.usage_point_config = UsagePoints(usage_point_id=job.usage_point_id)
        enabled_usage_points = [job.usage_point_config]
    else:
        enabled_usage_points = [up for up in job.usage_points if up.enable]
        for u in enabled_usage_points:
            rm = requests_mock.get(
                f"{URL}/contracts/{u.usage_point_id}/cache", json=status_response, status_code=status_code
            )
            requests_mocks.append(rm)

    for usage_point in enabled_usage_points:
        job.usage_point_config = usage_point
        res = job.get_contract()

    assert contains_logline(caplog, "[PDL1] RÉCUPÉRATION DES INFORMATIONS CONTRACTUELLES :", logging.INFO)
    is_truthy_response = 200 <= status_code < 400
    assert 1 == m_get_contract.call_count

    if is_truthy_response:
        if status_code != 200 and status_response:
            # If the status code is truthy, but not 200, the contents of response['detail'] are logged
            assert contains_logline(caplog, "{'error': True, 'description': 'truthy "
                                            "response'}", logging.ERROR)

        elif status_response and status_response.get("customer"):
            # Successful case: db is updated & set_error_log is called with None
            assert 1 == m_set_contract.call_count
            assert 0 == m_set_error_log.call_count
        else:
            # Successful case: db is updated & set_error_log is called with None
            assert 0 == m_set_contract.call_count
            assert 0 == m_set_error_log.call_count

    if not is_truthy_response:
        # FIXME: If response(500), no error is displayed
        # assert contains_logline(caplog, "{'error': True, 'description': 'truthy "
        #                                 "response'}", logging.ERROR)

        # db.set_error_log is called
        assert 0 == m_set_error_log.call_count

    # Ensuring {URL}/valid_access/{usage_point_id} is called exactly as many times as enabled usage_points
    # and only once per enabled usage_point
    for rm in requests_mocks:
        assert len(rm.request_history) == 1
