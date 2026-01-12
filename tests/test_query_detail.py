import dataclasses
import datetime
from unittest import mock

import pytest
from const import TIMEZONE


@dataclasses.dataclass
class MockResponse:
    status_code: int
    text: str = ""


@pytest.mark.parametrize("measure_type", ["consumption", "production"])
def test_get(mocker, measure_type):
    from external_services.myelectricaldata.detail import Detail

    m_get: mock.Mock = mocker.patch("models.query.Query.get")
    m_insert_detail: mock.Mock = mocker.patch("database.detail.DatabaseDetail.insert")
    m_get.return_value = MockResponse(
        status_code=200,
        text='{"meter_reading": {"interval_reading": [{"interval_length": "30", '
        '"value": "10", "date": "2024-01-01 00:00:00"}]}}',
    )

    # Instantiating a Detail class, pointing to a valid usage_point_id
    d = Detail(headers="any", usage_point_id="pdl1", measure_type=measure_type)

    # Using a very large max_detail value so that the mock is called only once
    d.max_detail = 3650

    # Triggering Details.get(), which should
    # - call m_get mock, which returns the value above
    # - call m_insert_detail with parameters that are consistent with the value returned at the previous step
    d.get()

    # Query.get() should only be called once, with no parameter
    m_get.assert_called_once_with()
    # Database.insert_details() should only be called once, with parameters below
    expected_date = TIMEZONE.localize(datetime.datetime(2024, 1, 1, 0, 30))
    m_insert_detail.assert_called_once_with(
        date=expected_date,
        value="10",
        interval="30",
        blacklist=0,
    )
