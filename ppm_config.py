import json
import pathlib
import sys
from site import getusersitepackages


def loadPpmConfig() -> dict:
    content: str
    with open("./ppm.config.json", "r", encoding="utf-8") as config:
        content = config.read()
    return json.loads(content)


USER_PLATFORM: str = sys.platform
USER_VERSION_INFO = sys.version_info

PPM_NAME = "Python Package Manager"
PPM_VERSION = "1.0.0"
PPM_CLI_TITLE = f"""{PPM_NAME} ({PPM_VERSION}) - {USER_PLATFORM} Python {USER_VERSION_INFO.major}.{USER_VERSION_INFO.minor}.{USER_VERSION_INFO.micro}"""

PPM_CONFIG = loadPpmConfig()
PPM_PROJECT_PATH = pathlib.Path(PPM_CONFIG["site-path"]).absolute()
PPM_GLOBAL_PATH = getusersitepackages()
