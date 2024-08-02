"""Main module of the application."""

from contextlib import asynccontextmanager
from os import listdir
from pathlib import Path

import uvicorn
from fastapi import APIRouter, FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi_utils.tasks import repeat_every
from uvicorn.config import LOGGING_CONFIG

from config.main import APP_CONFIG
from models.jobs import Job
from routers import account, action, data, html, info
from utils import get_version


#######################################################################################################################
# JOBS
@repeat_every(seconds=APP_CONFIG.server.cycle, wait_first=False)
def job_boot():
    """Bootstap jobs."""
    Job().boot()


@repeat_every(seconds=3600, wait_first=True)
def job_home_assistant():
    """Home Assistant Ecowatt."""
    Job().export_home_assistant(target="ecowatt")


@repeat_every(seconds=600, wait_first=False)
def job_gateway_status():
    """Gateway status check."""
    Job().get_gateway_status()


@asynccontextmanager
async def bootstrap(app: FastAPI):  # pylint: disable=unused-argument
    """Bootstap jobs."""
    await job_boot()
    await job_home_assistant()
    await job_gateway_status()
    yield


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
    lifespan=bootstrap,
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
    uvicorn_params = {
        "reload": False,
        "log_config": log_config,
        "host": APP_CONFIG.server.cidr,
        "port": APP_CONFIG.server.port,
        "log_level": "error",
        "reload_dirs": None,
        "reload_includes": None,
        "reload_excludes": None,
    }
    if APP_CONFIG.logging.log_http:
        uvicorn_params["log_level"] = "info"
    if APP_CONFIG.dev:
        uvicorn_params["reload"] = True
        uvicorn_params["reload_dirs"] = [APP_CONFIG.application_path]
        uvicorn_params["reload_includes"] = [APP_CONFIG.application_path]
        uvicorn_params["reload_excludes"] = [".venv", ".git/*", ".idea/*", ".vscode/*", ".py[cod]"]

    uvicorn_params = {**uvicorn_params, **APP_CONFIG.ssl_config.__dict__}
    uvicorn.run("main:APP", **uvicorn_params)
