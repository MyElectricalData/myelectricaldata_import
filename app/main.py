import logging
from os import getenv, environ

import uvicorn
from fastapi import FastAPI, APIRouter
from fastapi.openapi.utils import get_openapi
from fastapi_utils.tasks import repeat_every

from config import LOG_FORMAT, LOG_FORMAT_DATE, cycle_minimun
from dependencies import title, get_version, title_warning, logo
from init import CONFIG, DB
from routers import account
from routers import action
from routers import data
from routers import html
from routers import info
from tasks import Tasks

if "DEV" in environ or "DEBUG" in environ:
    title_warning("Run in Development mode")
else:
    title(" Run in production mode")

title(" Chargement du config.yaml...")
usage_point_list = []
if CONFIG.list_usage_point() is not None:
    for upi, upi_data in CONFIG.list_usage_point().items():
        logging.info(f"{upi}")
        DB.set_usage_point(upi, upi_data)
        usage_point_list.append(upi)
        logging.info("  => Success")
else:
    logging.warning("Aucun point de livraison détecté.")

title(" Nettoyage de la base de données...")
DB.clean_database(usage_point_list)

swagger_configuration = {
    "operationsSorter": "method",
    # "defaultModelRendering": "model",
    "tagsSorter": "alpha",
    # "docExpansion": "none",
    "deepLinking": True,
}
APP = FastAPI(
    title="MyElectricalData",
    swagger_ui_parameters=swagger_configuration
)

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
        "url": "https://github.com/MyElectricalData/myelectricaldata/issues",
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

CYCLE = CONFIG.get('cycle')
if CYCLE < cycle_minimun:
    logging.warning("Le cycle minimun est de 3600s")
    CYCLE = cycle_minimun
    CONFIG.set("cycle", cycle_minimun)


@APP.on_event("startup")
@repeat_every(seconds=CYCLE, wait_first=False)
def tasks():
    Tasks()


if __name__ == '__main__':
    logo(get_version())
    log_config = uvicorn.config.LOGGING_CONFIG
    log_config["formatters"]["access"]["fmt"] = LOG_FORMAT
    log_config["formatters"]["access"]["datefmt"] = LOG_FORMAT_DATE
    log_config["formatters"]["default"]["fmt"] = LOG_FORMAT
    log_config["formatters"]["default"]["datefmt"] = LOG_FORMAT_DATE
    tasks()
    if ("DEV" in environ and getenv("DEV")) or ("DEBUG" in environ and getenv("DEBUG")):
        uvicorn.run(
            "main:APP",
            host="0.0.0.0",
            port=5000,
            reload=True,
            reload_dirs=["/app"],
            log_config=log_config,
        )
    else:
        uvicorn.run(
            "main:APP",
            host="0.0.0.0",
            port=5000,
            log_config=log_config
        )
