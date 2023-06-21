"""
A module for working with environment variables.
"""

# built-in
from json import loads
import os
from pathlib import Path
from subprocess import run
from sys import executable


def source_file(path: Path) -> None:
    """Attempt to source a file."""

    # A simple script to dump environment contents to JSON.
    script = "import os,json;print(json.dumps(dict(os.environ)))"

    os.environ = loads(
        run(
            f'. {path} && {executable} -c "{script}"',
            shell=True,
            check=True,
            capture_output=True,
        ).stdout.decode()
    )


def try_source(path: Path) -> None:
    """Attempt to source a file if it exists."""

    if path.is_file():
        source_file(path)
