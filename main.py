"""
This is the startup file for Python Package Manager

(c) tankalxat34
"""

import os

from cli.main import Cli
from cli_config import CLI_CONFIG
from ppm_config import PPM_CLI_TITLE


if __name__ == "__main__":
    os.system("cls")
    print(PPM_CLI_TITLE)
    while True:
        cli = Cli(input(">>>"))
        try:
            if len(cli.arguments):
                print(CLI_CONFIG[cli.command][cli.arguments[0]](cli))
            else:
                print(CLI_CONFIG[cli.command](cli))

        except Exception as error:
            print(
                f"[ERROR] An unknown command '{cli.cmd}' or a command was executed with an error. See the logs below:",
            )
            print(error)

        print()
