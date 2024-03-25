import logging

import pytest
from test_jobs import job
from tests.conftest import contains_logline


@pytest.mark.parametrize("response, status_code", [(None, 200), (None, 500), ({"mock": "response"}, 200)])
def test_get_gateway_status(job, caplog, requests_mock, response, status_code):
    from config import URL

    requests_mock.get(f"{URL}/ping", json=response, status_code=status_code)

    job.get_gateway_status()

    assert contains_logline(caplog, "RÉCUPÉRATION DU STATUT DE LA PASSERELLE :", logging.INFO)

    # FIXME: No error is displayed
    # if status_code != 200:
    #     assert contains_logline(caplog, "Erreur lors de la récupération du statut de la passerelle :", logging.ERROR)

    if status_code == 200:
        if response:
            assert not contains_logline(caplog, "Erreur lors de la récupération du statut de la passerelle :", logging.ERROR)
        else:
            assert contains_logline(caplog, "Erreur lors de la récupération du statut de la passerelle :", logging.ERROR)
