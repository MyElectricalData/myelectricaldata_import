"""Configuration file for myelectricaldata."""


import pytz

LOG_FORMAT = "%(asctime)s.%(msecs)03d - %(levelname)8s : %(message)s"
LOG_FORMAT_DATE = "%Y-%m-%d %H:%M:%S"

URL = "https://myelectricaldata.fr"
URL_CONFIG_FILE = "https://github.com/MyElectricalData/myelectricaldata_import/blob/main/config.example.yaml"

USAGE_POINT_ID_LENGTH = 14

MAX_IMPORT_TRY = 20
CYCLE_MINIMUN = 3600

DAILY_MAX_DAYS = 1094
DETAIL_MAX_DAYS = 728

TEMPO_BEGIN = 600
TEMPO_END = 2200

# Return code
CODE_200_SUCCESS = 200
CODE_204_NO_CONTENT = 204
CODE_400_BAD_REQUEST = 400
CODE_404_NOT_FOUND = 404
CODE_409_CONFLICT = 409
CODE_403_FORBIDDEN = 403
CODE_422_UNPROCESSABLE_ENTITY = 422
CODE_429_TOO_MANY_REQUEST = 429
CODE_500_INTERNAL_SERVER_ERROR = 500

TIMEZONE = pytz.timezone("Europe/Paris")
TIMEZONE_UTC = pytz.timezone("UTC")
