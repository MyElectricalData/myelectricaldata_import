import logging

import pytest

from tests.conftest import contains_logline


@pytest.mark.parametrize("usage_point_id", ["pdl1"])
@pytest.mark.parametrize(
    "status_response, status_code",
    [
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
def test_get_account_status(mocker, usage_point_id, caplog, status_response, status_code, requests_mock):
    from models.ajax import Ajax
    from config import URL

    default_error_message = 'Erreur lors de la récupération du statut du compte.'

    m_usage_point_update = mocker.patch("models.database.Database.usage_point_update")
    m_set_error_log = mocker.patch("models.database.Database.set_error_log")

    requests_mocks = list()
    requests_mocks.append(requests_mock.get(
        f"{URL}/valid_access/{usage_point_id}/cache", json=status_response, status_code=status_code
    ))

    ajax = Ajax(usage_point_id=usage_point_id) if usage_point_id else Ajax()

    is_complete = {
        "consent_expiration_date",
        "call_number",
        "quota_limit",
        "quota_reached",
        "quota_reset_at",
        "ban",
    }.issubset(set(status_response.keys()))
    is_truthy_response = 200 <= status_code < 400

    res = ajax.account_status()

    if is_truthy_response:
        if status_code != 200 or not is_complete:
            assert contains_logline(caplog, status_response.get('detail', default_error_message), logging.ERROR)
            assert res == {'description': status_response.get('detail', default_error_message), 'error': True, 'last_call': None}

            # db.usage_point_update is not called
            assert 0 == m_usage_point_update.call_count
            # FIXME: db.set_error_log is not called, because returned errors are missing status_code and description.detail
            assert 0 == m_set_error_log.call_count

        if is_complete and status_code == 200:
            # Successful case: db is updated & set_error_log is called with None
            assert 1 == m_usage_point_update.call_count
            # FIXME: Ajax does not use set_error_log while Job does
            assert 0 == m_set_error_log.call_count
            assert res == {**status_response, "last_call": None}

    if not is_truthy_response:
        # FIXME: If response(500), no error is displayed
        assert not contains_logline(caplog, "Erreur lors de la récupération des informations du compte", logging.ERROR)
        # FIXME: Ajax does not use set_error_log while Job does
        assert 0 == m_set_error_log.call_count
        assert res == {'description': status_response,
                       'error': True,
                       'last_call': None,
                       'status_code': status_code}

    # Ensuring {URL}/valid_access/{usage_point_id} is called exactly as many times as enabled usage_points
    # and only once per enabled usage_point
    for rm in requests_mocks:
        assert len(rm.request_history) == 1

    assert contains_logline(caplog, "[PDL1] CHECK DU STATUT DU COMPTE.", logging.INFO)
