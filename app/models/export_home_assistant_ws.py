import asyncio
import logging
from datetime import datetime, timedelta
from enum import Enum
import aiohttp
from typing import Any, Dict, List, Optional
from init import CONFIG


async def HomeAssistant():
    home_assistant_ws_config = CONFIG.home_assistant_ws()
    url = f"{'wss' if home_assistant_ws_config['ssl'] else 'ws'}://{home_assistant_ws_config['url']}/api/websocket"
    logging.info(f"Connecting to websocket at {url}")
    async with aiohttp.ClientSession() as session:
        async with session.ws_connect(url) as websocket:
            ha_ws = HomeAssistantWs(websocket)

            # Must authenticate before sending commands
            logging.info("Authenticating with Home Assistant")
            await ha_ws.authenticate(home_assistant_ws_config['token'])

            ha_ws.recorder_import_statistics()

class Unit(Enum):
    KILO_WATT_HOUR = "kWh"
    EURO = "EUR"


class ElectricityType(Enum):
    CONSUMPTION = "consumption"
    PRODUCTION = "production"


class TariffType(Enum):
    BASE = "base"
    HC = "hc"
    HP = "hp"


class PlanType(Enum):
    BASE = "BASE"
    HCHP = "HC/HP"

StatisticData = Dict[str, Any]

TariffsPrices = Dict[TariffType, float]
PlanPrices = Dict[ElectricityType, TariffsPrices]

class StatisticMetadata:
    def __init__(self, usage_point_id: str, electricity_type: ElectricityType, tariff_type: TariffType, unit_of_measurement: Unit, max_date: datetime) -> None:
        # Metadata for MyElectricalData
        self.usage_point_id = usage_point_id
        self.max_date = max_date
        self.electricity_type = electricity_type
        self.tariff_type = tariff_type
        self.db_table_id = f"{electricity_type.value}_detail"
        # Metadata for Home Assistant
        self.unit_of_measurement = unit_of_measurement
        self.source = "myelectricaldata"
        is_cost = (unit_of_measurement == Unit.EURO)
        # id = myelectricaldata:xxx_(base|hc|hp)_(consumption|production)_(cost)
        self.id = f"{self.source}:{usage_point_id}_{tariff_type.value}_{electricity_type.value}{'_cost' if is_cost else ''}"
        # TODO use name in config.yaml ?
        self.name = f"MyElectricalData - {usage_point_id} {tariff_type.name} {electricity_type.value}{' cost' if is_cost else ''}"

class HomeAssistantWs:

    def __init__(self, websocket: aiohttp.ClientWebSocketResponse) -> None:
        self._websocket = websocket
        self._command_id = 0
        self.config = CONFIG
        self.home_assistant_ws_config = CONFIG.home_assistant_ws()

    async def authenticate(self, access_token: str) -> None:
        response = await self._websocket.receive_json()
        logging.info(f"authenticate: received response {response}")
        if response["type"] != "auth_required":
            raise Exception("authenticate: invalid server response {response}")

        # Auth
        await self._websocket.send_json({
            "type": "auth",
            "access_token": access_token
        })

        response = await self._websocket.receive_json()
        logging.info(f"authenticate: received response {response}")
        if response["type"] != "auth_ok":
            raise Exception("authenticate: auth NOT ok, check Home Assistant Long-Lived Access Token")

    async def recorder_import_statistics(self, stat_metadata: StatisticMetadata, stats: List[StatisticData]) -> None:
        self._command_id += 1
        await self._websocket.send_json({
            "id": self._command_id,
            "type": "recorder/import_statistics",
            "metadata": {
                "has_mean": False,
                "has_sum": True,
                "name": stat_metadata.name,
                "source": stat_metadata.source,
                "statistic_id": stat_metadata.id,
                "unit_of_measurement": stat_metadata.unit_of_measurement.value,
            },
            "stats": stats
        })

        response = await self._websocket.receive_json()
        print(f"recorder_import_statistics: received response {response}")
        if not response["success"]:
            raise Exception(f"recorder_import_statistics: failed")

asyncio.run(HomeAssistant())
