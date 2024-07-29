"""Routers pour les informations générales."""

import inspect
from typing import Optional

from fastapi import APIRouter
from fastapi.responses import HTMLResponse
from pydantic import BaseModel

from config.main import APP_CONFIG
from database import DB
from models.ajax import Ajax

ROUTER = APIRouter(tags=["Infos"])


@ROUTER.get("/status", response_class=HTMLResponse, response_model=str, include_in_schema=False)
@ROUTER.get("/status/", response_class=HTMLResponse, response_model=str, include_in_schema=False)
@ROUTER.get(
    "/ping",
    response_class=HTMLResponse,
    response_model=str,
    summary="Remonte l'état du service.",
)
@ROUTER.get("/ping/", response_class=HTMLResponse, response_model=str, include_in_schema=False)
def status():
    """Remonte l'état du service."""
    return "ok"


@ROUTER.get(
    "/import_status",
    response_model=bool,
    summary="Remonte l'état du processus d'importation des données.",
)
@ROUTER.get("/import_status/", response_model=bool, include_in_schema=False)
def import_status():
    """Remonte l'état du processus d'importation des données."""
    return DB.lock_status()


class GatewayStatus(BaseModel):
    """RESPONSE Get."""

    status: bool = False
    information: Optional[str]
    nb_client: int
    waiting_estimation: str
    version: str


@ROUTER.get(
    "/gateway_status",
    response_model=GatewayStatus,
    summary="Remonte l'état de la passerelle MyElectricalData.",
)
@ROUTER.get("/gateway_status/", response_model=GatewayStatus, include_in_schema=False)
def gateway_status():
    """Remonte l'état de la passerelle MyElectricalData."""
    with APP_CONFIG.tracer.start_as_current_span(f"{__name__}.{inspect.currentframe().f_code.co_name}"):
        return Ajax().gateway_status()
