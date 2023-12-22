import os
from contextlib import contextmanager
from unittest import TestCase
from unittest import mock

import pytest as pytest

from db_schema import UsagePoints


@contextmanager
def setenv(**envvars):
    old_env = os.environ.copy()
    try:
        for envvar, value in envvars.items():
            os.environ[envvar] = value
        yield
    finally:
        os.environ = old_env


@pytest.fixture(scope="session", autouse=True)
def update_paths():
    project_root = os.path.abspath(os.path.join(os.path.realpath(__file__), "..", ".."))
    app_path = os.path.join(project_root, "app")
    data_path = os.path.join(project_root, "tests", "data")
    config_path = os.path.join(project_root, "config.exemple.yaml")

    with setenv(APPLICATION_PATH=app_path, APPLICATION_PATH_DATA=data_path, CONFIG_PATH=config_path), \
            mock.patch('models.config.Config.influxdb_config') as influxdb_config, \
            mock.patch('models.config.Config.mqtt_config') as mqtt_config:
        # Disable influxdb until we can mock it properly
        influxdb_config.return_value = {"enable": False}
        # Disable mqtt until we can mock it properly
        mqtt_config.return_value = {"enable": False}
        yield


class TestJob(TestCase):
    def setUp(self) -> None:
        from models.jobs import Job
        self.job = Job()
        self.job.wait_job_start = 0

    @mock.patch('models.jobs.Job.job_import_data')
    def test_boot(self, m: mock.Mock):
        with setenv(DEV="true", DEBUG="true"):
            res = self.job.boot()
            self.assertFalse(res), "called with DEV or DEBUG should return False"
            self.assertEqual(0, m.call_count), "job_import_data should not be called"

        m.return_value = {"status": "Mocked"}
        res = self.job.boot()
        self.assertEqual(m.return_value["status"], res)
        m.assert_called_once()

    @mock.patch('models.jobs.Job.export_influxdb')
    @mock.patch('models.jobs.Job.export_home_assistant_ws')
    @mock.patch('models.jobs.Job.export_home_assistant')
    @mock.patch('models.jobs.Job.export_mqtt')
    @mock.patch('models.jobs.Job.stat_price')
    @mock.patch('models.jobs.Job.get_consumption_max_power')
    @mock.patch('models.jobs.Job.get_production_detail')
    @mock.patch('models.jobs.Job.get_production')
    @mock.patch('models.jobs.Job.get_consumption_detail')
    @mock.patch('models.jobs.Job.get_consumption')
    @mock.patch('models.jobs.Job.get_addresses')
    @mock.patch('models.jobs.Job.get_contract')
    @mock.patch('models.jobs.Job.get_account_status')
    @mock.patch('models.jobs.Job.get_ecowatt')
    @mock.patch('models.jobs.Job.get_tempo')
    @mock.patch('models.jobs.Job.get_gateway_status')
    def test_job_import_data(self, *args: mock.Mock):
        res = self.job.job_import_data(target=None)
        self.assertTrue(res["status"])
        for m in args:
            if m._mock_name in ["get_gateway_status", "get_tempo", "get_ecowatt"]:
                m.assert_called_once()
            else:
                self.assertEqual(len(self.job.usage_points), m.call_count)

    def test_header_generate(self):
        from dependencies import get_version

        # self.header_generate() assumes self.usage_point_config is overwritten
        for self.job.usage_point_config in [UsagePoints()]:
            self.assertDictEqual(
                {'Authorization': None, 'Content-Type': 'application/json', 'call-service': 'myelectricaldata',
                 'version': get_version()},
                self.job.header_generate())

    @mock.patch('models.jobs.Job.header_generate')
    def test_get_gateway_status(self, _):
        res = self.job.get_gateway_status()
        self.assertTrue(res["status"])
