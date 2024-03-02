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
