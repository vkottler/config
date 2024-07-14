"""
A module for implementing uf2 hooks.
"""

# built-in
from pathlib import Path
from typing import Any, Dict

# third-party
from vcorelib.paths.context import in_dir

# internal
from experimental_lowqa.edit import is_local_bin
from userfs.build import run_process
from userfs.config import ProjectSpecification


def post_fetch(
    root: Path,
    project: ProjectSpecification,
    _: Dict[str, Any],
    __: Dict[str, Any],
) -> None:
    """Project interaction."""

    if is_local_bin("uf2tool"):
        return

    loc = project.location(root=root)
    with in_dir(loc):
        run_process(project.logger, ["make", "-C", "uf2tool"])
