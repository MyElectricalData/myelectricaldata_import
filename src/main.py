"""Main module of the application."""

from os import listdir
from pathlib import Path

import uvicorn
from fastapi import APIRouter, FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi_utils.tasks import repeat_every
from uvicorn.config import LOGGING_CONFIG

from config.main import APP_CONFIG
from database.usage_points import DatabaseUsagePoints
from models.jobs import Job
from routers import account, action, data, html, info
from utils import get_version, title

usage_point_list = []
if APP_CONFIG.myelectricaldata.usage_point_config is not None:
    for upi, _ in APP_CONFIG.myelectricaldata.usage_point_config.items():
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


APP = FastAPI(
    title="MyElectricalData",
    version=get_version(),
    description="MyElectricalData",
    contact={
        "name": "m4dm4rtig4n",
        "url": "https://github.com/MyElectricalData/myelectricaldata_import/issues",
    },
    license_info={
        "name": "Apache 2.0",
        "url": "https://www.apache.org/licenses/LICENSE-2.0.html",
    },
    swagger_configuration={
        "operationsSorter": "method",
        "tagsSorter": "alpha",
        "deepLinking": True,
    },
)

#######################################################################################################################
# Static files
STATIC_FOLDER = f"{APP_CONFIG.application_path}/static"
if Path(STATIC_FOLDER).is_dir() and listdir(STATIC_FOLDER):
    APP.mount("/static", StaticFiles(directory=STATIC_FOLDER), name="static")


#######################################################################################################################
# ROUTER
ROUTER = APIRouter()
APP.include_router(info.ROUTER)
APP.include_router(html.ROUTER)
APP.include_router(data.ROUTER)
APP.include_router(action.ROUTER)
APP.include_router(account.ROUTER)


#######################################################################################################################
# JOB TASKS
@APP.on_event("startup")
@repeat_every(seconds=APP_CONFIG.server.cycle, wait_first=False)
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


#######################################################################################################################
# FastAPI opentelemetry configuration
APP_CONFIG.tracing_fastapi(APP)

#######################################################################################################################
# BOOTSTRAP
if __name__ == "__main__":
    log_config = LOGGING_CONFIG
    log_config["formatters"]["access"]["fmt"] = APP_CONFIG.logging.log_format
    log_config["formatters"]["access"]["datefmt"] = APP_CONFIG.logging.log_format_date
    log_config["formatters"]["default"]["fmt"] = APP_CONFIG.logging.log_format
    log_config["formatters"]["default"]["datefmt"] = APP_CONFIG.logging.log_format_date
    uvicorn_params = {}
    uvicorn_params["log_config"] = log_config
    uvicorn_params["host"] = APP_CONFIG.server.cidr
    uvicorn_params["port"] = APP_CONFIG.server.port
    uvicorn_params["reload"] = True
    uvicorn_params["reload_dirs"] = [APP_CONFIG.application_path]
    uvicorn_params["reload_includes"] = [APP_CONFIG.application_path]
    uvicorn_params["reload_excludes"] = [".venv", ".git/*", ".idea/*", ".vscode/*", ".py[cod]"]
    if APP_CONFIG.logging.log_http:
        uvicorn_params["log_level"] = "info"
    else:
        uvicorn_params["log_level"] = "error"
    uvicorn_params = {**uvicorn_params, **APP_CONFIG.ssl_config.__dict__}

    APP_CONFIG.display()
    uvicorn.run("main:APP", **uvicorn_params)
