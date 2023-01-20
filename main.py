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

production = False
test = False
if "env" in PARAMS and PARAMS["env"] == "production":
    production = True
if "env" in PARAMS and PARAMS["env"] == "test":
    test = True

if __name__ == "__main__":
    if ACTION == "wizard":
        wizard()
    elif ACTION == "run":
        if production:
            run()
        if test:
            run(test=True)
        else:
            run(dev=True)
    elif ACTION == "debug":
        run(debug=True)
    elif ACTION == "create_release":
        create_release()
