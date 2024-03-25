"""Main module of the application."""
import logging
from os import environ, getenv

import uvicorn
from fastapi import APIRouter, FastAPI
from fastapi.openapi.utils import get_openapi
from fastapi.staticfiles import StaticFiles
from fastapi_utils.tasks import repeat_every

from config import LOG_FORMAT, LOG_FORMAT_DATE, cycle_minimun
from database.config import DatabaseConfig
from database.usage_points import DatabaseUsagePoints
from dependencies import APPLICATION_PATH, get_version, logo, str2bool, title, title_warning
from init import CONFIG
from models.jobs import Job
from routers import account, action, data, html, info

if "DEV" in environ or "DEBUG" in environ:
    title_warning("Run in Development mode")
else:
    title("Run in production mode")

usage_point_list = []
if CONFIG.list_usage_point() is not None:
    for upi, _ in CONFIG.list_usage_point().items():
        usage_point_list.append(upi)

title("Nettoyage de la base de données...")
for usage_point in DatabaseUsagePoints().get_all():
    if usage_point.usage_point_id not in usage_point_list:
        DatabaseUsagePoints(usage_point.usage_point_id).delete()

swagger_configuration = {
    "operationsSorter": "method",
    "tagsSorter": "alpha",
    "deepLinking": True,
}
APP = FastAPI(title="MyElectricalData", swagger_ui_parameters=swagger_configuration)
APP.mount("/static", StaticFiles(directory=f"{APPLICATION_PATH}/static"), name="static")

ROUTER = APIRouter()
APP.include_router(info.ROUTER)
APP.include_router(html.ROUTER)
APP.include_router(data.ROUTER)
APP.include_router(action.ROUTER)
APP.include_router(account.ROUTER)

INFO = {
    "title": "MyElectricalData",
    "version": get_version(),
    "description": "",
    "contact": {
        "name": "m4dm4rtig4n",
        "url": "https://github.com/MyElectricalData/myelectricaldata_import/issues",
    },
    "license_info": {
        "name": "Apache 2.0",
        "url": "https://www.apache.org/licenses/LICENSE-2.0.html",
    },
    "routes": APP.routes,
    "servers": [],
}

OPENAPI_SCHEMA = get_openapi(
    title=INFO["title"],
    version=INFO["version"],
    description=INFO["description"],
    contact=INFO["contact"],
    license_info=INFO["license_info"],
    routes=INFO["routes"],
    servers=INFO["servers"],
)
OPENAPI_SCHEMA["info"]["x-logo"] = {
    "url": "https://pbs.twimg.com/profile_images/1415338422143754242/axomHXR0_400x400.png"
}

APP.openapi_schema = OPENAPI_SCHEMA

CYCLE = CONFIG.get("cycle")
if not CYCLE:
    CYCLE = 14400
elif CYCLE < cycle_minimun:
    logging.warning("Le cycle minimun est de 3600s")
    CYCLE = cycle_minimun
    CONFIG.set("cycle", cycle_minimun)


@APP.on_event("startup")
@repeat_every(seconds=CYCLE, wait_first=False)
def import_job():
    """Perform the import job."""
    Job().boot()


@APP.on_event("startup")
@repeat_every(seconds=3600, wait_first=True)
def home_assistant_export():
    """Perform the home assistant export job."""
    Job().export_home_assistant(target="ecowatt")


@APP.on_event("startup")
@repeat_every(seconds=600, wait_first=False)
def gateway_status():
    """Perform gateway status."""
    Job().get_gateway_status()


if __name__ == "__main__":
    logo(get_version())
    log_config = uvicorn.config.LOGGING_CONFIG
    log_config["formatters"]["access"]["fmt"] = LOG_FORMAT
    log_config["formatters"]["access"]["datefmt"] = LOG_FORMAT_DATE
    log_config["formatters"]["default"]["fmt"] = LOG_FORMAT
    log_config["formatters"]["default"]["datefmt"] = LOG_FORMAT_DATE
    uvicorn_params = {
        "host": "0.0.0.0",  # noqa: S104
        "port": CONFIG.port(),
        "log_config": log_config,
    }
    if "DEV" in environ and str2bool(getenv("DEV")) or "DEBUG" in environ and str2bool(getenv("DEBUG")):
        uvicorn_params["reload"] = True
        uvicorn_params["reload_dirs"] = [APPLICATION_PATH]

    ssl_config = CONFIG.ssl_config()
    if ssl_config:
        uvicorn_params = {**uvicorn_params, **ssl_config}

    uvicorn.run("main:APP", **uvicorn_params)
