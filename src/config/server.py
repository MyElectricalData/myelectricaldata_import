"""Server configuration."""
import inspect

from const import CYCLE_MINIMUN
from database.config import DatabaseConfig
from utils import edit_config


class Server:
    """Server configuration."""

    def __init__(self, config: dict, write: bool = True) -> None:
        self.config = config
        self.write = write
        self.db = DatabaseConfig()
        # LOCAL PROPERTIES
        self._cidr: str = None
        self._port: int = None
        self._certfile: str = None
        self._keyfile: str = None
        self._cycle: int = None
        # PROPERTIES
        self.key = "server"
        self.json: dict = {}
        self.comments = {"server": "Configuration du serveur web."}
        # FUNCTION
        self.load()

    def default(self) -> dict:
        """Return default configuration as dictionary."""
        return {
            "cidr": "0.0.0.0",  # noqa: S104
            "port": 5000,
            "certfile": "",
            "keyfile": "",
            "cycle": 14400,
        }

    def load(self):
        """Load configuration."""
        try:
            sub_key = "cidr"
            self.change(sub_key, self.config[self.key][sub_key], False)
        except Exception:
            self.change(sub_key, self.default()[sub_key], False)
        try:
            sub_key = "port"
            self.change(sub_key, int(self.config[self.key][sub_key]), False)
        except Exception:
            self.change(sub_key, self.default()[sub_key], False)
        try:
            sub_key = "certfile"
            self.change(sub_key, self.config[self.key][sub_key], False)
        except Exception:
            self.change(sub_key, self.default()[sub_key], False)
        try:
            sub_key = "keyfile"
            self.change(sub_key, self.config[self.key][sub_key], False)
        except Exception:
            self.change(sub_key, self.default()[sub_key], False)
        try:
            sub_key = "cycle"
            self.change(sub_key, int(max(self.config[self.key][sub_key], CYCLE_MINIMUN)), False)
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
    def cidr(self):
        """CIDR Listen address."""
        return self._cidr

    @cidr.setter
    def cidr(self, value):
        self.change(inspect.currentframe().f_code.co_name, value)

    @property
    def port(self):
        """Server listen port."""
        return self._port

    @port.setter
    def port(self, value):
        self.change(inspect.currentframe().f_code.co_name, value)

    @property
    def certfile(self):
        """HTTPs custom certificat."""
        return self._certfile

    @certfile.setter
    def certfile(self, value):
        self.change(inspect.currentframe().f_code.co_name, value)

    @property
    def keyfile(self):
        """HTTPs custom keyfile."""
        return self.keyfile

    @keyfile.setter
    def keyfile(self, value):
        self.change(inspect.currentframe().f_code.co_name, value)

    @property
    def cycle(self):
        """Jobs cycle."""
        return self._cycle

    @cycle.setter
    def cycle(self, value):
        self.change(inspect.currentframe().f_code.co_name, value)
