"""
A module for implementing ansible hooks.
"""

# built-in
from pathlib import Path
from typing import Any, Dict

# third-party
from userfs.build import run_process
from userfs.config import ProjectSpecification

# internal
from hooks_common import PROGS


def pre_deploy(
    root: Path,
    project: ProjectSpecification,
    _: Dict[str, Any],
    __: Dict[str, Any],
) -> None:
    """Project interaction."""

    run_process(
        project.logger,
        [str(PROGS["pip"]), "install", "-e", str(project.location(root=root))],
    )
