import faulthandler

from typing import Optional, Literal

from . import _LOG


class FHContext:
    def __init__(self) -> None:
        self._log_file = _LOG

    def __enter__(self) -> "FHContext":  # noqa: PYI034
        faulthandler.enable(self._log_file)
        return self

    def __exit__(
        self,
        exc_type: Optional[type[BaseException]],
        exc_value: Optional[BaseException],
        traceback: object,
    ) -> Literal[False]:
        faulthandler.disable()
        self._log_file.flush()
        self._log_file.close()
        return False
