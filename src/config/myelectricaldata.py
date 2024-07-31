"""MyElectricalData configuration."""
import inspect
import sys
from datetime import datetime

from const import TIMEZONE_UTC
from database.usage_points import DatabaseUsagePoints
from utils import edit_config, str2bool


class Plan:
    """Plan templates."""

    def __init__(self) -> None:
        self.base: str = "BASE"
        self.hchp: str = "HC/HP"
        self.tempo: str = "TEMPO"


class UsagePointId:
    """UsagePoint templates."""

    def __init__(self, config: dict, usage_point_id: str, write: bool = True) -> None:
        self.usage_point_id: str = usage_point_id
        self.config: dict = config
        self.write: bool = write
        self.db = DatabaseUsagePoints(self.usage_point_id)
        # LOCAL PROPERTIES
        self._enable: bool = None
        self._name: str = None
        self._token: str = None
        self._cache: bool = None
        self._plan: Plan = None
        self._consumption: bool = None
        self._consumption_detail: bool = None
        self._consumption_max_power: bool = None
        self._consumption_price_hc: float = None
        self._consumption_price_hp: float = None
        self._consumption_price_base: float = None
        self._consumption_max_date: str = None
        self._consumption_detail_max_date: str = None
        self._production: bool = None
        self._production_detail: bool = None
        self._production_max_date: str = None
        self._production_detail_max_date: str = None
        self._production_price: float = None
        self._offpeak_hours_0: str = None
        self._offpeak_hours_1: str = None
        self._offpeak_hours_2: str = None
        self._offpeak_hours_3: str = None
        self._offpeak_hours_4: str = None
        self._offpeak_hours_5: str = None
        self._offpeak_hours_6: str = None
        self._refresh_addresse: bool = None
        self._refresh_contract: bool = None
        # PROPERTIES
        self.key: str = "myelectricaldata"
        self.json: dict = {}
        # FUNCTION
        self.load()

    def default(self) -> dict:
        """Return default configuration as dictionary."""
        return {
            "enable": True,
            "name": self.usage_point_id,
            "token": "VOTRE_TOKEN_MYELECTRICALDATA",
            "cache": True,
            "plan": Plan().base,
            "consumption": True,
            "consumption_detail": True,
            "consumption_max_power": True,
            "consumption_price_hc": 0,
            "consumption_price_hp": 0,
            "consumption_price_base": 0,
            "consumption_max_date": "",
            "consumption_detail_max_date": "",
            "production": False,
            "production_detail": False,
            "production_max_date": "",
            "production_detail_max_date": "",
            "production_price": 0,
            "offpeak_hours_0": "",
            "offpeak_hours_1": "",
            "offpeak_hours_2": "",
            "offpeak_hours_3": "",
            "offpeak_hours_4": "",
            "offpeak_hours_5": "",
            "offpeak_hours_6": "",
            "refresh_addresse": False,
            "refresh_contract": False,
        }

    def load(self):  # noqa: C901, PLR0912, PLR0915
        """Load configuration from file."""
        try:
            sub_key = "enable"
            self.change(sub_key, str2bool(self.config[self.key][self.usage_point_id][sub_key]), False)
        except Exception:
            self.change(sub_key, self.default()[sub_key], False)
        try:
            sub_key = "name"
            self.change(sub_key, self.config[self.key][self.usage_point_id][sub_key], False)
        except Exception:
            self.change(sub_key, self.default()[sub_key], False)
        try:
            sub_key = "token"
            self.change(sub_key, self.config[self.key][self.usage_point_id][sub_key], False)
        except Exception:
            self.change(sub_key, self.default()[sub_key], False)
        try:
            sub_key = "cache"
            self.change(sub_key, str2bool(self.config[self.key][self.usage_point_id][sub_key]), False)
        except Exception:
            self.change(sub_key, self.default()[sub_key], False)
        try:
            sub_key = "plan"
            current_plan = self.config[self.key][self.usage_point_id][sub_key].upper()
            plan = Plan()
            plan_available = ""
            for value in plan.__dict__.values():
                plan_available += f"{value}, "
            if current_plan not in plan.__dict__.values():
                sys.exit(
                    f'[MyElectricalData][{self.usage_point_id}] Erreur de configuration, le plan "{current_plan} '
                    f"n'éxiste pas. ({plan_available[:-2]})"
                )

            self.change(sub_key, self.config[self.key][self.usage_point_id][sub_key].upper(), False)
        except Exception:
            self.change(sub_key, self.default()[sub_key], False)
        try:
            sub_key = "consumption"
            self.change(sub_key, str2bool(self.config[self.key][self.usage_point_id][sub_key]), False)
        except Exception:
            self.change(sub_key, self.default()[sub_key], False)
        try:
            sub_key = "consumption_detail"
            self.change(sub_key, str2bool(self.config[self.key][self.usage_point_id][sub_key]), False)
        except Exception:
            self.change(sub_key, self.default()[sub_key], False)
        try:
            sub_key = "consumption_max_power"
            self.change(sub_key, str2bool(self.config[self.key][self.usage_point_id][sub_key]), False)
        except Exception:
            self.change(sub_key, self.default()[sub_key], False)
        try:
            sub_key = "consumption_price_hc"
            self.change(sub_key, float(self.config[self.key][self.usage_point_id][sub_key]), False)
        except Exception:
            self.change(sub_key, self.default()[sub_key], False)
        try:
            sub_key = "consumption_price_hp"
            self.change(sub_key, float(self.config[self.key][self.usage_point_id][sub_key]), False)
        except Exception:
            self.change(sub_key, self.default()[sub_key], False)
        try:
            sub_key = "consumption_price_base"
            self.change(sub_key, float(self.config[self.key][self.usage_point_id][sub_key]), False)
        except Exception:
            self.change(sub_key, self.default()[sub_key], False)
        try:
            self.sub_key = "consumption_max_date"
            self.change(sub_key, self.config[self.key][self.usage_point_id][sub_key], False)
        except Exception:
            self.change(sub_key, self.default()[sub_key], False)
        try:
            sub_key = "consumption_detail_max_date"
            self.change(sub_key, self.config[self.key][self.usage_point_id][sub_key], False)
        except Exception:
            self.change(sub_key, self.default()[sub_key], False)
        try:
            sub_key = "production"
            self.change(sub_key, str2bool(self.config[self.key][self.usage_point_id][sub_key]), False)
        except Exception:
            self.change(sub_key, self.default()[sub_key], False)
        try:
            sub_key = "production_detail"
            self.change(sub_key, str2bool(self.config[self.key][self.usage_point_id][sub_key]), False)
        except Exception:
            self.change(sub_key, self.default()[sub_key], False)
        try:
            sub_key = "production_max_date"
            self.change(sub_key, self.config[self.key][self.usage_point_id][sub_key], False)
        except Exception:
            self.change(sub_key, self.default()[sub_key], False)
        try:
            sub_key = "production_detail_max_date"
            self.change(sub_key, self.config[self.key][self.usage_point_id][sub_key], False)
        except Exception:
            self.change(sub_key, self.default()[sub_key], False)
        try:
            sub_key = "production_price"
            self.change(sub_key, float(self.config[self.key][self.usage_point_id][sub_key]), False)
        except Exception:
            self.change(sub_key, self.default()[sub_key], False)
        try:
            sub_key = "offpeak_hours_0"
            self.change(sub_key, self.config[self.key][self.usage_point_id][sub_key], False)
        except Exception:
            self.change(sub_key, self.default()[sub_key], False)
        try:
            sub_key = "offpeak_hours_1"
            self.change(sub_key, self.config[self.key][self.usage_point_id][sub_key], False)
        except Exception:
            self.change(sub_key, self.default()[sub_key], False)
        try:
            sub_key = "offpeak_hours_2"
            self.change(sub_key, self.config[self.key][self.usage_point_id][sub_key], False)
        except Exception:
            self.change(sub_key, self.default()[sub_key], False)
        try:
            sub_key = "offpeak_hours_3"
            self.change(sub_key, self.config[self.key][self.usage_point_id][sub_key], False)
        except Exception:
            self.change(sub_key, self.default()[sub_key], False)
        try:
            sub_key = "offpeak_hours_4"
            self.change(sub_key, self.config[self.key][self.usage_point_id][sub_key], False)
        except Exception:
            self.change(sub_key, self.default()[sub_key], False)
        try:
            sub_key = "offpeak_hours_5"
            self.change(sub_key, self.config[self.key][self.usage_point_id][sub_key], False)
        except Exception:
            self.change(sub_key, self.default()[sub_key], False)
        try:
            sub_key = "offpeak_hours_6"
            self.change(sub_key, self.config[self.key][self.usage_point_id][sub_key], False)
        except Exception:
            self.change(sub_key, self.default()[sub_key], False)
        try:
            sub_key = "refresh_addresse"
            self.change(sub_key, str2bool(self.config[self.key][self.usage_point_id][sub_key]), False)
        except Exception:
            self.change(sub_key, self.default()[sub_key], False)
        try:
            sub_key = "refresh_contract"
            self.change(sub_key, str2bool(self.config[self.key][self.usage_point_id][sub_key]), False)
        except Exception:
            self.change(sub_key, self.default()[sub_key], False)

        # Save configuration
        if self.write:
            edit_config({self.key: {self.usage_point_id: self.json}})
            data = {}
            for key, value in self.json.items():
                data[key] = self.check_format(key, value)
            self.db.set(data)

    def check_format(self, key, value):
        """Check if value is a datetime and return in datetime format (if datetime)."""
        try:
            if value == "":
                return None
            if key in [
                "consumption_max_date",
                "consumption_detail_max_date",
                "production_max_date",
                "production_detail_max_date",
            ]:
                return datetime.strptime(value, "%Y-%m-%d").replace(tzinfo=TIMEZONE_UTC)
            return value
        except Exception:
            return None

    def change(self, key: str, value: str, write_file: bool = True) -> None:
        """Change configuration."""
        setattr(self, f"_{key}", value)
        self.json[key] = value
        if write_file:
            edit_config({self.key: {self.usage_point_id: {key: value}}})
            self.db.set_value(key, self.check_format(key, value))

    @property
    def enable(self) -> bool:
        """Enable/Disable UsagePoint."""
        return self._enable

    @enable.setter
    def enable(self, value):
        self.change(inspect.currentframe().f_code.co_name, value)

    @property
    def name(self) -> str:
        """UsagePoint name."""
        return self._name

    @name.setter
    def name(self, value):
        self.change(inspect.currentframe().f_code.co_name, value)

    @property
    def token(self) -> str:
        """UsagePoint token."""
        return self._token

    @token.setter
    def token(self, value):
        self.change(inspect.currentframe().f_code.co_name, value)

    @property
    def cache(self) -> bool:
        """Enable/Disable cache."""
        return self._cache

    @cache.setter
    def cache(self, value):
        self.change(inspect.currentframe().f_code.co_name, value)

    @property
    def plan(self) -> str:
        """UsagePoint plan."""
        return self._plan

    @plan.setter
    def plan(self, value):
        self.change(inspect.currentframe().f_code.co_name, value)

    @property
    def consumption(self) -> bool:
        """Enable/Disable consumption."""
        return self._consumption

    @consumption.setter
    def consumption(self, value):
        self.change(inspect.currentframe().f_code.co_name, value)

    @property
    def consumption_detail(self) -> bool:
        """Enable/Disable consumption detail."""
        return self._consumption_detail

    @consumption_detail.setter
    def consumption_detail(self, value):
        self.change(inspect.currentframe().f_code.co_name, value)

    @property
    def consumption_max_power(self) -> bool:
        """Enable/Disable consumption max power."""
        return self._consumption_max_power

    @consumption_max_power.setter
    def consumption_max_power(self, value):
        self.change(inspect.currentframe().f_code.co_name, value)

    @property
    def consumption_price_hc(self) -> float:
        """Consumption price HC."""
        return self._consumption_price_hc

    @consumption_price_hc.setter
    def consumption_price_hc(self, value):
        self.change(inspect.currentframe().f_code.co_name, value)

    @property
    def consumption_price_hp(self) -> float:
        """Consumption price HP."""
        return self._consumption_price_hp

    @consumption_price_hp.setter
    def consumption_price_hp(self, value):
        self.change(inspect.currentframe().f_code.co_name, value)

    @property
    def consumption_price_base(self) -> float:
        """Consumption price BASE."""
        return self._consumption_price_base

    @consumption_price_base.setter
    def consumption_price_base(self, value):
        self.change(inspect.currentframe().f_code.co_name, value)

    @property
    def consumption_max_date(self) -> str:
        """Consumption max date."""
        return self._consumption_max_date

    @consumption_max_date.setter
    def consumption_max_date(self, value):
        self.change(inspect.currentframe().f_code.co_name, value)

    @property
    def consumption_detail_max_date(self) -> str:
        """Consumption detail max date."""
        return self._consumption_detail_max_date

    @consumption_detail_max_date.setter
    def consumption_detail_max_date(self, value):
        self.change(inspect.currentframe().f_code.co_name, value)

    @property
    def production(self) -> bool:
        """Enable/Disable production."""
        return self._production

    @production.setter
    def production(self, value):
        self.change(inspect.currentframe().f_code.co_name, value)

    @property
    def production_detail(self) -> bool:
        """Enable/Disable production detail."""
        return self._production_detail

    @production_detail.setter
    def production_detail(self, value):
        self.change(inspect.currentframe().f_code.co_name, value)

    @property
    def production_max_date(self) -> str:
        """Production max date."""
        return self._production_max_date

    @production_max_date.setter
    def production_max_date(self, value):
        self.change(inspect.currentframe().f_code.co_name, value)

    @property
    def production_detail_max_date(self) -> str:
        """Production detail max date."""
        return self._production_detail_max_date

    @production_detail_max_date.setter
    def production_detail_max_date(self, value):
        self.change(inspect.currentframe().f_code.co_name, value)

    @property
    def production_price(self) -> float:
        """Production price."""
        return self._production_price

    @production_price.setter
    def production_price(self, value):
        self.change(inspect.currentframe().f_code.co_name, value)

    @property
    def offpeak_hours_0(self) -> str:
        """Offpeak hours 0."""
        return self._offpeak_hours_0

    @offpeak_hours_0.setter
    def offpeak_hours_0(self, value):
        self.change(inspect.currentframe().f_code.co_name, value)

    @property
    def offpeak_hours_1(self) -> str:
        """Offpeak hours 1."""
        return self._offpeak_hours_1

    @offpeak_hours_1.setter
    def offpeak_hours_1(self, value):
        self.change(inspect.currentframe().f_code.co_name, value)

    @property
    def offpeak_hours_2(self) -> str:
        """Offpeak hours 2."""
        return self._offpeak_hours_2

    @offpeak_hours_2.setter
    def offpeak_hours_2(self, value):
        self.change(inspect.currentframe().f_code.co_name, value)

    @property
    def offpeak_hours_3(self) -> str:
        """Offpeak hours 3."""
        return self._offpeak_hours_3

    @offpeak_hours_3.setter
    def offpeak_hours_3(self, value):
        self.change(inspect.currentframe().f_code.co_name, value)

    @property
    def offpeak_hours_4(self) -> str:
        """Offpeak hours 4."""
        return self._offpeak_hours_4

    @offpeak_hours_4.setter
    def offpeak_hours_4(self, value):
        self.change(inspect.currentframe().f_code.co_name, value)

    @property
    def offpeak_hours_5(self) -> str:
        """Offpeak hours 5."""
        return self._offpeak_hours_5

    @offpeak_hours_5.setter
    def offpeak_hours_5(self, value):
        self.change(inspect.currentframe().f_code.co_name, value)

    @property
    def offpeak_hours_6(self) -> str:
        """Offpeak hours 6."""
        return self._offpeak_hours_6

    @offpeak_hours_6.setter
    def offpeak_hours_6(self, value):
        self.change(inspect.currentframe().f_code.co_name, value)

    @property
    def refresh_addresse(self) -> bool:
        """Enable/Disable refresh addresse."""
        return self._refresh_addresse

    @refresh_addresse.setter
    def refresh_addresse(self, value):
        self.change(inspect.currentframe().f_code.co_name, value)

    @property
    def refresh_contract(self) -> bool:
        """Enable/Disable refresh contract."""
        return self._refresh_contract

    @refresh_contract.setter
    def refresh_contract(self, value):
        self.change(inspect.currentframe().f_code.co_name, value)


class MyElectricalData:
    """MyElectricalData configuration."""

    def __init__(self, config: dict) -> None:
        self.config = config
        self.key = "myelectricaldata"
        self.usage_point_config = {}
        self.json: dict = {}
        self.load()

    def default(self) -> dict:
        """Return default configuration as dictionary."""
        return {"MON_POINT_DE_LIVRAISON": UsagePointId(self.config, "MON_POINT_DE_LIVRAISON", write=False).default()}

    def load(self):
        """Load configuration from file."""
        if self.config is None or "myelectricaldata" not in self.config:
            self.config = {"myelectricaldata": self.default()}

        for usage_point_id in self.config["myelectricaldata"]:
            usage_point_config: UsagePointId = UsagePointId(self.config, str(usage_point_id))
            self.usage_point_config[usage_point_id] = usage_point_config
            self.json[usage_point_id] = usage_point_config.json

    def new(self, usage_point_id: str):
        """Create new usage point."""
        usage_point_config: UsagePointId = UsagePointId(self.config, str(usage_point_id))
        self.usage_point_config[usage_point_id] = usage_point_config
        self.json[usage_point_id] = usage_point_config.json
