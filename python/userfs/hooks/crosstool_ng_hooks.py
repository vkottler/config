"""
A module for implementing crosstool-ng hooks.
"""

# built-in
from pathlib import Path
from typing import Any, Dict

# third-party
from vcorelib.paths.context import in_dir

# internal
from experimental_lowqa.edit import is_local_bin
from experimental_lowqa.userfs import MAKE_NPROCS, PREFIX_ARGS
from userfs.build import run_process
from userfs.config import ProjectSpecification


def post_fetch(
    root: Path,
    project: ProjectSpecification,
    _: Dict[str, Any],
    __: Dict[str, Any],
) -> None:
    """Project interaction."""

    if is_local_bin("ct-ng"):
        return

    with in_dir(project.location(root=root)):
        # Check if we need to bootstrap.
        if not Path("configure").is_file():
            project.logger.info("Running bootstrap.")
            run_process(project.logger, ["./bootstrap"])

        # Check if we need to run configure.
        if not Path("Makefile").is_file():
            run_process(project.logger, ["./configure", PREFIX_ARGS])

        run_process(project.logger, ["make", MAKE_NPROCS])
        run_process(project.logger, ["make", "install"])
