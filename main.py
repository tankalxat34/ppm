"""
This is the startup file for Python Package Manager

(c) tankalxat34
"""

import os

from utils.cli.main import Cli
import utils.config


if __name__ == "__main__":
    os.system("cls")
    print(utils.config.PPM_CLI_TITLE)
    while True:
        cli = Cli(input(">>>"))
        try:
            if len(cli.arguments):
                print(utils.config.CLI_CONFIG[cli.command][cli.arguments[0]](cli))
            else:
                print(utils.config.CLI_CONFIG[cli.command](cli))

        except Exception as error:
            if ("debug" in cli.options):
                print(error.with_traceback())
            else:
                print("[ERROR]", str(error))

        print()
