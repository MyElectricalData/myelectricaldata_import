from fastapi import APIRouter, Request

from init import CONFIG, DB
from models.ajax import Ajax

ROUTER = APIRouter(
    tags=["Account"],
    include_in_schema=False
)


@ROUTER.post("/configuration/{usage_point_id}")
@ROUTER.post("/configuration/{usage_point_id}/", include_in_schema=False)
def configuration(request: Request, usage_point_id):
    return Ajax(CONFIG, DB, usage_point_id).configuration(request)


@ROUTER.post("/new_account")
@ROUTER.post("/new_account/", include_in_schema=False)
def new_account():
    return Ajax(CONFIG, DB).new_account(requests)


@ROUTER.get("/account_status/{usage_point_id}")
@ROUTER.get("/account_status/{usage_point_id}/", include_in_schema=False)
def account_status(usage_point_id):
    return Ajax(CONFIG, DB, usage_point_id).account_status()
