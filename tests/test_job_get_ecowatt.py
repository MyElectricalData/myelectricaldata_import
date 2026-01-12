import logging
from datetime import datetime
from dateutil.relativedelta import relativedelta
import pytest
from conftest import contains_logline
from test_jobs import job  # noqa: F401


@pytest.mark.parametrize(
    "response, status_code",
    [
        (None, 200),
        (None, 500),
        ({"2099-01-01": {"value": 9000, "message": "mock message", "detail": "mock detail"}}, 200),
    ],
)
def test_get_ecowatt(mocker, job, caplog, requests_mock, response, status_code):
    from const import URL

    start = (datetime.now() - relativedelta(years=3)).strftime("%Y-%m-%d")
    end = (datetime.now() + relativedelta(days=3)).strftime("%Y-%m-%d")

    m_db_get_ecowatt = mocker.patch("database.ecowatt.DatabaseEcowatt.get")
    m_db_set_ecowatt = mocker.patch("database.ecowatt.DatabaseEcowatt.set")

    m_db_get_ecowatt.return_value = []
    requests_mock.get(f"{URL}/rte/ecowatt/{start}/{end}", json=response, status_code=status_code)

    job.get_ecowatt()

    assert contains_logline(caplog, "RÉCUPÉRATION DES DONNÉES ECOWATT", logging.INFO)
    if status_code != 200:
        assert m_db_get_ecowatt.call_count == 1
        assert m_db_set_ecowatt.call_count == 0

        # FIXME: No error is displayed
        # assert contains_logline(caplog, "{'error': True, 'description': 'Erreur "
        #  "lors de la récupération des données Ecowatt.'}", logging.ERROR)

    if status_code == 200:
        if response:
            assert m_db_get_ecowatt.call_count == 1
            assert m_db_set_ecowatt.call_count == 1

            assert not contains_logline(
                caplog,
                "{'error': True, 'description': 'Erreur " "lors de la récupération des données Ecowatt.'}",
                logging.ERROR,
            )

        else:
            assert m_db_get_ecowatt.call_count == 1
            assert m_db_set_ecowatt.call_count == 0

            assert contains_logline(
                caplog,
                "{'error': True, 'description': 'Erreur " "lors de la récupération des données Ecowatt.'}",
                logging.ERROR,
            )
