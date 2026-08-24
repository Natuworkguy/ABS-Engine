import time
import tkinter
import os
import tempfile

from pathlib import Path
from multiprocessing import Process

_LOG_FILE: Path = Path(tempfile.NamedTemporaryFile(mode="w+", delete=False, prefix="abs-traceback-").name)  # noqa: SIM115
_LOG = _LOG_FILE.open("a", encoding="utf-8")
print(_LOG_FILE)


class ABSFatalError(RuntimeError):
    def __init__(self, message: str) -> None:
        super().__init__(message)

        with _LOG_FILE.open("a", encoding="utf-8") as f:
            f.write(f"ABS Engine hit a fatal exception: {message}\n")
            f.close()
        Process(target=tkinter.Tk().mainloop()).start()
        time.sleep(1.5)
        os.abort()
