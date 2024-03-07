import os
import pathlib
import sys
from site import getusersitepackages

from utils.cli.main import Cli

USER_PLATFORM: str = sys.platform
USER_VERSION_INFO = sys.version_info

PPM_NAME = "Python Package Manager"
PPM_VERSION = "1.3.0"
PPM_CLI_TITLE = f"""{PPM_NAME} ({PPM_VERSION}) - {USER_PLATFORM} Python {USER_VERSION_INFO.major}.{USER_VERSION_INFO.minor}.{USER_VERSION_INFO.micro}"""

PPM_DEFAULT_VENV_DIR_NAME = "venv"
PPM_CREATE_VENV_CMD = f"python -m venv {PPM_DEFAULT_VENV_DIR_NAME}"
PPM_CONFIG_JSON = "ppm.config.json"
PPM_REQUIREMENTS_TXT = "requirements.txt"
PPM_VENV_PATH = pathlib.Path(
    os.getcwd(), PPM_DEFAULT_VENV_DIR_NAME, "lib", "site-packages"
).absolute()
PPM_PROJECT_PATH = (
    pathlib.Path(os.getcwd(), "python_modules").absolute()
    if not os.path.exists(PPM_VENV_PATH)
    else PPM_VENV_PATH
)
PPM_GLOBAL_PATH = getusersitepackages()


def getSitePath(cli: Cli) -> str | pathlib.Path:
    """Returns path to `site-packages` dir when alias `-g` in CLI command"""
    return PPM_GLOBAL_PATH if ("g" in cli.aliases) else PPM_PROJECT_PATH


def convertPackageName(name: str):
    REPLACE_MASK = {"-": "_"}
    for frm, t in REPLACE_MASK.items():
        result = name.replace(frm, t)
    return result
