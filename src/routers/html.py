from fastapi import Request, APIRouter
from fastapi.responses import HTMLResponse, FileResponse

from init import CONFIG, DB
from models.ajax import Ajax
from templates.index import Index
from templates.usage_point import UsagePoint
from dependencies import APPLICATION_PATH

ROUTER = APIRouter(tags=["HTML"], include_in_schema=False)


@ROUTER.get("/favicon.ico")
async def favicon():
    return FileResponse(f"{APPLICATION_PATH}/static/favicon.ico")


@ROUTER.get("/", response_class=HTMLResponse)
def main():
    return Index(CONFIG, DB).display()


@ROUTER.get("/usage_point_id/{usage_point_id}", response_class=HTMLResponse)
@ROUTER.get("/usage_point_id/{usage_point_id}/", response_class=HTMLResponse)
def usage_point_id(usage_point_id):
    return UsagePoint(usage_point_id).display()


@ROUTER.get("/datatable/{usage_point_id}/{measurement_direction}")
@ROUTER.get("/datatable/{usage_point_id}/{measurement_direction}/")
def datatable(request: Request, usage_point_id, measurement_direction):
    return Ajax(usage_point_id).datatable(measurement_direction, request)


# ########################################################################################################################
# # SWAGGER
# @ROUTER.get(f"/swagger", response_class=HTMLResponse, include_in_schema=False)
# def swagger():
#     data = '<object style="background-color: #FFFFFF; width: 100%; height: 100%" data="/docs"/>'
#     html_content = html_return_fullscreen(body=data, footer_type="consent")
#     return html_content
#
#
# ########################################################################################################################
# # REDOC
# @ROUTER.get(f"/redocs", response_class=HTMLResponse, include_in_schema=False)
# def swagger():
#     data = '<object style="background-color: #FFFFFF; width: 100%; height: 100%" data="/redoc"/>'
#     html_content = html_return_fullscreen(body=data, footer_type="consent")
#     return html_content
#
# from jinja2 import Template
# def html_return_fullscreen(body, footer_type="donation"):
#     with open(f'/app/templates/html/index.html') as file_:
#         index_template = Template(file_.read())
#     html = index_template.render(
#         body=body,
#         )
#     return html
