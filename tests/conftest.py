import logging
import os
import tempfile
from contextlib import contextmanager

import pytest
import yaml


@contextmanager
def setenv(**envvars):
    old_env = os.environ.copy()
    try:
        for envvar, value in envvars.items():
            os.environ[envvar] = value
        yield
    finally:
        os.environ = old_env


@contextmanager
def mock_config(data_dir):
    filename = "config.yaml"
    config = {
        "home_assistant": {"enable": "False"},
        "myelectricaldata": {
            "pdl1": {
                "enable": True,
                "consumption": True,
                "consumption_detail": True,
                "production": True,
                "production_detail": True,
                "token": "abcd",
            },
            "pdl2": {"enable": False},
            "pdl3": {"enable": False},
        },
    }

    with open(os.path.join(data_dir, filename), "w") as fp:
        yaml.dump(config, fp)
    print(f"created {fp.name} for testing")
    yield


@contextmanager
def mock_datadir():
    with tempfile.TemporaryDirectory() as data_dir:
        yield data_dir


# TODO: Extract as a function in main.py to avoid duplication
def copied_from_main():
    from init import CONFIG, DB

    usage_point_list = []
    if CONFIG.list_usage_point() is not None:
        for upi, upi_data in CONFIG.list_usage_point().items():
            logging.info(f"{upi}")
            DB.set_usage_point(upi, upi_data)
            usage_point_list.append(upi)
            logging.info("  => Success")
    else:
        logging.warning("Aucun point de livraison détecté.")

    DB.clean_database(usage_point_list)


@pytest.fixture(scope="session", autouse=True)
def update_paths():
    project_root = os.path.abspath(os.path.join(os.path.realpath(__file__), "..", ".."))
    app_path = os.path.join(project_root, "src")
    with mock_datadir() as data_dir:
        with setenv(APPLICATION_PATH=app_path, APPLICATION_PATH_DATA=data_dir), mock_config(data_dir):
            copied_from_main()
            yield


def contains_logline(caplog, expected_log: str, expected_level: int = None):
    for logger_name, level, message in caplog.record_tuples:
        is_log_match = expected_log == message
        is_level_match = expected_level == level if expected_level else True
        if is_log_match and is_level_match:
            return True
    try:
        # Use assertion to generate debugging message
        assert expected_log in caplog.text
    except Exception:
        return False
