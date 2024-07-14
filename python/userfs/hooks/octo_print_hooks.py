"""
A module for implementing OctoPrint hooks.
"""

# built-in
from pathlib import Path
from typing import Any, Dict

# internal
from experimental_lowqa.userfs import PROGS

# third-party
from userfs.config import ProjectSpecification


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
