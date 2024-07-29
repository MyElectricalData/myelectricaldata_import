"""Server configuration."""
import inspect

from database.config import DatabaseConfig
from utils import edit_config, str2bool


class HomeAssistantWs:
    """Home Assistant Websocket configuration."""

    def __init__(self, config: dict, write: bool = True) -> None:
        self.config: dict = config
        self.write = write
        self.db = DatabaseConfig()
        # LOCAL PROPERTIES
        self._enable: bool = None
        self._ssl: bool = None
        self._token: str = None
        self._url: str = None
        self._purge: bool = None
        self._batch_size: int = None
        self._max_date: str = None
        # PROPERTIES
        self.key: str = "home_assistant_ws"
        self.json: dict = {}
        self.comments = {
            "home_assistant_ws": "Home Assistant Websocket configuration pour l'importation des données dans "
            'l\'onglet "Energy".'
        }
        # FUNCTION
        self.load()

    def default(self) -> dict:
        """Return default configuration as dictionary."""
        return {
            "enable": False,
            "ssl": False,
            "token": "",
            "url": "ws://localhost:8123",
            "purge": False,
            "batch_size": 1000,
            "max_date": None,
        }

    def load(self):  # noqa: PLR0912
        """Load configuration from file."""
        try:
            sub_key = "enable"
            self.change(sub_key, str2bool(self.config[self.key][sub_key]), False)
        except Exception:
            self.change(sub_key, self.default()[sub_key], False)
        try:
            sub_key = "ssl"
            self.change(sub_key, str2bool(self.config[self.key][sub_key]), False)
        except Exception:
            self.change(sub_key, self.default()[sub_key], False)
        try:
            sub_key = "token"
            self.change(sub_key, self.config[self.key][sub_key], False)
        except Exception:
            self.change(sub_key, self.default()[sub_key], False)
        try:
            sub_key = "url"
            self.change(sub_key, self.config[self.key][sub_key], False)
        except Exception:
            self.change(sub_key, self.default()[sub_key], False)
        try:
            sub_key = "purge"
            self.change(sub_key, str2bool(self.config[self.key][sub_key]), False)
        except Exception:
            self.change(sub_key, self.default()[sub_key], False)
        try:
            sub_key = "batch_size"
            self.change(sub_key, int(self.config[self.key][sub_key], False))
        except Exception:
            self.change(sub_key, self.default()[sub_key], False)
        try:
            sub_key = "max_date"
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
    def ssl(self) -> bool:
        """Enable SSL (https)."""
        return self._ssl

    @ssl.setter
    def ssl(self, value):
        self.change(inspect.currentframe().f_code.co_name, value)

    @property
    def token(self) -> str:
        """Home Assistant long life Token (profile)."""
        return self._token

    @token.setter
    def token(self, value):
        self.change(inspect.currentframe().f_code.co_name, value)

    @property
    def url(self) -> str:
        """Home assistant Url."""
        return self._url

    @url.setter
    def url(self, value):
        self.change(inspect.currentframe().f_code.co_name, value)

    @property
    def purge(self) -> bool:
        """Home assistant Purge data."""
        return self._purge

    @purge.setter
    def purge(self, value):
        self.change(inspect.currentframe().f_code.co_name, value)

    @property
    def batch_size(self) -> int:
        """Home assistant WS batch_size."""
        return self._batch_size

    @batch_size.setter
    def batch_size(self, value):
        self.change(inspect.currentframe().f_code.co_name, value)

    @property
    def max_date(self) -> str:
        """Home assistant WS Max date import."""
        return self._max_date

    @max_date.setter
    def max_date(self, value):
        self.change(inspect.currentframe().f_code.co_name, value)
