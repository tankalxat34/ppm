from io import BytesIO
import json
import os
import pathlib
import sys
import zipfile
from site import getusersitepackages

from . import urllib3
from .. import config

PYPI_JSON = "https://pypi.org/pypi/{name}/json"
PYPI_VERSION_JSON = "https://pypi.org/pypi/{name}/{version}/json"


class PyPi:
    def __init__(self, packageName: str) -> None:
        self.pm = urllib3.PoolManager()
        self.name = packageName

        self.json = dict()

    def upackArchive(self, iobytes: BytesIO, path: str | pathlib.Path):
        """Unpack archive that represented as wheel (`*.zip`)"""
        with zipfile.ZipFile(iobytes, "r") as archive:
            for file in archive.namelist():
                archive.extract(file, path)

    def fetch(self):
        """Needs to perform before any action"""
        url = PYPI_JSON.format(name=self.name)
        self.json = json.loads(self.pm.request("GET", url).data)
        return self.json

    def releases(self) -> list[str]:
        """Return the list of existing versions"""
        return list(self.json["releases"].keys())

    def fetchArchive(self, version: str = ""):
        """Return `BytesIO` of archive"""
        parentObj = (
            self.json["urls"] if not version else self.json["releases"].get(version)
        )
        for obj in parentObj:
            if obj["packagetype"] == "bdist_wheel" and "whl" in obj["url"]:
                return BytesIO(self.pm.request("GET", parentObj[0]["url"]).data)
        raise NameError("Link to download wheel not found")

    def setup(self, path: str | pathlib.Path, version: str = ""):
        return self.upackArchive(self.fetchArchive(version), path)


if __name__ == "__main__":
    # print(PPM_PATH)
    pypi = PyPi("numpy")

    pypi.fetch()
    print(pypi.json)
    # print(pypi.fetchArchive())
    pypi.upackArchive(pypi.fetchArchive(), config.PPM_PROJECT_PATH)
