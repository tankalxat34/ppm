"""
This is a part of Python Package Managger

This package needs to parse information from files in `*.dist-info` dir

(c) tankalxat34
"""

import json
import re
import sys
import os
import pathlib


class PackageParser:
    def __init__(self, sitePath: str | pathlib.Path, packageName: str) -> None:
        self.packageName = packageName
        self.path = sitePath

    def _readAsMetadataSyntax(self, filename: str):
        content: str
        with open(
            pathlib.Path(self.path, self.getDistInfo(), filename),
            "r",
            encoding="utf-8",
        ) as file:
            content = file.read()
        keyvalues = re.findall(r"^(\w\S+): *(.+)$", content, re.MULTILINE)

        result: dict[str, list[str]] = {}

        for t in keyvalues:
            key, value = t
            try:
                result[key].append(value)
            except Exception:
                result[key] = [value]

        return result

    def getDistInfo(self):
        dirlist = os.listdir(self.path)

        for dirname in dirlist:
            if (
                self.packageName == dirname.lower().split("-")[0]
                and ".dist-info" in dirname.lower()
            ):
                return dirname
        raise NameError(
            f"You have not installed package with name '{self.packageName}'"
        )

    def getRecord(self):
        """Returns parsed content from file `*.dist-info/RECORD`"""

        def _parse(line: str):
            path, sha256, size = line.strip().split(",")
            return {"path": path, "sha256": sha256, "size": size}

        content: list
        with open(
            pathlib.Path(self.path, self.getDistInfo(), "RECORD"),
            "r",
            encoding="utf-8",
        ) as file:
            content = file.readlines()
        return list(map(_parse, content))

    def getMetadata(self):
        """Returns parsed content from file `*.dist-info/METADATA`"""
        return self._readAsMetadataSyntax("METADATA")

    def getWheel(self):
        """Returns parsed content from file `*.dist-info/WHEEL`"""
        return self._readAsMetadataSyntax("WHEEL")

    def isInstalled(self) -> bool:
        """Return `True` if package is installed"""
        return os.path.exists(pathlib.Path(self.path, self.getDistInfo()))


"""
pkginfo
PasteDeploy
zope.interface (>3.5.0)
pywin32 >1.0; sys_platform == 'win32'
brotli>=1.0.9; (platform_python_implementation == 'CPython') and extra == 'brotli'
brotlicffi>=0.8.0; (platform_python_implementation != 'CPython') and extra == 'brotli'
h2<5,>=4; extra == 'h2'
pysocks!=1.5.7,<2.0,>=1.5.6; extra == 'socks'
zstandard>=0.18.0; extra == 'zstd'
"""


class Requirement:
    def __init__(self, requirementString: str) -> None:
        self.reqStr = requirementString

        self.name = re.match(r"\w[a-zA-Z0-9]+", self.reqStr)
        print(self.name.span())

    def __str__(self) -> str:
        return str(self.__dict__)


if __name__ == "__main__":
    from packaging.requirements import Requirement as Req
    from packaging.version import Version

    req = Requirement("pysocks[all, pdf]!=1.5.7,<2.0,>=1.5.6; extra == 'socks'")
    print(req)

    # req = Req("pysocks[all, pdf]!=1.5.7,<2.0,>=1.5.6; extra == 'socks'")
    # print(f"{req.extras = }")
    # print(f"{req.marker = }")
    # print(f"{req.name = }")
    # print(f"{req.specifier = }")
    # print(f"{req.url = }")

    # ver = Version("1.0.9")
    # ver2 = Version("1.1.12")
    # print(ver.dev)
