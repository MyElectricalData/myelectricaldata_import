from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse

from init import CONFIG, DB
from models.ajax import Ajax

ROUTER = APIRouter(
    tags=["Données"]
)


@ROUTER.put("/tempo", include_in_schema=False)
@ROUTER.put("/tempo/", include_in_schema=False)
def put_tempo():
    """Force la récupération des données Tempo."""
    return Ajax(CONFIG, DB).fetch_tempo()


@ROUTER.get("/tempo", summary="Retourne les données Tempo du cache local.")
@ROUTER.get("/tempo/", include_in_schema=False)
def tempo():
    """Retourne les données Tempo du cache local."""
    return Ajax(CONFIG, DB).get_tempo()


@ROUTER.put("/ecowatt", include_in_schema=False)
@ROUTER.put("/ecowatt/", include_in_schema=False)
def ecowatt():
    return Ajax(CONFIG, DB).fetch_ecowatt()


@ROUTER.get("/ecowatt", summary="Retourne les données Ecowatt du cache local.")
@ROUTER.get("/ecowatt/", include_in_schema=False)
def ecowatt():
    """Retourne les données Ecowatt du cache local."""
    return Ajax(CONFIG, DB).get_ecowatt()


@ROUTER.put("/price/{usage_point_id}", summary="Met à jour le cache local du comparateur d'abonnement.",
            tags=["Données"])
@ROUTER.put("/price/{usage_point_id}/", include_in_schema=False)
def fetch_price(usage_point_id):
    """Mise à jour le cache local du comparateur d'abonnement."""
    return Ajax(CONFIG, DB, usage_point_id).generate_price()


@ROUTER.get("/price/{usage_point_id}", summary="Retourne le résultat du comparateur d'abonnements.")
@ROUTER.get("/price/{usage_point_id}/", include_in_schema=False)
def get_price(usage_point_id):
    """Retourne les données du cache local du comparateur d'abonnement."""
    return Ajax(CONFIG, DB, usage_point_id).get_price()


@ROUTER.get("/get/{usage_point_id}/{measurement_direction}", response_class=HTMLResponse)
@ROUTER.get("/get/{usage_point_id}/{measurement_direction}/", response_class=HTMLResponse, include_in_schema=False)
def get_data(request: Request, usage_point_id, measurement_direction):
    return Ajax(CONFIG, DB, usage_point_id).datatable(measurement_direction, request)
