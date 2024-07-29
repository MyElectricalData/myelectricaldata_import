"""Account routes."""

import inspect

from fastapi import APIRouter, Request
from opentelemetry import trace

from config.main import APP_CONFIG
from models.ajax import Ajax

ROUTER = APIRouter(tags=["Account"], include_in_schema=False)


@ROUTER.post("/configuration/{usage_point_id}")
@ROUTER.post("/configuration/{usage_point_id}/", include_in_schema=False)
async def configuration(request: Request, usage_point_id):
    """Account configuration."""
    with APP_CONFIG.tracer.start_as_current_span(f"{__name__}.{inspect.currentframe().f_code.co_name}"):
        trace.get_current_span().set_attribute("usage_point_id", usage_point_id)
        form = await request.form()
        return Ajax(usage_point_id).configuration(form)


@ROUTER.post("/new_account")
@ROUTER.post("/new_account/", include_in_schema=False)
async def new_account(request: Request):
    """Create account."""
    with APP_CONFIG.tracer.start_as_current_span(f"{__name__}.{inspect.currentframe().f_code.co_name}"):
        form = await request.form()
        return Ajax().new_account(form)


@ROUTER.get("/account_status/{usage_point_id}")
@ROUTER.get("/account_status/{usage_point_id}/", include_in_schema=False)
def account_status(usage_point_id):
    """Get account status."""
    with APP_CONFIG.tracer.start_as_current_span(f"{__name__}.{inspect.currentframe().f_code.co_name}"):
        return Ajax(usage_point_id).account_status()
