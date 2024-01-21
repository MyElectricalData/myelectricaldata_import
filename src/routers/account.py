from fastapi import APIRouter, Request

from models.ajax import Ajax

ROUTER = APIRouter(tags=["Account"], include_in_schema=False)


@ROUTER.post("/configuration/{usage_point_id}")
@ROUTER.post("/configuration/{usage_point_id}/", include_in_schema=False)
async def configuration(request: Request, usage_point_id):
    form = await request.form()
    return Ajax(usage_point_id).configuration(form)


@ROUTER.post("/new_account")
@ROUTER.post("/new_account/", include_in_schema=False)
async def new_account(request: Request):
    form = await request.form()
    return Ajax().new_account(form)


@ROUTER.get("/account_status/{usage_point_id}")
@ROUTER.get("/account_status/{usage_point_id}/", include_in_schema=False)
def account_status(usage_point_id):
    return Ajax(usage_point_id).account_status()
