from io import BytesIO
import sys


BYTES = 1
KB = 1024
MB = 1024 * 1024
GB = 1024 * 1024 * 1024


def calculate_bytes_size(iobytes: BytesIO):
    """Return `tuple` with rounded float number at first and humanized string at second"""
    size = sys.getsizeof(iobytes)
    if size / BYTES <= BYTES:
        return (round(size / BYTES, 1), " BYTES")
    if size / KB <= KB:
        return (round(size / KB, 1), " KB")
    if size / MB <= MB:
        return (round(size / MB, 1), " MB")
    if size / GB <= GB:
        return (round(size / GB, 1), " GB")
    return (0, " BYTES")


class TextTable:
    def __init__(self, dataframe: dict | list) -> None:
        self.df = dataframe

    def log(self) -> None:
        pass


if __name__ == "__main__":
    # from .. import cli_config
    from site import getusersitepackages
    import os

    PACKAGES: list = []

    PPM_GLOBAL_PATH = getusersitepackages()

    print(os.listdir(PPM_GLOBAL_PATH))
