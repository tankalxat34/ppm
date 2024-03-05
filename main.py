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
            print(
                f"[ERROR] An unknown command '{cli.cmd}' or a command was executed with an error. See the logs below:",
            )
            print(str(error))
            # print(error.with_traceback())

        print()
