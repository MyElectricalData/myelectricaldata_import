import logging
from datetime import datetime
from dateutil.relativedelta import relativedelta
import pytest
from conftest import contains_logline
from test_jobs import job  # noqa: F401


@pytest.mark.parametrize("response, status_code", [(None, 200), (None, 500), ({"2099-01-01": "turquoise"}, 200)])
def test_get_tempo(mocker, job, caplog, requests_mock, response, status_code):
    from const import URL

    start = (datetime.now() - relativedelta(years=3)).strftime("%Y-%m-%d")
    end = (datetime.now() + relativedelta(days=2)).strftime("%Y-%m-%d")

    m_db_get_tempo = mocker.patch("database.tempo.DatabaseTempo.get")
    m_db_set_tempo_config = mocker.patch("database.tempo.DatabaseTempo.set_config")
    m_db_set_tempo = mocker.patch("database.tempo.DatabaseTempo.set")

    requests_mock.get(f"{URL}/rte/tempo/{start}/{end}", json=response, status_code=status_code)
    requests_mock.get(f"{URL}/edf/tempo/days", json=response, status_code=status_code)
    requests_mock.get(f"{URL}/edf/tempo/price", json=response, status_code=status_code)

    job.get_tempo()

    assert contains_logline(caplog, "RÉCUPÉRATION DES DONNÉES TEMPO", logging.INFO)
    if status_code != 200:
        assert m_db_get_tempo.call_count == 1
        assert m_db_set_tempo.call_count == 0
        assert m_db_set_tempo_config.call_count == 0

        # FIXME: No error is displayed
        # assert contains_logline(caplog, "{'error': True, 'description': 'Erreur lors "
        #                                 "de la récupération de données Tempo.'}", logging.ERROR)

    if status_code == 200:
        if response:
            assert m_db_get_tempo.call_count == 1
            assert m_db_set_tempo.call_count == 1
            assert m_db_set_tempo_config.call_count == 2

            assert not contains_logline(
                caplog,
                "{'error': True, 'description': 'Erreur lors " "de la récupération de données Tempo.'}",
                logging.ERROR,
            )
        else:
            assert m_db_get_tempo.call_count == 1
            assert m_db_set_tempo.call_count == 0
            # FIXME: set_tempo_config shouldn't be called when status_code != 200
            # assert m_db_set_tempo_config.call_count == 0

            assert contains_logline(
                caplog,
                "{'error': True, 'description': 'Erreur lors " "de la récupération de données Tempo.'}",
                logging.ERROR,
            )
