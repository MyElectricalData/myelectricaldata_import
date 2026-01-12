import logging
from datetime import datetime
from types import SimpleNamespace

import pytest

from conftest import contains_logline


@pytest.mark.parametrize("usage_point_id", ["pdl1"])
@pytest.mark.parametrize(
    "status_response, last_call, expected_last_call",
    [
        (
            {
                "consent_expiration_date": "2099-01-01T00:00:00",
                "call_number": 42,
                "quota_limit": 42,
                "quota_reached": 42,
                "quota_reset_at": "2099-01-01T00:00:00.000000",
                "ban": False,
            },
            datetime(2024, 1, 1, 15, 30),
            "15:30",
        ),
        ({"error": True, "description": "failure"}, None, None),
    ],
)
def test_get_account_status(mocker, usage_point_id, caplog, status_response, last_call, expected_last_call):
    from models.ajax import Ajax

    m_status = mocker.patch("external_services.myelectricaldata.status.Status.status")
    m_status.return_value = status_response
    mocker.patch(
        "database.usage_points.DatabaseUsagePoints.get",
        return_value=SimpleNamespace(token="mock-token", cache=True, last_call=last_call),
    )

    ajax = Ajax(usage_point_id=usage_point_id)

    res = ajax.account_status()

    assert m_status.call_count == 1
    assert res == {**status_response, "last_call": expected_last_call}
    assert contains_logline(caplog, "[PDL1] CHECK DU STATUT DU COMPTE.", logging.INFO)
