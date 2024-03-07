def handle_KeyboardInterrupt(func):
    """Handle `KeyboardInterrupt` for `func` to safe break executing `func`"""

    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except KeyboardInterrupt:
            print("^C")

    return wrapper
