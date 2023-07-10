from fastapi import Request, APIRouter
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.staticfiles import StaticFiles

from init import CONFIG, DB
from models.ajax import Ajax
from templates.index import Index
from templates.usage_point import UsagePoint

ROUTER = APIRouter(include_in_schema=False)

ROUTER.mount("/static", StaticFiles(directory="/app/static"), name="static")


@ROUTER.get('/favicon.ico')
async def favicon():
    return FileResponse("/app/static/favicon.ico")


@ROUTER.get("/", response_class=HTMLResponse)
def main():
    return Index(CONFIG, DB).display()


@ROUTER.get('/usage_point_id/{usage_point_id}', response_class=HTMLResponse)
@ROUTER.get('/usage_point_id/{usage_point_id}/', response_class=HTMLResponse)
def usage_point_id(usage_point_id):
    return UsagePoint(CONFIG, DB, usage_point_id).display()


@ROUTER.get("/datatable/{usage_point_id}/{measurement_direction}")
@ROUTER.get("/datatable/{usage_point_id}/{measurement_direction}/")
def datatable(request: Request, usage_point_id, measurement_direction):
    return Ajax(CONFIG, DB, usage_point_id).datatable(measurement_direction, request)
