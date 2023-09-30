"""
A module for implementing alacritty hooks.
"""

# built-in
from pathlib import Path
from typing import Any, Dict

# third-party
from userfs.build import run_process
from userfs.config import ProjectSpecification
from vcorelib.paths.context import in_dir

# internal
from hooks_common import is_local_bin, link_local_bin, local_bin


def post_fetch(
    root: Path,
    project: ProjectSpecification,
    _: Dict[str, Any],
    __: Dict[str, Any],
) -> None:
    """Project interaction."""

    if is_local_bin(project.repository):
        return

    run_process(
        project.logger,
        ["sudo", "apt-get", "install", "-y", "libfontconfig1-dev"],
    )

    loc = project.location(root=root)
    with in_dir(loc):
        run_process(project.logger, ["cargo", "build", "--release"])
        link_local_bin(loc.joinpath("target", "release", project.repository))

        run_process(
            project.logger,
            [
                "sudo",
                "update-alternatives",
                "--install",
                "/usr/bin/x-terminal-emulator",
                "x-terminal-emulator",
                str(local_bin(project.repository)),
                "1",
            ],
        )
        run_process(
            project.logger,
            ["sudo", "update-alternatives", "--config", "x-terminal-emulator"],
        )
