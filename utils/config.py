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
"""

import json
import os
import sys
import pathlib
import shutil
from site import getusersitepackages
from getpass import getuser
from utils.constants import (
    PPM_CONFIG_JSON,
    PPM_CREATE_VENV_CMD,
    PPM_GLOBAL_PATH,
    PPM_NAME,
    PPM_PROJECT_PATH,
    PPM_VENV_PATH,
    PPM_VERSION,
    convertPackageName,
    getSitePath,
)

from utils.ppm_config_parser.main import REQUIRES_DIST, PpmConfig
from utils.pypi_api.main import PyPi
from utils.cli.main import Cli, Options, Prefix
from utils.cli.tui import calculate_bytes_size
from utils.package_parser.main import PackageParser
from utils.package_parser.packaging.requirements import Requirement
from utils.decorators.handlers import handle_AskBeforeStart, handle_KeyboardInterrupt


def loadPpmConfig() -> dict:
    content: str
    with open(f"./{PPM_CONFIG_JSON}", "r", encoding="utf-8") as config:
        content = config.read()
    return json.loads(content)


def print_dict_with_indent(d, indent=0):
    for key, value in d.items():
        if isinstance(value, dict):
            print(" " * indent + str(key) + ":")
            print_dict_with_indent(value, indent + 2)
        else:
            print(" " * indent + str(key) + ": " + str(value))


def getInstalledPackages(cli: Cli) -> list[str]:
    PPM_PATH = getSitePath(cli)

    listdir = os.listdir(PPM_PATH)
    out_filter = list(
        map(
            lambda x: x.split("-")[0],
            filter(lambda x: ".dist-info" in x, listdir),
        )
    )
    return out_filter


def install(cli: Cli, _installedPackages: list[str] = []):
    PPM_PATH = getSitePath(cli)
    CONFIG = PpmConfig()
    packages = cli.arguments[1:]

    if not len(packages):
        config_content = CONFIG.read()
        joinedAliases = "-" + " -".join(cli.aliases)
        requires_dist_cmd = (
            f"ppm install {joinedAliases} {' '.join(config_content[REQUIRES_DIST])}"
        )
        return install(
            Cli(requires_dist_cmd),
            _installedPackages,
        )

    for position, pack in enumerate(packages):
        requirement = Requirement(pack.replace(";", ""))
        package = requirement.name

        try:
            if PackageParser(
                PPM_PATH, convertPackageName(package.lower())
            ).isInstalled():
                Cli.stdout(
                    f"Package '{package}' has been skipped because it's installed before",
                    prefix=Prefix.INFO,
                )
                continue
        except Exception:
            pass

        Cli.stdout(f"Collecting '{requirement}'")
        pypi = PyPi(package)
        pypi.fetch()
        releases = pypi.releases()

        version: str = pypi.json["info"]["version"]
        if not requirement.specifier.contains(version):
            for release in releases[::-1]:
                if requirement.specifier.contains(release):
                    version = release
                    break

        Cli.stdout(f"Installing {package}=={version}", level=1)

        archive = pypi.fetchArchive(version)
        archiveSize = calculate_bytes_size(archive)
        Cli.stdout(f"Package size is {(archiveSize)[0]}{archiveSize[1]}", level=1)

        pypi.upackArchive(archive, PPM_PATH)

        Cli.stdout(f"Successfully unpacked to '{PPM_PATH}'", level=1)
        _installedPackages.append(package + "-" + str(version))

        if "no-strict-req" in cli.options:
            CONFIG.addRequirement(requirement)
        else:
            CONFIG.addRequirement(Requirement(f"{package}=={str(version)}"))

        if pypi.json["info"]["requires_dist"] and (
            "no-deps" not in tuple(cli.options.keys())
        ):
            for req_dist in pypi.json["info"]["requires_dist"]:
                child_requirement = Requirement(req_dist)

                if (not bool(child_requirement.marker)) or (
                    child_requirement.marker
                    and child_requirement.marker.evaluate(
                        {"extra": list(requirement.extras)[0]}
                        if requirement.extras
                        else None
                    )
                ):
                    try:
                        joinedAliases = "-" + " -".join(cli.aliases)
                        requires_dist_cmd = (
                            f"ppm install {joinedAliases} {req_dist.replace(' ', '')}"
                        )
                        install(
                            Cli(requires_dist_cmd),
                            _installedPackages,
                        )
                    except Exception:
                        pass

    return (
        f"Complete installing packages: {' '.join(set(_installedPackages))}"
        if len(_installedPackages)
        else ""
    )


def uninstall(cli: Cli):
    PPM_PATH = getSitePath(cli)
    CONFIG = PpmConfig()
    ui_packages = cli.arguments[1:]
    packages = tuple(map(lambda x: convertPackageName(x), cli.arguments[1:]))

    if not len(packages):
        raise NameError("You does not provide package names")

    for i, package in enumerate(packages):
        packageParser = PackageParser(PPM_PATH, package)

        CONFIG.uninstallRequirement(Requirement(package))

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

        Cli.stdout(
            f"Package {ui_packages[i]}=={''.join(metadata['Version'])} successfully deleted",
            level=0,
        )

    return f"Successfully uninstalled {' '.join(ui_packages)}"


def view(cli: Cli):
    PPM_PATH = getSitePath(cli)
    KEYS = [
        "Name",
        "Version",
        "Summary",
        "Home-page",
        "Author",
        "Author-email",
    ]
    if len(cli.arguments) >= 2:
        package = convertPackageName(cli.arguments[1])
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

        return result + f"Installed to: {pathlib.Path(PPM_PATH, package)}"
    else:
        out_filter = getInstalledPackages(cli)
        return (
            "\n".join(out_filter)
            + f"\n"
            + "-" * 15
            + f"\nTotal packages: {len(out_filter)}"
        )


def upgrade(cli: Cli):
    PPM_PATH = getSitePath(cli)
    packages = tuple(map(lambda name: convertPackageName(name), cli.arguments[1:]))

    if not len(packages):
        raise NameError("You does not provide package names")

    Cli.stdout(f"Updating packages {' '.join(packages)}")

    uninstall(cli)
    install(cli)

    return f"Successfully updated packages: {' '.join(packages)}"


def releases(cli: Cli):
    pypi = PyPi(cli.arguments[1])
    pypi.fetch()
    releases = pypi.releases()

    return "\n".join(releases)


def _createVenv(cli: Cli):
    Cli.stdout(
        f"Creating virtual environment using command '{PPM_CREATE_VENV_CMD}'",
        level=1,
    )
    os.system(PPM_CREATE_VENV_CMD)
    Cli.stdout(f"Virtual environment created at '{PPM_VENV_PATH}'", level=1)


@handle_KeyboardInterrupt
def initialize(cli: Cli):
    PPM_PATH = getSitePath(cli)
    yesStatus = "y" in cli.aliases or "yes" in cli.options

    if os.path.exists(PPM_CONFIG_JSON):
        userInputReinitProject = Cli.stdin(
            "You have completed `ppm.config.json` for this project. You want to reinitialize it?",
            Options.NOYES,
            errorIfUnknownOption=True,
        )
        if userInputReinitProject == "n":
            return "Cancelled reinitialisation of the PPM project"

    if not os.path.exists(PPM_VENV_PATH):
        userInputSetupVenv = Cli.stdin(
            "Would you like to setup Python venv?",
            Options.YESNO,
            errorIfUnknownOption=True,
        )
        if userInputSetupVenv == "y":
            _createVenv(cli)

    userResp = {
        "name": Cli.stdin(
            "Project name", [os.path.basename(os.getcwd())], useDefault=yesStatus
        ),
        "version": Cli.stdin("Version", ["1.0.0"], useDefault=yesStatus),
        "main": Cli.stdin("Main script", ["main.py"], useDefault=yesStatus),
        "summary": Cli.stdin("Summary", [""], useDefault=yesStatus),
        "keywords": Cli.stdin("Keywords", [""], useDefault=yesStatus),
        "author": Cli.stdin(
            "Author",
            [getuser() or "Unnamed Author <unnamed@email.com>"],
            useDefault=yesStatus,
        ),
        "license": Cli.stdin("License", ["ISC"], useDefault=yesStatus),
    }

    with open(PPM_CONFIG_JSON, "w") as config:
        config.write(json.dumps(userResp, indent=2))
    return f"Created {PPM_CONFIG_JSON} with content:\n" + json.dumps(userResp, indent=2)


def freeze(cli: Cli):
    CONFIG = PpmConfig()
    return CONFIG.freeze(cli)


@handle_AskBeforeStart
def makedeps(cli: Cli):
    PPM_PATH = getSitePath(cli)
    CONFIG = PpmConfig()

    installed_packages = getInstalledPackages(cli)
    for pack in installed_packages:
        CONFIG.addRequirement(Requirement(pack))

    return (
        f"All installed packages has been added to `ppm.config.json` from '{PPM_PATH}'"
    )


CLI_CONFIG = {
    # command
    "ppm": {
        # arguments
        "install": lambda cli: install(cli, []),
        "uninstall": lambda cli: uninstall(cli),
        "upgrade": lambda cli: upgrade(cli),
        "view": lambda cli: view(cli),
        "releases": lambda cli: releases(cli),
        "init": lambda cli: initialize(cli),
        "freeze": lambda cli: freeze(cli),
        "makedeps": lambda cli: makedeps(cli),
        "help": lambda cli: __doc__,
        "config": lambda cli: f"""{PPM_NAME}
Version: {PPM_VERSION}
Global site-path: {PPM_GLOBAL_PATH}
Project site-path: {PPM_PROJECT_PATH}
""",
    },
    "exit": lambda cli: quit(),
}
