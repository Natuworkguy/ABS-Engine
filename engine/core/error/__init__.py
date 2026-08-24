import faulthandler
import os


class ABSFatalError(RuntimeError):
    def __init__(self, message: str) -> None:
        super().__init__(message)

        print(f"ABS Engine hit a fatal exception: {message}\n")

        faulthandler.enable()
        os.abort()
        faulthandler.disable()
