"""Logging configuration."""
import inspect
import logging

from database.config import DatabaseConfig
from utils import edit_config, str2bool


class Logging:
    """Logging configuration."""

    def __init__(self, config: dict, write: bool = True) -> None:
        self.config = config
        self.write = write
        self.db = DatabaseConfig()
        # LOCAL PROPERTIES
        self._log_format: str = None
        self._log_format_date: str = None
        self._log2file: bool = None
        self._debug: bool = None
        self._log_level: int = None
        self._log_http: bool = None
        # PROPERTIES
        self.key = "logging"
        self.json: dict = {}
        self.comments = {"logging": 'Permet de "custom" la gestion des logs de l\'application.'}
        # FUNCTION
        self.load()

    def default(self) -> dict:
        """Return default configuration as dictionary."""
        return {
            "log_format": "%(asctime)s.%(msecs)03d - %(levelname)8s : %(message)s",
            "log_format_date": "%Y-%m-%d %H:%M:%S",
            "log2file": False,
            "log_level": logging.INFO,
            "debug": False,
            "log_http": False,
        }

    def load(self):  # noqa: PLR0912
        """Load configuration from file."""
        try:
            sub_key = "log_format"
            self.change(sub_key, self.config[self.key][sub_key], False)
        except Exception:
            self.change(sub_key, self.default()[sub_key], False)
        try:
            sub_key = "log_format_date"
            self.change(sub_key, self.config[self.key][sub_key], False)
        except Exception:
            self.change(sub_key, self.default()[sub_key], False)
        try:
            sub_key = "log2file"
            if "log2file" in self.config:
                self.change(sub_key, str2bool(self.config["log2file"]), False)
                del self.config["log2file"]
            else:
                self.change(sub_key, str2bool(self.config[self.key][sub_key]), False)
        except Exception:
            self.change(sub_key, self.default()[sub_key], False)
        try:
            sub_key = "debug"
            if "debug" in self.config:
                self.change(sub_key, str2bool(self.config["debug"]), False)
                del self.config["debug"]
            else:
                self.change(sub_key, str2bool(self.config[self.key][sub_key]), False)
        except Exception:
            self.change(sub_key, self.default()[sub_key], False)
        try:
            self._log_level = logging.DEBUG if self._debug else logging.INFO
        except Exception:
            self.log_level = self.default()["log_level"]
        try:
            sub_key = "log_http"
            self.change(sub_key, str2bool(self.config[self.key][sub_key]), False)
        except Exception:
            self.change(sub_key, self.default()[sub_key], False)

        # Save configuration
        if self.write:
            edit_config(data={self.key: self.json}, comments=self.comments)
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
    def log_format(self) -> str:
        """Log format."""
        return self._log_format

    @log_format.setter
    def log_format(self, value):
        self._log_format = value
        self.change(inspect.currentframe().f_code.co_name, value)

    @property
    def log_format_date(self) -> str:
        """Log format date."""
        return self._log_format_date

    @log_format_date.setter
    def log_format_date(self, value):
        self._log_format_date = value
        self.change(inspect.currentframe().f_code.co_name, value)

    @property
    def log2file(self) -> bool:
        """Log to file."""
        return self._log2file

    @log2file.setter
    def log2file(self, value):
        self._log2file = value
        self.change(inspect.currentframe().f_code.co_name, value)

    @property
    def debug(self) -> bool:
        """Debug mode."""
        return self._debug

    @debug.setter
    def debug(self, value):
        self._debug = value
        self.change(inspect.currentframe().f_code.co_name, value)

    @property
    def log_level(self) -> int:
        """Log level."""
        return self._log_level

    @log_level.setter
    def log_level(self, value):
        self._log_level = value
        self.change(inspect.currentframe().f_code.co_name, value)

    @property
    def log_http(self) -> bool:
        """Log HTTP requests."""
        return self._log_http

    @log_http.setter
    def log_http(self, value):
        self._log_http = value
        self.change(inspect.currentframe().f_code.co_name, value)
