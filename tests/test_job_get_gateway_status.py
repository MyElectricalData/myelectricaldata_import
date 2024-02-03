import pytest
from test_jobs import job


@pytest.mark.parametrize("response, status_code", [(None, 200), (None, 500), ({"mock": "response"}, 200)])
def test_get_gateway_status(job, caplog, requests_mock, response, status_code):
    from config import URL

    requests_mock.get(f"{URL}/ping", json=response, status_code=status_code)

    job.get_gateway_status()

    assert "INFO     root:dependencies.py:88 RÉCUPÉRATION DU STATUT DE LA PASSERELLE :\n" in caplog.text
    if status_code != 200:
        # FIXME: No error is displayed
        assert (
            "ERROR    root:jobs.py:170 Erreur lors de la récupération du statut de la passerelle :\n"
            not in caplog.text
        )

    if status_code == 200:
        if response:
            assert (
                "ERROR    root:jobs.py:170 Erreur lors de la récupération du statut de la passerelle :\n"
                not in caplog.text
            )
        else:
            assert (
                "ERROR    root:jobs.py:170 Erreur lors de la récupération du statut de la passerelle :\n"
                in caplog.text
            )
