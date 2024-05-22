"""Return data from cache."""

import ast
from datetime import datetime

from fastapi import APIRouter, HTTPException, Path, Request
from fastapi.responses import HTMLResponse

from database.contracts import DatabaseContracts
from database.addresses import DatabaseAddresses
from database.daily import DatabaseDaily
from database.detail import DatabaseDetail
from database.max_power import DatabaseMaxPower
from database.usage_points import DatabaseUsagePoints
from doc import DOCUMENTATION
from models.ajax import Ajax

ROUTER = APIRouter(tags=["Données"])


@ROUTER.get("/contract/{usage_point_id}")
@ROUTER.get("/contract/{usage_point_id}/", include_in_schema=False)
def get_contract(usage_point_id: str = Path(..., description=DOCUMENTATION["usage_point_id"])):
    """Renvoie les information du contrat remonter par Enedis."""
    if DatabaseUsagePoints(usage_point_id).get() is not None:
        data = DatabaseContracts(usage_point_id).get().__dict__
        return dict(sorted(data.items()))
    else:
        raise HTTPException(
            status_code=404,
            detail=f"Le point de livraison '{usage_point_id}' est inconnu!",
        )


@ROUTER.get("/addresse/{usage_point_id}")
@ROUTER.get("/addresse/{usage_point_id}/", include_in_schema=False)
def get_contract(usage_point_id: str = Path(..., description=DOCUMENTATION["usage_point_id"])):
    """Renvoie les information postal remonter par Enedis."""
    if DatabaseUsagePoints(usage_point_id).get() is not None:
        data = DatabaseAddresses(usage_point_id).get().__dict__
        return dict(sorted(data.items()))
    else:
        raise HTTPException(
            status_code=404,
            detail=f"Le point de livraison '{usage_point_id}' est inconnu!",
        )


@ROUTER.put("/tempo", include_in_schema=False)
@ROUTER.put("/tempo/", include_in_schema=False)
def put_tempo():
    """Force la récupération des données Tempo."""
    return Ajax().fetch_tempo()


@ROUTER.get("/tempo", summary="Retourne les données Tempo du cache local.")
@ROUTER.get("/tempo/", include_in_schema=False)
def tempo():
    """Retourne les données Tempo du cache local."""
    return Ajax().get_tempo()


@ROUTER.put("/ecowatt", include_in_schema=False)
@ROUTER.put("/ecowatt/", include_in_schema=False)
def put_ecowatt():
    return Ajax().fetch_ecowatt()


@ROUTER.get("/ecowatt", summary="Retourne les données Ecowatt du cache local.")
@ROUTER.get("/ecowatt/", include_in_schema=False)
def ecowatt():
    """Retourne les données Ecowatt du cache local."""
    return Ajax().get_ecowatt()


@ROUTER.put(
    "/price/{usage_point_id}",
    summary="Met à jour le cache local du comparateur d'abonnement.",
    tags=["Données"],
)
@ROUTER.put("/price/{usage_point_id}/", include_in_schema=False)
def fetch_price(usage_point_id: str = Path(..., description=DOCUMENTATION["usage_point_id"])):
    """Mise à jour le cache local du comparateur d'abonnement."""
    usage_point_id = usage_point_id.strip()
    if DatabaseUsagePoints(usage_point_id).get() is not None:
        return ast.literal_eval(Ajax(usage_point_id).generate_price())
    else:
        raise HTTPException(
            status_code=404,
            detail=f"Le point de livraison '{usage_point_id}' est inconnu!",
        )


@ROUTER.get(
    "/price/{usage_point_id}",
    summary="Retourne le résultat du comparateur d'abonnements.",
)
@ROUTER.get("/price/{usage_point_id}/", include_in_schema=False)
def get_price(usage_point_id: str = Path(..., description=DOCUMENTATION["usage_point_id"])):
    """Retourne les données du cache local du comparateur d'abonnement."""
    usage_point_id = usage_point_id.strip()
    if DatabaseUsagePoints(usage_point_id).get() is not None:
        return Ajax(usage_point_id).get_price()
    else:
        raise HTTPException(
            status_code=404,
            detail=f"Le point de livraison '{usage_point_id}' est inconnu!",
        )


@ROUTER.get(
    "/daily/{usage_point_id}/{measurement_direction}/{begin}/{end}",
    summary="Retourne la consommation/production journalière.",
)
@ROUTER.get(
    "/daily/{usage_point_id}/{measurement_direction}/{begin}/{end}/",
    include_in_schema=False,
)
def get_data_daily(
    usage_point_id: str = Path(..., description=DOCUMENTATION["usage_point_id"]),
    measurement_direction: str = Path(..., description=DOCUMENTATION["measurement_direction"]),
    begin: str = Path(..., description=DOCUMENTATION["begin"]),
    end: str = Path(..., description=DOCUMENTATION["end"]),
):
    """Retourne les données du cache local de consommation journalière."""
    usage_point_id = usage_point_id.strip()
    begin = datetime.strptime(begin, "%Y-%m-%d")
    end = datetime.strptime(end, "%Y-%m-%d")
    if measurement_direction not in ["consumption", "production"]:
        raise HTTPException(
            status_code=404,
            detail="'measurement_direction' inconnu, valeur possible consumption/production",
        )
    data = DatabaseDaily(usage_point_id, measurement_direction).get_range(begin=begin, end=end)
    output = {"unit": "w", "data": {}}
    if data is not None:
        for d in data:
            output["data"][d.date] = d.value
    return output


@ROUTER.get(
    "/detail/{usage_point_id}/{measurement_direction}/{begin}/{end}",
    summary="Retourne la consommation/production détaillée.",
)
@ROUTER.get(
    "/detail/{usage_point_id}/{measurement_direction}/{begin}/{end}/",
    include_in_schema=False,
)
def get_data_detail(
    usage_point_id: str = Path(..., description=DOCUMENTATION["usage_point_id"]),
    measurement_direction: str = Path(..., description=DOCUMENTATION["measurement_direction"]),
    begin: str = Path(..., description=DOCUMENTATION["begin"]),
    end: str = Path(..., description=DOCUMENTATION["end"]),
):
    """Retourne les données du cache local de consommation détaillée."""
    usage_point_id = usage_point_id.strip()
    begin = datetime.strptime(begin, "%Y-%m-%d")
    end = datetime.strptime(end, "%Y-%m-%d")
    if measurement_direction not in ["consumption", "production"]:
        raise HTTPException(
            status_code=404,
            detail="'measurement_direction' inconnu, valeur possible consumption/production",
        )
    data = DatabaseDetail(usage_point_id, measurement_direction).get_range(begin=begin, end=end)
    output = {"unit": "w", "data": {}}
    if data is not None:
        for d in data:
            output["data"][d.date] = d.value
    return output


@ROUTER.get(
    "/max_power/{usage_point_id}/{begin}/{end}",
    summary="Retourne la puissance maximun.",
)
@ROUTER.get(
    "/max_power/{usage_point_id}/{begin}/{end}/",
    include_in_schema=False,
)
def get_max_power(
    usage_point_id: str = Path(..., description=DOCUMENTATION["usage_point_id"]),
    begin: str = Path(..., description=DOCUMENTATION["begin"]),
    end: str = Path(..., description=DOCUMENTATION["end"]),
):
    """Retourne les données du cache local de puissance maximal."""
    usage_point_id = usage_point_id.strip()
    begin = datetime.strptime(begin, "%Y-%m-%d")
    end = datetime.strptime(end, "%Y-%m-%d")
    data = DatabaseMaxPower(usage_point_id).get_range(begin=begin, end=end)
    print(data)
    output = {"unit": "w", "data": {}}
    if data is not None:
        for d in data:
            output["data"][d.event_date] = d.value
    return output


@ROUTER.get(
    "/get/{usage_point_id}/{measurement_direction}",
    response_class=HTMLResponse,
    include_in_schema=False,
)
@ROUTER.get(
    "/get/{usage_point_id}/{measurement_direction}/",
    response_class=HTMLResponse,
    include_in_schema=False,
)
def get_data(
    request: Request,
    usage_point_id: str = Path(..., description=DOCUMENTATION["usage_point_id"]),
    measurement_direction: str = Path(..., description=DOCUMENTATION["measurement_direction"]),
):
    usage_point_id = usage_point_id.strip()
    if DatabaseUsagePoints(usage_point_id).get() is not None:
        return Ajax(usage_point_id).datatable(measurement_direction, request)
    else:
        raise HTTPException(
            status_code=404,
            detail=f"Le point de livraison '{usage_point_id}' est inconnu!",
        )
