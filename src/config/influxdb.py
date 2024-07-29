"""InfluxDB configuration."""
import inspect
import sys

from database.config import DatabaseConfig
from utils import edit_config, str2bool


class BatchOptions:
    """InfluxDB Batch Option."""

    def __init__(self, config: dict, write: bool = True) -> None:
        self.config: dict = config
        self.write = write
        # LOCAL PROPERTIES
        self._batch_size: int = None
        self._flush_interval: int = None
        self._jitter_interval: int = None
        self._retry_interval: int = None
        self._max_retry_time: str = None
        self._max_retries: int = None
        self._max_retry_delay: str = None
        self._exponential_base: int = None
        # PROPERTIES
        self.key: str = "influxdb"
        self.sub_key: str = "batching_options"
        self.json: dict = {}
        self.comments = {
            "influxdb": (
                "Permet d'exporter vos données vers un serveur InfluxDB et d'exploiter vos "
                "données avec Grafana (ou autre)."
            )
        }
        # FUNCTION
        self.load()

    def default(self) -> dict:
        """Return default configuration as dictionary."""
        return {
            "batch_size": 1000,
            "flush_interval": 1000,
            "jitter_interval": 0,
            "retry_interval": 5000,
            "max_retry_time": "180_000",
            "max_retries": 5,
            "max_retry_delay": "125_000",
            "exponential_base": 2,
        }

    def load(self):  # noqa: PLR0912
        """Load configuration from file."""
        try:
            sub_key = "batch_size"
            self.change(sub_key, int(self.config[self.key][self.sub_key][sub_key], False))
        except Exception:
            self.change(sub_key, self.default()[sub_key], False)
        try:
            sub_key = "flush_interval"
            self.change(sub_key, int(self.config[self.key][self.sub_key][sub_key], False))
        except Exception:
            self.change(sub_key, self.default()[sub_key], False)
        try:
            sub_key = "jitter_interval"
            self.change(sub_key, int(self.config[self.key][self.sub_key][sub_key], False))
        except Exception:
            self.change(sub_key, self.default()[sub_key], False)
        try:
            sub_key = "retry_interval"
            self.change(sub_key, int(self.config[self.key][self.sub_key][sub_key], False))
        except Exception:
            self.change(sub_key, self.default()[sub_key], False)
        try:
            sub_key = "max_retry_time"
            self.change(sub_key, self.config[self.key][self.sub_key][sub_key], False)
        except Exception:
            self.change(sub_key, self.default()[sub_key], False)
        try:
            sub_key = "max_retries"
            self.change(sub_key, int(self.config[self.key][self.sub_key][sub_key], False))
        except Exception:
            self.change(sub_key, self.default()[sub_key], False)
        try:
            sub_key = "max_retry_delay"
            self.change(sub_key, self.config[self.key][self.sub_key][sub_key], False)
        except Exception:
            self.change(sub_key, self.default()[sub_key], False)
        try:
            sub_key = "exponential_base"
            self.change(sub_key, int(self.config[self.key][self.sub_key][sub_key], False))
        except Exception:
            self.change(sub_key, self.default()[sub_key], False)

        # Save configuration
        if self.write:
            edit_config(data={self.key: {self.sub_key: self.json}}, comments=self.comments)

    def change(self, key: str, value: str, write_file: bool = True) -> None:
        """Change configuration."""
        setattr(self, f"_{key}", value)
        self.json[key] = value
        if write_file:
            edit_config({self.key: {self.sub_key: {key: value}}})

    @property
    def batch_size(self) -> int:
        """Batch size."""
        return self._batch_size

    @batch_size.setter
    def batch_size(self, value):
        self.change(inspect.currentframe().f_code.co_name, value)

    @property
    def flush_interval(self) -> int:
        """Flush interval."""
        return self._flush_interval

    @flush_interval.setter
    def flush_interval(self, value):
        self.change(inspect.currentframe().f_code.co_name, value)

    @property
    def jitter_interval(self) -> int:
        """Jitter interval."""
        return self._jitter_interval

    @jitter_interval.setter
    def jitter_interval(self, value):
        self.change(inspect.currentframe().f_code.co_name, value)

    @property
    def retry_interval(self) -> int:
        """Retry interval."""
        return self._retry_interval

    @retry_interval.setter
    def retry_interval(self, value):
        self.change(inspect.currentframe().f_code.co_name, value)

    @property
    def max_retry_time(self) -> str:
        """Max retry time."""
        return self._max_retry_time

    @max_retry_time.setter
    def max_retry_time(self, value):
        self.change(inspect.currentframe().f_code.co_name, value)

    @property
    def max_retries(self) -> int:
        """Max retries."""
        return self._max_retries

    @max_retries.setter
    def max_retries(self, value):
        self.change(inspect.currentframe().f_code.co_name, value)

    @property
    def max_retry_delay(self) -> str:
        """Max retry delay."""
        return self._max_retry_delay

    @max_retry_delay.setter
    def max_retry_delay(self, value):
        self.change(inspect.currentframe().f_code.co_name, value)

    @property
    def exponential_base(self) -> int:
        """Exponential base."""
        return self._exponential_base

    @exponential_base.setter
    def exponential_base(self, value):
        self.change(inspect.currentframe().f_code.co_name, value)


class Method:
    """InfluxDB Method."""

    def __init__(self) -> None:
        self.synchronous: str = "SYNCHRONOUS"
        self.asynchronous: str = "ASYNCHRONOUS"
        self.batching: str = "BATCHING"


class InfluxDB:
    """InfluxDB configuration."""

    def __init__(self, config: dict, write: bool = True) -> None:
        self.config: dict = config
        self.write: dict = write
        self.db = DatabaseConfig()
        # LOCAL PROPERTIES
        self._batching_options: BatchOptions = BatchOptions(self.config, self.write)
        self._enable: bool = self.default()["enable"]
        self._scheme: str = self.default()["scheme"]
        self._hostname: str = self.default()["hostname"]
        self._port: int = self.default()["port"]
        self._token: str = self.default()["token"]
        self._org: str = self.default()["org"]
        self._bucket: str = self.default()["bucket"]
        self._method: Method = self.default()["method"]
        self._timezone: str = self.default()["timezone"]
        self._wipe: str = self.default()["wipe"]
        # PROPERTIES
        self.key: str = "influxdb"
        self.json: dict = {"batching_options": self._batching_options.json}
        # FUNCTION
        self.load()

    def default(self) -> dict:
        """Return default configuration as dictionary."""
        return {
            "enable": False,
            "scheme": "http",
            "hostname": "localhost",
            "port": 8086,
            "token": "my-token",
            "org": "myorg",
            "bucket": "mybucket",
            "method": Method().synchronous,
            "timezone": "UTC",
            "wipe": False,
            "batching_options": self._batching_options.json,
        }

    def load(self):  # noqa: PLR0912, C901, PLR0915
        """Load configuration from file."""
        try:
            sub_key = "enable"
            self.change(sub_key, str2bool(self.config[self.key][sub_key]), False)
        except Exception:
            self.change(sub_key, self.default()[sub_key], False)
        try:
            sub_key = "scheme"
            self.change(sub_key, self.config[self.key][sub_key], False)
        except Exception:
            self.change(sub_key, self.default()[sub_key], False)
        try:
            sub_key = "hostname"
            self.change(sub_key, self.config[self.key][sub_key], False)
        except Exception:
            self.change(sub_key, self.default()[sub_key], False)
        try:
            sub_key = "port"
            self.change(sub_key, int(self.config[self.key][sub_key]), False)
        except Exception:
            self.change(sub_key, self.default()[sub_key], False)
        try:
            sub_key = "token"
            self.change(sub_key, self.config[self.key][sub_key], False)
        except Exception:
            self.change(sub_key, self.default()[sub_key], False)
        try:
            sub_key = "org"
            self.change(sub_key, self.config[self.key][sub_key], False)
        except Exception:
            self.change(sub_key, self.default()[sub_key], False)
        try:
            sub_key = "bucket"
            self.change(sub_key, self.config[self.key][sub_key], False)
        except Exception:
            self.change(sub_key, self.default()[sub_key], False)
        try:
            sub_key = "method"
            current_method = self.config[self.key][sub_key]
            method = Method()
            method_available = ""
            for value in method.__dict__.values():
                method_available += f"{value}, "
            if current_method not in method.__dict__.values():
                sys.exit(
                    f'[InfluxDB] Erreur de configuration, la méthode "{current_method}" '
                    "n'éxiste pas. ({method_available[:-2]})"
                )
            self.change(sub_key, self.config[self.key][sub_key], False)
        except Exception:
            self.change(sub_key, self.default()[sub_key], False)
        try:
            sub_key = "timezone"
            self.change(sub_key, self.config[self.key][sub_key], False)
        except Exception:
            self.change(sub_key, self.default()[sub_key], False)
        try:
            sub_key = "wipe"
            self.change(sub_key, self.config[self.key][sub_key], False)
        except Exception:
            self.change(sub_key, self.default()[sub_key], False)

        # Save configuration
        if self.write:
            edit_config({self.key: self.json})
            self.db.set(self.key, self.json)

    def change(self, key: str, value: str, write_file: bool = True) -> None:
        """Change configuration."""
        setattr(self, f"_{key}", value)
        self.json[key] = value
        if write_file:
            edit_config({self.key: {key: value}})
            current_config = self.db.get(self.key)
            new_config = {**current_config, **{key: value}}
            self.db.set(self.key, new_config)

    @property
    def enable(self) -> bool:
        """InfluxDB enable."""
        return self._enable

    @enable.setter
    def enable(self, value):
        self.change(inspect.currentframe().f_code.co_name, value)

    @property
    def scheme(self) -> str:
        """InfluxDB scheme."""
        return self._scheme

    @scheme.setter
    def scheme(self, value):
        self.change(inspect.currentframe().f_code.co_name, value)

    @property
    def hostname(self) -> str:
        """InfluxDB hostname."""
        return self._hostname

    @hostname.setter
    def hostname(self, value):
        self.change(inspect.currentframe().f_code.co_name, value)

    @property
    def port(self) -> int:
        """InfluxDB port."""
        return self._port

    @port.setter
    def port(self, value):
        self.change(inspect.currentframe().f_code.co_name, value)

    @property
    def token(self) -> str:
        """InfluxDB token."""
        return self._token

    @token.setter
    def token(self, value):
        self.change(inspect.currentframe().f_code.co_name, value)

    @property
    def org(self) -> str:
        """InfluxDB org."""
        return self._org

    @org.setter
    def org(self, value):
        self.change(inspect.currentframe().f_code.co_name, value)

    @property
    def bucket(self) -> str:
        """InfluxDB bucket."""
        return self._bucket

    @bucket.setter
    def bucket(self, value):
        self.change(inspect.currentframe().f_code.co_name, value)

    @property
    def method(self) -> str:
        """InfluxDB method."""
        return self._method

    @method.setter
    def method(self, value):
        self.change(inspect.currentframe().f_code.co_name, value)

    @property
    def timezone(self) -> str:
        """InfluxDB timezone."""
        return self._timezone

    @timezone.setter
    def timezone(self, value):
        self.change(inspect.currentframe().f_code.co_name, value)

    @property
    def wipe(self) -> str:
        """InfluxDB wipe."""
        return self._wipe

    @wipe.setter
    def wipe(self, value):
        self.change(inspect.currentframe().f_code.co_name, value)

    @property
    def batching_options(self) -> str:
        """Batching options."""
        return self._batching_options

    @batching_options.setter
    def batching_options(self, value):
        self.change(inspect.currentframe().f_code.co_name, value)
