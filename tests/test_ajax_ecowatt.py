import ast
import logging
from datetime import datetime
from json import JSONDecodeError
from dateutil.relativedelta import relativedelta
import pytest

from db_schema import Ecowatt
from conftest import contains_logline


@pytest.mark.parametrize(
    "response, status_code, expect_exception, expect_success",
    [
        (None, 200, False, False),
        (None, 500, True, False),
        ({"2099-01-01": {"value": 9000, "message": "mock message", "detail": "mock detail"}}, 200, False, True),
    ],
)
def test_fetch_ecowatt_empty(mocker, caplog, requests_mock, response, status_code, expect_exception, expect_success):
    from models.ajax import Ajax
    from const import URL

    start = (datetime.now() - relativedelta(years=3)).strftime("%Y-%m-%d")
    end = (datetime.now() + relativedelta(days=3)).strftime("%Y-%m-%d")

    m_db_get_ecowatt = mocker.patch("database.ecowatt.DatabaseEcowatt.get")
    m_db_set_ecowatt = mocker.patch("database.ecowatt.DatabaseEcowatt.set")

    m_db_get_ecowatt.return_value = []
    requests_mock.get(f"{URL}/rte/ecowatt/{start}/{end}", json=response, status_code=status_code)

    ajax = Ajax()

    # FIXME: In case the status_code is not 200 and the response is not a valid json, an exception is raised
    if expect_exception:
        with pytest.raises(JSONDecodeError):
            ajax.fetch_ecowatt()
    else:
        res = ajax.fetch_ecowatt()
        if expect_success:
            assert res == response

            assert m_db_get_ecowatt.call_count == 1
            assert m_db_set_ecowatt.call_count == 1

            assert not contains_logline(
                caplog,
                "{'error': True, 'description': 'Erreur " "lors de la récupération des données Ecowatt.'}",
                logging.ERROR,
            )
        else:
            assert res == "OK"

            assert m_db_get_ecowatt.call_count == 1
            assert m_db_set_ecowatt.call_count == 0

            assert contains_logline(
                caplog,
                "{'error': True, 'description': 'Erreur " "lors de la récupération des données Ecowatt.'}",
                logging.ERROR,
            )


@pytest.mark.parametrize(
    "response, expect_exception, expect_success",
    [
        (None, True, False),
        (
            [Ecowatt(date="2099-01-01", value=9000, message="mock message", detail="{'detail': 'mock detail'}")],
            False,
            True,
        ),
    ],
)
def test_get_ecowatt(mocker, caplog, response, expect_exception, expect_success):
    from models.ajax import Ajax

    m_db_get_ecowatt = mocker.patch("database.ecowatt.DatabaseEcowatt.get")
    m_db_get_ecowatt.return_value = response
    m_db_set_ecowatt = mocker.patch("database.ecowatt.DatabaseEcowatt.set")

    ajax = Ajax()

    # FIXME: In case the status_code is not 200 and the response is not a valid json, an exception is raised
    if expect_exception:
        with pytest.raises(TypeError):
            ajax.get_ecowatt()
    else:
        res = ajax.get_ecowatt()
        assert res == {
            r.date: {"value": r.value, "message": r.message, "detail": ast.literal_eval(r.detail)} for r in response
        }

        assert m_db_get_ecowatt.call_count == 1
        assert m_db_set_ecowatt.call_count == 0

        assert not contains_logline(
            caplog,
            "{'error': True, 'description': 'Erreur " "lors de la récupération des données Ecowatt.'}",
            logging.ERROR,
        )
