"""MQTT configuration."""
import inspect

from database.config import DatabaseConfig
from utils import edit_config, str2bool


class MQTT:
    """MQTT Option."""

    def __init__(self, config: dict, write: bool = True) -> None:
        self.config = config
        self.write = write
        self.db = DatabaseConfig()
        # LOCAL PROPERTIES
        self._enable: bool = None
        self._hostname: str = None
        self._port: int = None
        self._username: str = None
        self._password: str = None
        self._prefix: str = None
        self._client_id: str = None
        self._retain: bool = None
        self._qos: int = None
        self._cert: str = None
        # PROPERTIES
        self.key = "mqtt"
        self.json: dict = {}
        self.comments = {"mqtt": "Configuration du serveur MQTT (nécéssaire pour Home Assistant)."}
        # FUNCTION
        self.load()

    def default(self) -> dict:
        """Return default configuration as dictionary."""
        return {
            "enable": False,
            "hostname": "localhost",
            "port": 1883,
            "username": "",
            "password": "",
            "prefix": "myelectricaldata",
            "client_id": "myelectricaldata",
            "retain": True,
            "qos": 0,
            "cert": False,
        }

    def load(self):  # noqa: C901, PLR0912, PLR0915
        """Load configuration from file."""
        try:
            sub_key = "enable"
            self.change(sub_key, str2bool(self.config[self.key][sub_key]), False)
        except Exception:
            self.change(sub_key, self.default()[sub_key], False)
        try:
            sub_key = "hostname"
            self.change(sub_key, self.config[self.key][sub_key], False)
        except Exception:
            self.change(sub_key, self.default()[sub_key], False)
        try:
            sub_key = "port"
            self.change(sub_key, int(self.config[self.key][sub_key], False))
        except Exception:
            self.change(sub_key, self.default()[sub_key], False)
        try:
            sub_key = "username"
            self.change(sub_key, self.config[self.key][sub_key], False)
        except Exception:
            self.change(sub_key, self.default()[sub_key], False)
        try:
            sub_key = "password"
            self.change(sub_key, self.config[self.key][sub_key], False)
        except Exception:
            self.change(sub_key, self.default()[sub_key], False)
        try:
            sub_key = "prefix"
            self.change(sub_key, self.config[self.key][sub_key], False)
        except Exception:
            self.change(sub_key, self.default()[sub_key], False)
        try:
            sub_key = "client_id"
            self.change(sub_key, self.config[self.key][sub_key], False)
        except Exception:
            self.change(sub_key, self.default()[sub_key], False)
        try:
            sub_key = "retain"
            self.change(sub_key, str2bool(self.config[self.key][sub_key]), False)
        except Exception:
            self.change(sub_key, self.default()[sub_key], False)
        try:
            sub_key = "qos"
            self.change(sub_key, int(self.config[self.key][sub_key], False))
        except Exception:
            self.change(sub_key, self.default()[sub_key], False)
        try:
            sub_key = "cert"
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
    def enable(self) -> bool:
        """Enable/Disable MQTT."""
        return self._enable

    @enable.setter
    def enable(self, value):
        self.change(inspect.currentframe().f_code.co_name, value)

    @property
    def hostname(self) -> str:
        """MQTT hostname."""
        return self._hostname

    @hostname.setter
    def hostname(self, value):
        self.change(inspect.currentframe().f_code.co_name, value)

    @property
    def port(self) -> int:
        """MQTT port."""
        return self._port

    @port.setter
    def port(self, value):
        self.change(inspect.currentframe().f_code.co_name, value)

    @property
    def username(self) -> str:
        """MQTT username."""
        return self._username

    @username.setter
    def username(self, value):
        self.change(inspect.currentframe().f_code.co_name, value)

    @property
    def password(self) -> str:
        """MQTT password."""
        return self._password

    @password.setter
    def password(self, value):
        self.change(inspect.currentframe().f_code.co_name, value)

    @property
    def prefix(self) -> str:
        """MQTT prefix."""
        return self._prefix

    @prefix.setter
    def prefix(self, value):
        self.change(inspect.currentframe().f_code.co_name, value)

    @property
    def client_id(self) -> str:
        """MQTT client_id."""
        return self._client_id

    @client_id.setter
    def client_id(self, value):
        self.change(inspect.currentframe().f_code.co_name, value)

    @property
    def retain(self) -> bool:
        """MQTT retain."""
        return self._retain

    @retain.setter
    def retain(self, value):
        self.change(inspect.currentframe().f_code.co_name, value)

    @property
    def qos(self) -> int:
        """MQTT qos."""
        return self._qos

    @qos.setter
    def qos(self, value):
        self.change(inspect.currentframe().f_code.co_name, value)

    @property
    def cert(self) -> str:
        """MQTT cert."""
        return self._cert

    @cert.setter
    def cert(self, value):
        self.change(inspect.currentframe().f_code.co_name, value)
