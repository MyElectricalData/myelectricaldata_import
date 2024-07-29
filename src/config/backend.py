"""Backend configuration."""
import inspect

from utils import edit_config


class Backend:
    """Backend configuration."""

    def __init__(self, config: dict, write: bool = True) -> None:
        self.config = config
        self.write = write
        # LOCAL PROPERTIES
        self._uri: str = None
        # PROPERTIES
        self.key = "backend"
        self.json: dict = {}
        self.comments = {
            "backend": "SQLite (sqlite:///data/myelectricaldata.db) ou PostgreSQL (postgresql://USER:PASSWORD@HOSTNAME:PORT/DBNAME)"
        }
        # FUNCTION
        self.load()

    def default(self) -> dict:
        """Return default configuration as dictionary."""
        return {"uri": "sqlite:////data/myelectricaldata.db"}

    def load(self):
        """Load configuration from file."""
        try:
            sub_key = "uri"
            self.change(sub_key, self.config[self.key][sub_key], False)
        except Exception:
            self.change(sub_key, self.default()[sub_key], False)

        # Save configuration
        if self.write:
            edit_config(data={self.key: self.json}, comments=self.comments)

    def change(self, key: str, value: str, write_file: bool = True) -> None:
        """Change configuration."""
        setattr(self, f"_{key}", value)
        self.json[key] = value
        if write_file:
            edit_config({self.key: {key: value}})

    @property
    def uri(self) -> str:
        """CIDR Listen address."""
        return self._uri

    @uri.setter
    def uri(self, value):
        self.change(inspect.currentframe().f_code.co_name, value)
