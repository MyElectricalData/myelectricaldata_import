from fastapi import APIRouter

from init import CONFIG, DB
from models.ajax import Ajax

ROUTER = APIRouter(
    tags=["Ajax"],
    include_in_schema=False
)


@ROUTER.get("/import/{usage_point_id}")
@ROUTER.get("/import/{usage_point_id}/", include_in_schema=False)
def import_all_data(usage_point_id):
    return Ajax(usage_point_id).import_data()


@ROUTER.get("/import/{usage_point_id}/{target}")
@ROUTER.get("/import/{usage_point_id}/{target}/", include_in_schema=False)
def import_data(usage_point_id, target):
    return Ajax(usage_point_id).import_data(target)


@ROUTER.get("/reset/{usage_point_id}")
@ROUTER.get("/reset/{usage_point_id}/", include_in_schema=False)
def reset_all_data(usage_point_id):
    return Ajax(usage_point_id).reset_all_data()


@ROUTER.get("/delete/{usage_point_id}")
@ROUTER.get("/delete/{usage_point_id}/", include_in_schema=False)
def delete_all_data(usage_point_id):
    return Ajax(usage_point_id).delete_all_data()


@ROUTER.get("/reset_gateway/{usage_point_id}")
@ROUTER.get("/reset_gateway/{usage_point_id}/", include_in_schema=False)
def reset_gateway(usage_point_id):
    return Ajax(usage_point_id).reset_gateway()


@ROUTER.get("/usage_point_id/{usage_point_id}/{target}/reset/{date}")
@ROUTER.get("/usage_point_id/{usage_point_id}/{target}/reset/{date}/", include_in_schema=False)
def reset_data(usage_point_id, target, date):
    return Ajax(usage_point_id).reset_data(target, date)


@ROUTER.get("/usage_point_id/{usage_point_id}/{target}/blacklist/{date}")
@ROUTER.get("/usage_point_id/{usage_point_id}/{target}/blacklist/{date}/", include_in_schema=False)
def blacklist_data(usage_point_id, target, date):
    return Ajax(usage_point_id).blacklist(target, date)


@ROUTER.get("/usage_point_id/{usage_point_id}/{target}/whitelist/{date}")
@ROUTER.get("/usage_point_id/{usage_point_id}/{target}/whitelist/{date}/", include_in_schema=False)
def whitelist_data(usage_point_id, target, date):
    return Ajax(usage_point_id).whitelist(target, date)


@ROUTER.get("/usage_point_id/{usage_point_id}/{target}/import/{date}")
@ROUTER.get("/usage_point_id/{usage_point_id}/{target}/import/{date}/", include_in_schema=False)
def fetch_data(usage_point_id, target, date):
    return Ajax(usage_point_id).fetch(target, date)
