import logging
from datetime import datetime
from json import JSONDecodeError
from dateutil.relativedelta import relativedelta
import pytest

from db_schema import Tempo
from tests.conftest import contains_logline


@pytest.mark.parametrize("response, status_code",
                         [(None, 200), (None, 500), ({"mock": "response"}, 200), ({"2099-01-01": "turquoise"}, 200)])
def test_fetch_tempo(mocker, caplog, requests_mock, response, status_code):
    from models.ajax import Ajax
    from config import URL

    start = (datetime.now() - relativedelta(years=3)).strftime("%Y-%m-%d")
    end = (datetime.now() + relativedelta(days=2)).strftime("%Y-%m-%d")

    m_db_get_tempo = mocker.patch("models.database.Database.get_tempo")
    m_db_set_tempo_config = mocker.patch("models.database.Database.set_tempo_config")
    m_db_set_tempo = mocker.patch("models.database.Database.set_tempo")

    requests_mock.get(f"{URL}/rte/tempo/{start}/{end}", json=response, status_code=status_code)
    requests_mock.get(f"{URL}/edf/tempo/days", json=response, status_code=status_code)
    requests_mock.get(f"{URL}/edf/tempo/price", json=response, status_code=status_code)

    ajax = Ajax()

    # FIXME: In case the status_code is not 200 and the response is not a valid json, an exception is raised
    if status_code != 200 and not response:
        with pytest.raises(JSONDecodeError):
            ajax.fetch_tempo()
    else:
        res = ajax.fetch_tempo()
        if status_code == 200 and response and response.get("2099-01-01"):
            assert res == response

            assert m_db_get_tempo.call_count == 1
            assert m_db_set_tempo.call_count == 1
            assert m_db_set_tempo_config.call_count == 0

            assert not contains_logline(caplog, "{'error': True, 'description': 'Erreur lors "
                                                "de la récupération de données Tempo.'}", logging.ERROR)
        else:
            assert res == "OK"

            assert m_db_get_tempo.call_count == 1
            assert m_db_set_tempo.call_count == 0
            assert m_db_set_tempo_config.call_count == 0

            assert contains_logline(caplog, "{'error': True, 'description': 'Erreur lors "
                                            "de la récupération de données Tempo.'}", logging.ERROR)


@pytest.mark.parametrize("response", [None, [Tempo(date="2099-01-01", color="turquoise")]])
def test_get_tempo(mocker, caplog, response):
    from models.ajax import Ajax

    m_db_get_tempo = mocker.patch("models.database.Database.get_tempo")
    m_db_get_tempo.return_value = response
    m_db_set_tempo_config = mocker.patch("models.database.Database.set_tempo_config")
    m_db_set_tempo = mocker.patch("models.database.Database.set_tempo")

    ajax = Ajax()

    # FIXME: In case the status_code is not 200 and the response is not a valid json, an exception is raised
    if not response:
        with pytest.raises(TypeError):
            ajax.get_tempo()
    else:
        res = ajax.get_tempo()
        assert res == {r.date: r.color for r in response}

        assert m_db_get_tempo.call_count == 1
        assert m_db_set_tempo.call_count == 0
        assert m_db_set_tempo_config.call_count == 0

        assert not contains_logline(caplog, "{'error': True, 'description': 'Erreur lors "
                                            "de la récupération de données Tempo.'}", logging.ERROR)
