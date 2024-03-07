import pathlib
import os

from utils.package_parser.packaging.requirements import Requirement

class PpmConfig:
    def __init__(self, projectPath: str = os.getcwd()):
        self.path = pathlib.Path(projectPath, "ppm.config.json").absolute()

    def _read(self):
        pass

    def addRequirement(self, requirement: str | Requirement):
        pass