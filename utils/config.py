"""
Python Package Manager
======================

This is the simplest console package manager in Python. 
It uses standard Python dependencies, is easy to install 
and runs on any operating system. With this ppm manager 
you will be able to install, remove and update packages 
obtained from PyPi.org, as well as save information about 
them for the current project in the requirements.txt file 
and, if necessary, duplicate them in a separate configuration 
file ppm.config.json

(с) tankalxat34

All commands:
    - ppm
        - install [--version | --ignore]        download and setup new package
        - uninstall                             remove existing package
        - update                                download and setup actual version
    - exit              exit from ppm
"""

import json
import os
import sys
import pathlib
import shutil
from site import getusersitepackages

from utils.cli.main import Cli
from utils.cli.tui import calculate_bytes_size
from utils.package_parser.main import PackageParser
from utils.pypi_api.main import PyPi


USER_PLATFORM: str = sys.platform
USER_VERSION_INFO = sys.version_info


PPM_NAME = "Python Package Manager"
PPM_VERSION = "1.1.0"
PPM_CLI_TITLE = f"""{PPM_NAME} ({PPM_VERSION}) - {USER_PLATFORM} Python {USER_VERSION_INFO.major}.{USER_VERSION_INFO.minor}.{USER_VERSION_INFO.micro}"""


PPM_PROJECT_PATH = pathlib.Path(os.getcwd(), "python_modules").absolute()
PPM_GLOBAL_PATH = getusersitepackages()


def loadPpmConfig() -> dict:
    content: str
    with open("./ppm.config.json", "r", encoding="utf-8") as config:
        content = config.read()
    return json.loads(content)


def getSitePath(cli: Cli) -> str | pathlib.Path:
    """Returns path to `site-packages` dir when alias `-g` in CLI command"""
    return PPM_GLOBAL_PATH if ("g" in cli.aliases) else PPM_PROJECT_PATH


def install(cli: Cli):
    PPM_PATH = getSitePath(cli)
    packages = cli.arguments[1:]
    installedPackages: list[str] = []

    for pack in packages:
        if "@" in pack:
            package, version = pack.split("@")[0], pack.split("@")[1]
        else:
            package, version = pack, ""

        try:
            if PackageParser(PPM_PATH, package).isInstalled():
                print(
                    f"  Package '{package}' has been skipped because it also installed"
                )
                continue
        except Exception:
            pass

        print(f"Collecting '{package}'")
        pypi = PyPi(package, version)
        pypi.fetch()

        print(f"  Installing '{package}' ({pypi.json['info']['version']})")

        archive = pypi.fetchArchive()
        archiveSize = calculate_bytes_size(archive)
        print(f"  Package size is {(archiveSize)[0]}{archiveSize[1]}")

        pypi.upackArchive(archive, PPM_PATH)

        installedPackages.append(package + version)
        print(f"  Successfully unpacked to '{PPM_PATH}'")

    return f"Complete installing packages: {' '.join(installedPackages)}"


def uninstall(cli: Cli):
    PPM_PATH = getSitePath(cli)
    packages = cli.arguments[1:]
    for package in packages:
        packageParser = PackageParser(PPM_PATH, package)

        distinfo = packageParser.getDistInfo()
        record = packageParser.getRecord()
        metadata = packageParser.getMetadata()

        for file in record:
            pathlib.Path(PPM_PATH, file["path"]).absolute().unlink()

        shutil.rmtree(pathlib.Path(PPM_PATH, distinfo).absolute())
        try:
            shutil.rmtree(pathlib.Path(PPM_PATH, package).absolute())
        except Exception:
            pass

        print(
            f"  Package '{package}' ({''.join(metadata['Version'])}) successfully deleted"
        )

    return f"Successfully uninstalled {' '.join(packages)}"


def view(cli: Cli):
    PPM_PATH = getSitePath(cli)
    KEYS = ["Name", "Version", "Summary", "Home-page", "Author", "Author-email"]
    if len(cli.arguments) >= 2:
        package = cli.arguments[1]
        packageParser = PackageParser(PPM_PATH, package)

        distinfo = packageParser.getDistInfo()
        record = packageParser.getRecord()
        metadata = packageParser.getMetadata()

        result: str = ""

        for key in KEYS:
            try:
                result += f"{key}: {''.join(metadata[key])}\n"
            except Exception:
                pass

        return result
    else:
        listdir = os.listdir(PPM_PATH)
        return (
            "\n".join(listdir) + f"\n" + "-" * 15 + f"\nTotal packages: {len(listdir)}"
        )


def update(cli: Cli):
    PPM_PATH = getSitePath(cli)
    packages = cli.arguments[1:]

    print(f"Updating packages {' '.join(packages)}")

    uninstall(cli)
    install(cli)

    return f"Successfully updated packages: {' '.join(packages)}"


CLI_CONFIG = {
    # command
    "ppm": {
        # arguments
        "install": lambda cli: install(cli),
        "uninstall": lambda cli: uninstall(cli),
        "update": lambda cli: update(cli),
        "view": lambda cli: view(cli),
        "help": lambda cli: __doc__,
        "config": lambda cli: f"""{PPM_NAME}
Version: {PPM_VERSION}
Global site-path: {PPM_GLOBAL_PATH}
Project site-path: {PPM_PROJECT_PATH}
""",
    },
    "exit": lambda cli: quit(),
}
