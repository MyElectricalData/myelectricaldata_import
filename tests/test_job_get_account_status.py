import logging

import pytest

from conftest import contains_logline
from test_jobs import job  # noqa: F401
from types import SimpleNamespace


@pytest.mark.parametrize(
    "status_return, expected_message",
    [
        (
            {"error": True, "status_code": 500, "description": {"detail": "failure"}},
            "500 - failure",
        ),
        (
            {
                "consent_expiration_date": "2099-01-01T00:00:00",
                "call_number": 42,
                "quota_limit": 42,
                "quota_reached": 42,
                "quota_reset_at": "2099-01-01T00:00:00.000000",
                "ban": False,
            },
            None,
        ),
    ],
)
def test_get_account_status(mocker, job, caplog, status_return, expected_message):
    m_status = mocker.patch(
        "external_services.myelectricaldata.status.Status.status",
        return_value=status_return,
    )
    m_set_error_log = mocker.patch("database.usage_points.DatabaseUsagePoints.set_error_log")

    usage_point_id = job.usage_point_id or "pdl1"
    usage_point = SimpleNamespace(usage_point_id=usage_point_id, enable=True, token="mock-token")
    job.usage_points_all = [usage_point]
    job.usage_point_config = usage_point if job.usage_point_id else None
    usage_points = [usage_point]

    job.get_account_status()

    assert m_status.call_count == len(usage_points)
    assert m_set_error_log.call_count == len(usage_points)
    for call in m_set_error_log.call_args_list:
        assert call.args[0] == expected_message

    assert contains_logline(caplog, "[PDL1] RÉCUPÉRATION DES INFORMATIONS DU COMPTE", logging.INFO)
