"""
A module for implementing picamera2 hooks.
"""

# built-in
from pathlib import Path
from typing import Any, Dict

# third-party
from userfs.build import run_process
from userfs.config import ProjectSpecification

# internal
from hooks_common import PROGS


def pre_build(
    root: Path,
    project: ProjectSpecification,
    _: Dict[str, Any],
    __: Dict[str, Any],
) -> None:
    """Project interaction."""

    run_process(
        project.logger,
        [PROGS["pip"], "install", "-e", project.location(root=root)],
    )
