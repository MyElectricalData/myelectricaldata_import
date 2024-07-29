"""Gateway configuration."""
import inspect

from utils import edit_config, str2bool


class Gateway:
    """Gateway configuration."""

    def __init__(self, config: dict, write: bool = True) -> None:
        self.config: dict = config
        self.write = write
        # LOCAL PROPERTIES
        self._url: str = None
        self._ssl: bool = None
        # PROPERTIES
        self.key: str = "gateway"
        self.json: dict = {}
        self.comments = {"gateway": "MyElectricalData configuration."}
        # FUNCTION
        self.load()

    def default(self) -> dict:
        """Return default configuration as dictionary."""
        return {"url": "myelectricaldata.fr", "ssl": True}

    def load(self):
        """Load configuration from file."""
        try:
            sub_key = "url"
            self.change(sub_key, self.config[self.key][sub_key], False)
        except Exception:
            self.change(sub_key, self.default()[sub_key], False)
        try:
            sub_key = "ssl"
            self.change(sub_key, str2bool(self.config[self.key][sub_key]), False)
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
    def url(self) -> str:
        """Gateway URL."""
        return self._url

    @url.setter
    def url(self, value):
        self.change(inspect.currentframe().f_code.co_name, value)

    @property
    def ssl(self) -> bool:
        """Enable HTTPS to all gateway call."""
        return self._ssl

    @ssl.setter
    def ssl(self, value):
        self.change(inspect.currentframe().f_code.co_name, value)
