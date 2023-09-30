"""
A module for implementing ctags hooks.
"""

# built-in
from pathlib import Path
from typing import Any, Dict

# third-party
from userfs.build import run_process
from userfs.config import ProjectSpecification
from vcorelib.paths.context import in_dir

# internal
from hooks_common import MAKE_NPROCS, PREFIX_ARGS, is_local_bin


def post_fetch(
    root: Path,
    project: ProjectSpecification,
    _: Dict[str, Any],
    __: Dict[str, Any],
) -> None:
    """Project interaction."""

    if is_local_bin(project.repository):
        return

    with in_dir(project.location(root=root)):
        # Check if we need to autogen.
        if not Path("configure").is_file():
            project.logger.info("Running autogen.")
            run_process(project.logger, ["./autogen.sh"])

        # Check if we need to configure.
        if not Path("Makefile").is_file():
            run_process(project.logger, ["./configure", PREFIX_ARGS])

        # Build and install.
        run_process(project.logger, ["make", MAKE_NPROCS])
        run_process(project.logger, ["make", "install"])
