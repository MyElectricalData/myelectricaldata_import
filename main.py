import sys

from dependencies import *

from app.models.log import Log

del sys.argv[0]
PARAMS = {}
for arg in sys.argv:
    PARAMS[arg.split("=")[0]] = arg.split("=")[1]

ACTION = PARAMS["action"]
APPLICATION_PATH = "app"

LOG = Log()

if __name__ == "__main__":
    if ACTION == "wizard":
        wizard()
    elif ACTION == "run":
        run()
        # run()
    elif ACTION == "debug":
        run(debug=True)
    elif ACTION == "create_pre_release":
        create_release("preprod")
    elif ACTION == "create_release":
        create_release()
        