"""
A module for implementing OctoPrint hooks.
"""

# built-in
from pathlib import Path
from typing import Any, Dict

# third-party
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

    print(root)
    print(project)
    print(PROGS["pip"])
