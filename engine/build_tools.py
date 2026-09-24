# Copyright (C) Natuworkguy
# See the LICENSE file for GPLv3

"""
Build and development utilities for the engine.
"""

import os
import shutil
import stat
import sys
import time
from multiprocessing import Process, Queue

from tkinter import messagebox
from pathlib import Path
from typing import Optional, Tuple, Any, Union

from .saveload import resource_path
from . import logger

engine_path = Path(__file__).parent


class _QueueWriter:
    """A writable stream that forwards each written line to a Queue."""

    def __init__(self, log_queue: "Queue[Optional[str]]") -> None:
        """
        Wrap a queue in a writable stream.

        Args:
            log_queue (Queue[Optional[str]]): Queue that receives each completed line.
        """

        self._queue = log_queue
        self._buffer = ""

    def write(self, text: str) -> int:
        """
        Buffer text, forwarding each line to the queue once it is complete.

        Args:
            text (str): Text written to the stream.

        Returns:
            int: Number of characters written, as a writable stream is expected to report.
        """

        self._buffer += text

        while "\n" in self._buffer:
            line, self._buffer = self._buffer.split("\n", 1)
            self._queue.put(line)

        return len(text)

    def flush(self) -> None:
        """
        Do nothing. Lines reach the queue as soon as they complete, so nothing
        is ever held back waiting to be flushed.
        """


def _clear_readonly(path: Any) -> None:
    """
    Clear a path's read-only bit and retry the removal that failed on it.

    Args:
        path (Any): Path that could not be removed.
    """

    os.chmod(path, stat.S_IWRITE)


def _remove_previous_build(path: Path, retries: int = 5, delay: float = 0.5) -> None:
    """
    Delete a previous build directory, waiting out any lock still held on it.

    A build that has only just finished can keep files open for a moment, so a
    PermissionError is retried rather than treated as fatal straight away.

    Args:
        path (Path): Build directory to remove. A missing path is ignored.
        retries (int): How many removal attempts to make. Defaults to 5.
        delay (float): Seconds to wait between attempts. Defaults to 0.5.

    Raises:
        PermissionError: If the directory is still locked after the final attempt.
    """

    if not path.exists():
        return

    for attempt in range(retries):
        try:
            shutil.rmtree(path)
            return
        except PermissionError:
            if attempt == retries - 1:
                raise
            time.sleep(delay)
        except (FileNotFoundError, FileExistsError) as e:
            messagebox.showerror("Error", f"{e.__class__.__name__}: {e!s}")
            sys.exit(1)
        except Exception:
            _clear_readonly(path)
            continue


def _build_pyinstaller(
    name: str, directory: Path, log_queue: "Queue[Optional[str]]", autoadd: list[Union[str, Path]]
) -> None:
    """
    Run PyInstaller over a prepared project directory, reporting progress.

    Meant to run in its own process, since it replaces the process-wide output
    streams. A None item is put on the queue once the build ends, however it
    ends, so a reader knows no more output is coming.

    Args:
        name (str): Name to give the built executable.
        directory (Path): Project directory holding game.absp and run.py.
        log_queue (Queue[str | None]): Queue that receives PyInstaller's output.
        autoadd (list[str | Path]): Directories to automatically add to the build, if they exist.
    """

    sys.stdout = _QueueWriter(log_queue)
    sys.stderr = _QueueWriter(log_queue)

    from PyInstaller.__main__ import run as pyinstaller

    try:
        _remove_previous_build(directory / "dist" / name)

        pyi_args = [
            "--onedir",
            "--noconsole",
            "--noconfirm",
            "--name",
            name,
            "--distpath",
            str(directory / "dist"),
            "--workpath",
            str(directory / "build"),
            "--specpath",
            str(directory),
            f"--add-data={directory / 'game.absp'!s}{os.pathsep}.",
            f"--add-data={directory / 'engine' / 'nut'}{os.pathsep}engine/nut/",
            f"--add-data={directory / 'engine' / 'tcl'}{os.pathsep}engine/tcl/",
        ]

        for path in autoadd:
            if (directory / path).exists():
                pyi_args.append(f"--add-data={directory / path!s}{os.pathsep}{path!s}")

        pyi_args.append(f"--add-data={directory / 'data'!s}{os.pathsep}data")
        pyi_args.append(str(directory / "run.py"))

        pyinstaller(pyi_args=pyi_args)
    finally:
        log_queue.put(None)


def build(
    name: str, directory: Path, ENGINE_DATA_PATH: str
) -> Optional[Tuple[Process, "Queue[Optional[str]]"]]:
    """
    Build the game

    Args:
        name (str): The project's name
        directory (Path): Path to build the game to
        ENGINE_DATA_PATH (str): Path of the data directory

    Returns:
        Optional[Tuple[Process, Queue[Optional[str]]]]: The process running the
        PyInstaller build and a queue of its output lines, or None if the build
        could not be started. Callers can poll `process.is_alive()` to know when
        the build has actually finished, and drain the queue for PyInstaller's
        output as it happens. A `None` item on the queue marks the end of output.
    """

    if not directory.exists():
        logger.warning(f'Build directory "{str(directory.resolve())}" does not exist.')
        messagebox.showerror(
            "Build Error",
            f'Build directory "{str(directory.resolve())}" does not exist. Save the project to a valid location and try again.',
        )
        return None

    launch_game_script = Path(resource_path("data/scripts/launch_game.py")).read_text(
        encoding="utf-8"
    )
    (directory / "run.py").write_text(launch_game_script, encoding="utf-8")

    ignore = shutil.ignore_patterns("*.pyc", "__pycache__")

    shutil.copytree(engine_path, directory / "engine", dirs_exist_ok=True, ignore=ignore)
    shutil.copytree(Path(ENGINE_DATA_PATH), directory / "data", dirs_exist_ok=True, ignore=ignore)

    name = name.replace(" ", "-")

    log_queue: "Queue[Optional[str]]" = Queue()
    process = Process(
        target=_build_pyinstaller,
        args=(name, directory, log_queue, ["scripts"]),
    )
    process.start()

    return process, log_queue
