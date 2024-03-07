"""
This is the startup file for Python Package Manager

(c) tankalxat34
"""

import os

from utils.cli.main import Cli, Prefix
from utils.constants import PPM_CLI_TITLE
import utils.config


if __name__ == "__main__":
    os.system("cls")
    print(PPM_CLI_TITLE)
    while True:
        cli = Cli(input(">>>"))
        try:
            if len(cli.arguments):
                resp = utils.config.CLI_CONFIG[cli.command][cli.arguments[0]](cli)
                if resp:
                    Cli.stdout(resp, prefix=Prefix.INFO)
            else:
                resp = utils.config.CLI_CONFIG[cli.command](cli)
                if resp:
                    Cli.stdout(resp, prefix=Prefix.INFO)

        except Exception as error:
            # print(error.with_traceback())
            Cli.stdout(str(error), prefix=Prefix.ERROR)

        print()
