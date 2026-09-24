# Copyright (C) Natuworkguy
# See the LICENSE file for GPLv3

"""
C integration utilities for the engine.
"""

import importlib
import sys

import cffi

from functools import cache
from types import ModuleType
from typing import Final, Any
from pathlib import Path

from ..logger import logger, Status
from . import _ENGINE_DIR

C_DIR: Final[Path] = _ENGINE_DIR / "c"
BUILD_DIR: Final[Path] = C_DIR / "build"

INSTALL_HINT: Final[str] = (
    "Install one:\n"
    "  macOS          xcode-select --install\n"
    "  Debian, Ubuntu sudo apt install build-essential\n"
    "  Fedora         sudo dnf install gcc\n"
    "  Windows        the Visual Studio Build Tools, with the C++ workload\n"
    "Or set CC to a compiler that is already installed somewhere else."
)

if not C_DIR.exists() or not C_DIR.is_dir():
    logger("Could not find engine/c/ directory.", status=Status.CRITICAL)
    sys.exit(1)


class CompilerNotFoundError(RuntimeError):
    """
    There is no C compiler on this machine to build engine/c/ with.
    """


class CModule:
    """
    A compiled C file, with the functions it exposes reachable as attributes.
    """

    ffi: cffi.FFI
    lib: Any

    def __init__(self, source_name: str, module: ModuleType) -> None:
        """
        Wrap the module cffi compiled for a C file.

        Args:
            source_name (str): file in engine/c/ the module was compiled from
            module (ModuleType): Module cffi produced for that file.
        """

        self.source_name = source_name
        self.ffi = module.ffi
        self.lib = module.lib

    def __getattr__(self, name: str) -> Any:
        """
        Get a function or constant from the compiled C.

        Args:
            name (str): Name the C file's header declares.

        Returns:
            Any: The function or constant it names.

        Raises:
            AttributeError: If the header declares no such name.
        """

        try:
            return getattr(self.lib, name)
        except AttributeError:
            raise AttributeError(f"Could not find {name} in {self.source_name}.") from None

    def __repr__(self) -> str:
        """
        Return a developer-friendly representation of the compiled C file.

        Returns:
            str: Debug representation of the module.
        """

        return f"<{self.__class__.__name__} of {self.source_name}>"


def _build(module_name: str, source_path: Path, header_path: Path) -> None:
    """
    Compile a C file into an extension module under engine/c/build/

    Args:
        module_name (str): Name to give the compiled module.
        source_path (Path): C file to compile.
        header_path (Path): Header declaring what the C file exposes.

    Raises:
        CompilerNotFoundError: If the file would not build, which on a
            machine with no C compiler installed is every time.
    """

    ffibuilder = cffi.FFI()

    ffibuilder.cdef(header_path.read_text(encoding="utf-8"))
    ffibuilder.set_source(
        module_name,
        source_path.read_text(encoding="utf-8"),
        include_dirs=[str(C_DIR)],
        libraries=[] if sys.platform == "win32" else ["m"],
    )

    try:
        ffibuilder.compile(tmpdir=str(BUILD_DIR))
    except cffi.VerificationError as e:
        raise CompilerNotFoundError(
            f"Could not build {source_path.name}, which usually means there is no "
            f"C compiler installed.\n\n{INSTALL_HINT}\n\n{e}"
        ) from e


@cache
def c_source(source_name: str) -> CModule:
    """
    Compile and load a C file from engine/c/

    The file needs a header of the same name holding its prototypes. cffi reads
    that header to learn what Python may call, so it holds declarations only,
    with no includes and no include guards.

    The file is compiled every time a process first asks for it, and the result
    is held, so later calls return the same already built module. Compiling
    needs a C compiler installed, and raises :class:`engine.loaders.c_loader.CompilerNotFoundError`
    when there is none.

    Args:
        source_name (str): file in engine/c/ to compile

    Returns:
        CModule: The compiled C file, with its functions as attributes.

    Raises:
        FileNotFoundError: If no such source or header exists under engine/c/.
        IsADirectoryError: If the path names a directory rather than a file.
        ModuleNotFoundError: If the compiled module cannot be imported, which
            usually means engine/c/build/ holds a module built by a different
            Python than the one running now.
    """

    source_path = C_DIR / source_name

    if not source_path.exists():
        raise FileNotFoundError(f"Could not find C file {source_path}.")

    if source_path.is_dir():
        raise IsADirectoryError(f"{source_path}: Invalid script path (Is a directory)")

    header_path = source_path.with_suffix(".h")

    if not header_path.exists():
        raise FileNotFoundError(f"Could not find C header {header_path}.")

    module_name = f"_{source_path.stem}_cffi"

    _build(module_name, source_path, header_path)

    if str(BUILD_DIR) not in sys.path:
        sys.path.insert(0, str(BUILD_DIR))

    try:
        module = importlib.import_module(module_name)
    except ModuleNotFoundError as e:
        raise ModuleNotFoundError(
            f"Compiled {source_name}, but {module_name} could not be imported from "
            f"{BUILD_DIR}. Delete that directory to build it again."
        ) from e

    return CModule(source_name, module)


def c_call_function(source_name: str, function_name: str, *args: Any) -> Any:
    """
    Call a C function from a file in engine/c/ with arguments and return result

    Example:
        result = c_call_function("geometry.c", "distance", 0.0, 0.0, 3.0, 4.0)

    Args:
        source_name (str): file in engine/c/ holding the function
        function_name (str): function to call
        *args (Any): Arguments passed to the C function.

    Returns:
        Any: Result of the function
    """

    return getattr(c_source(source_name), function_name)(*args)
