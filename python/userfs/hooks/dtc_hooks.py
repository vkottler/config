"""
A module for implementing device-tree compiler hooks.
"""

from os import environ

# built-in
from pathlib import Path
from sys import version_info
from typing import Any, Dict

# third-party
from vcorelib.paths.context import in_dir

# internal
from experimental_lowqa.edit import is_local_bin
from experimental_lowqa.userfs import PREFIX
from userfs.build import run_process
from userfs.config import ProjectSpecification


def post_fetch(
    root: Path,
    project: ProjectSpecification,
    _: Dict[str, Any],
    __: Dict[str, Any],
) -> None:
    """Project interaction."""

    if is_local_bin(project.repository):
        return

    environ["PKG_CONFIG_PATH"] = "/usr/local/lib/pkgconfig"

    # link python-3.11 to python3.11 .....

    # This install is not working right now.

    with in_dir(project.location(root=root)):
        run_process(
            project.logger,
            [
                "make",
                "install",
                f"PYTHON=python-{version_info.major}.{version_info.minor}",
                f"PREFIX={PREFIX}",
            ],
        )
