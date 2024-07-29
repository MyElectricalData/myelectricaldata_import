"""OpenTelemetry configuration."""
import inspect

from database.config import DatabaseConfig
from utils import edit_config, str2bool


class OpTel:
    """OpenTelemetry configuration."""

    def __init__(self, config: dict, write: bool = True) -> None:
        self.config = config
        self.write = write
        self.db = DatabaseConfig()
        # LOCAL PROPERTIES
        self._enable: bool = None
        self._service_name: str = None
        self._endpoint: str = None
        self._environment: str = None
        self._extension: list = []
        # PROPERTIES
        self.key = "opentelemetry"
        self.json: dict = {}
        self.comments = {"opentelemetry": "Pour les utilisateurs avancées."}
        # FUNCTION
        self.load()

    def default(self) -> dict:
        """Return default configuration as dictionary."""
        return {
            "enable": False,
            "service_name": "myelectricaldata",
            "endpoint": "http://localhost:4317",
            "environment": "production",
            "extension": ["fastapi", "sqlalchemy"],
        }

    def load(self):
        """Load configuration from file."""
        try:
            sub_key = "enable"
            self.change(sub_key, str2bool(self.config[self.key][sub_key]), False)
        except Exception:
            self.change(sub_key, self.default()[sub_key], False)
        try:
            sub_key = "service_name"
            self.change(sub_key, self.config[self.key][sub_key], False)
        except Exception:
            self.change(sub_key, self.default()[sub_key], False)
        try:
            sub_key = "endpoint"
            self.change(sub_key, self.config[self.key][sub_key], False)
        except Exception:
            self.change(sub_key, self.default()[sub_key], False)
        try:
            sub_key = "environment"
            self.change(sub_key, self.config[self.key][sub_key], False)
        except Exception:
            self.change(sub_key, self.default()[sub_key], False)
        try:
            sub_key = "extension"
            self.change(sub_key, self.config[self.key][sub_key], False)
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
    def enable(self) -> bool:
        """Enable/Disable service."""
        return self._enable

    @enable.setter
    def enable(self, value):
        self.change(inspect.currentframe().f_code.co_name, value)

    @property
    def service_name(self) -> str:
        """Service name."""
        return self._service_name

    @service_name.setter
    def service_name(self, value):
        self.change(inspect.currentframe().f_code.co_name, value)

    @property
    def endpoint(self) -> str:
        """Endpoint."""
        return self._endpoint

    @endpoint.setter
    def endpoint(self, value):
        self.change(inspect.currentframe().f_code.co_name, value)

    @property
    def environment(self) -> str:
        """Environment."""
        return self._environment

    @environment.setter
    def environment(self, value):
        self.change(inspect.currentframe().f_code.co_name, value)

    @property
    def extension(self) -> list:
        """Extension (fastapi, sqlalchemy)."""
        return self._extension

    @extension.setter
    def extension(self, value):
        self.change(inspect.currentframe().f_code.co_name, value)
