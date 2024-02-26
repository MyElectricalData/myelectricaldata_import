from fastapi import APIRouter, Path

from doc import DOCUMENTATION
from models.ajax import Ajax

ROUTER = APIRouter(
    tags=["Ajax"],
)


@ROUTER.get(
    "/import/{usage_point_id}",
    summary="Force l'importation des données depuis la passerelle.",
)
@ROUTER.get("/import/{usage_point_id}/", include_in_schema=False)
def import_all_data(usage_point_id: str = Path(..., description=DOCUMENTATION["usage_point_id"])):
    """Force l'importation des données depuis la passerelle."""
    return Ajax(usage_point_id).import_data()


@ROUTER.get(
    "/import/{usage_point_id}/{target}",
    summary="Permet de forcer une tâche d'importation.",
)
@ROUTER.get("/import/{usage_point_id}/{target}/", include_in_schema=False)
def import_data(
    usage_point_id: str = Path(..., description=DOCUMENTATION["usage_point_id"]),
    target: str = Path(..., description=DOCUMENTATION["target_full"]),
):
    """Permet de forcer une tâche d'importation.

    Target :
    - tempo
    - ecowatt
    - account_status
    - contract
    - addresses
    - consumption
    - consumption_detail
    - production
    - production_detail
    - consumption_max_power
    - stat
    - mqtt
    - home_assistant
    - influxdb
    """
    return Ajax(usage_point_id).import_data(target)


@ROUTER.get("/reset/{usage_point_id}", summary="Efface les données du point de livraison.")
@ROUTER.get("/reset/{usage_point_id}/", include_in_schema=False)
def reset_all_data(usage_point_id: str = Path(..., description=DOCUMENTATION["usage_point_id"])):
    """Efface les données du point de livraison."""
    return Ajax(usage_point_id).reset_all_data()


@ROUTER.get("/delete/{usage_point_id}", summary="Supprime le point de livraison.")
@ROUTER.get("/delete/{usage_point_id}/", include_in_schema=False)
def delete_all_data(usage_point_id: str = Path(..., description=DOCUMENTATION["usage_point_id"])):
    """Supprime le point de livraison."""
    return Ajax(usage_point_id).delete_all_data()


@ROUTER.get(
    "/reset_gateway/{usage_point_id}",
    summary="Efface le cache du point de livraison sur la passerelle.",
)
@ROUTER.get("/reset_gateway/{usage_point_id}/", include_in_schema=False)
def reset_gateway(usage_point_id: str = Path(..., description=DOCUMENTATION["usage_point_id"])):
    """Efface le cache du point de livraison sur la passerelle."""
    return Ajax(usage_point_id).reset_gateway()


@ROUTER.get(
    "/usage_point_id/{usage_point_id}/{target}/reset/{date}",
    summary="Efface les données cible à une date spécifique.",
)
@ROUTER.get("/usage_point_id/{usage_point_id}/{target}/reset/{date}/", include_in_schema=False)
def reset_data(
    usage_point_id: str = Path(..., description=DOCUMENTATION["usage_point_id"]),
    target: str = Path(..., description=DOCUMENTATION["target"]),
    date: str = Path(..., description=DOCUMENTATION["date_format"]),
):
    """Efface une date du cache local.

    Target :
    - consumption
    - consumption_detail
    - production
    - production_detail
    - consumption_max_power
    """
    return Ajax(usage_point_id).reset_data(target, date)


@ROUTER.get(
    "/usage_point_id/{usage_point_id}/{target}/blacklist/{date}",
    summary="Blacklist une date de récupération des données.",
)
@ROUTER.get(
    "/usage_point_id/{usage_point_id}/{target}/blacklist/{date}/",
    include_in_schema=False,
)
def blacklist_data(
    usage_point_id: str = Path(..., description=DOCUMENTATION["usage_point_id"]),
    target: str = Path(..., description=DOCUMENTATION["target"]),
    date: str = Path(..., description=DOCUMENTATION["date_format"]),
):
    """Blacklist une date de récupération des données.

    Target :
    - consumption
    - consumption_detail
    - production
    - production_detail
    - consumption_max_power
    """
    return Ajax(usage_point_id).blacklist(target, date)


@ROUTER.get(
    "/usage_point_id/{usage_point_id}/{target}/whitelist/{date}",
    summary="Whitelist une date de récupération des données.",
)
@ROUTER.get(
    "/usage_point_id/{usage_point_id}/{target}/whitelist/{date}/",
    include_in_schema=False,
)
def whitelist_data(
    usage_point_id: str = Path(..., description=DOCUMENTATION["usage_point_id"]),
    target: str = Path(..., description=DOCUMENTATION["target"]),
    date: str = Path(..., description=DOCUMENTATION["date_format"]),
):
    """Whitelist une date de récupération des données.

    Target :
    - consumption
    - consumption_detail
    - production
    - production_detail
    - consumption_max_power
    """
    return Ajax(usage_point_id).whitelist(target, date)


@ROUTER.get(
    "/usage_point_id/{usage_point_id}/{target}/import/{date}",
    summary="Importe les données à une date spécifique.",
)
@ROUTER.get("/usage_point_id/{usage_point_id}/{target}/import/{date}/", include_in_schema=False)
def fetch_data(
    usage_point_id: str = Path(..., description=DOCUMENTATION["usage_point_id"]),
    target: str = Path(..., description=DOCUMENTATION["target"]),
    date: str = Path(..., description=DOCUMENTATION["date_format"]),
):
    """Importe les données à une date spécifique.

    Target :
    - consumption
    - consumption_detail
    - production
    - production_detail
    - consumption_max_power
    """
    return Ajax(usage_point_id).fetch(target, date)
