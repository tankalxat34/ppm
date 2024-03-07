from utils.cli.main import Cli, Options, Prefix


def handle_KeyboardInterrupt(func):
    """Handle `KeyboardInterrupt` for `func` to safe break executing `func`"""

    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except KeyboardInterrupt:
            Cli.stdout("Action has been cancelled", prefix=Prefix.INFO)

    return wrapper


def handle_AskBeforeStart(func):
    def wrapper(*args, **kwargs):
        if (
            Cli.stdin(
                "This action carries serious consequences. Do you wish to continue?",
                Options.NOYES,
                errorIfUnknownOption=True,
            )
            == "y"
        ):
            return func(*args, **kwargs)
        else:
            Cli.stdout("Action has been cancelled", prefix=Prefix.INFO)

    return wrapper
