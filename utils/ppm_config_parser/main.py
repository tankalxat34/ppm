import json
import pathlib
import os
from typing import Any

from utils.cli.main import Cli
from utils.package_parser.main import PackageParser
from utils.package_parser.packaging.requirements import Requirement
from utils.package_parser.main import PackageParser
from .. import constants

REQUIRES_DIST = "requires_dist"
CONFIG_PATH = pathlib.Path(os.getcwd(), constants.PPM_CONFIG_JSON).absolute()


class PpmConfig:
    def __init__(self):
        self.path = CONFIG_PATH
        if not os.path.exists(self.path):
            raise FileNotFoundError(
                f"Config file '{CONFIG_PATH}' was not found on this project. You need to initialize the Python Package Manajer project using command 'ppm init'"
            )

    @staticmethod
    def write_return(func):
        def wrapper(*args, **kwargs):
            resp = func(*args, **kwargs)
            with open(CONFIG_PATH, "w") as file:
                return file.write(json.dumps(resp, indent=2))

        return wrapper

    def read(self) -> dict[str, Any]:
        with open(self.path, "r") as file:
            try:
                return json.load(file)
            except Exception:
                raise SyntaxError("Config file is empty or contains JSON-valid syntax")

    def freeze(self, cli: Cli):
        """Export all dependensies from `ppm.config.json`"""
        PPM_PATH = constants.getSitePath(cli)
        content = self.read()
        resp: str = ""
        if content.get(REQUIRES_DIST):
            for req in content[REQUIRES_DIST]:
                r = Requirement(req)
                resp += f"{r.name}=={''.join(PackageParser(PPM_PATH, constants.convertPackageName(r.name)).getMetadata()['Version'])}\n"

        with open(
            pathlib.Path(os.getcwd(), constants.PPM_REQUIREMENTS_TXT), "w"
        ) as file:
            file.write(resp)

        return resp

    @write_return
    def addRequirement(self, requirement: Requirement):
        content = self.read()
        req = str(requirement)
        if content.get(REQUIRES_DIST) != None:
            if req not in content[REQUIRES_DIST]:
                content[REQUIRES_DIST].append(req)
        else:
            content[REQUIRES_DIST] = [req]
        return content

    @write_return
    def uninstallRequirement(self, requirement: Requirement):
        content = self.read()
        req = str(requirement)
        content[REQUIRES_DIST] = list(
            filter(
                lambda x: constants.convertPackageName(req)
                != constants.convertPackageName(Requirement(x).name),
                content[REQUIRES_DIST],
            )
        )
        return content
