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
        """Returns parsed content from file `*.dist-info/METADATA`

        [About METADATA](https://packaging.python.org/en/latest/specifications/core-metadata/)
        """
        return self._readAsMetadataSyntax("METADATA")

    def getWheel(self):
        """Returns parsed content from file `*.dist-info/WHEEL`"""
        return self._readAsMetadataSyntax("WHEEL")

    def isInstalled(self) -> bool:
        """Return `True` if package is installed"""
        return os.path.exists(pathlib.Path(self.path, self.getDistInfo().lower()))


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


if __name__ == "__main__":
    from packaging.requirements import Requirement as Req
    from packaging.version import Version
    from packaging.markers import Marker
    from packaging.specifiers import Specifier

    reqStr = "ujson[all]!=4.0.2,!=4.1.0,!=4.2.0,!=4.3.0,!=5.0.0,!=5.1.0,>=4.0.1; extra == 'all'"
    # reqStr = "email-validator>=2.0.0; extra == 'all'"
    # reqStr = "pydantic!=1.8,!=1.8.1,!=2.0.0,!=2.0.1,!=2.1.0,<3.0.0,>=1.7.4"
    # reqStr = "requests~=0.1.2"

    req = Req(reqStr)
    print(f"{req.extras = }", "all" in req.extras)
    print(f"{req.marker = }")
    print(f"{req.name = }")
    print(f"{req.specifier = }")
    print(f"{req.url = }")

    # print(req.marker.evaluate())
    # print(*req.specifier.filter(["0.2.0", "0.9.1"]))
    # print(req.specifier.contains("0.2.23"))
    print(f"{req.marker and req.marker.evaluate() = }")
    print(req.marker)

    # marker = Marker("extra == 'bar'")
    # print(marker.evaluate({"extra": "bar"}))

    # ver = Version("1.0.9")
    # ver2 = Version("1.1.12")
    # print(ver.dev)
