"""
Utilities common to multiple project tasks.
"""

# built-in
from contextlib import suppress
from os import environ, pathsep
from pathlib import Path
from typing import Dict

PATHS: Dict[str, Path] = {}


def add_path(path: Path) -> None:
    """Add to the system path variable."""

    str_path = str(path)
    if str_path not in environ["PATH"]:
        environ["PATH"] = str_path + pathsep + environ["PATH"]


def add_program_path(
    program: str,
    third_party: Path,
    *parts: str,
    update_path: bool = False,
    local_bin: bool = False,
) -> bool:
    """Register a path to a program."""

    prog = third_party.joinpath(*parts).resolve()
    assert program not in PATHS, prog

    result = False

    if prog.is_file():
        with suppress(FileNotFoundError):
            if local_bin:
                link_local_bin(prog)

            if update_path:
                add_path(prog.parent)

            PATHS[program] = prog

    return result


def program_str(program: str) -> str:
    """Get a string path to a program."""
    return str(PATHS[program])


PREFIX = Path.home().joinpath(".local")


def lbin(program: str) -> Path:
    """Get the path to a local binary."""
    return PREFIX.joinpath("bin", program)


def is_local_bin(program: str) -> bool:
    """Determine if a binary or entry script is installed locally."""
    return lbin(program).is_file()


def link_local_bin(path: Path) -> None:
    """Link a local binary from some arbitrary location."""

    prog = path.name
    if not is_local_bin(prog):
        lbin(prog).symlink_to(path.resolve())
