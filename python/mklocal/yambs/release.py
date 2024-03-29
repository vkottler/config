"""
A module for working with GitHub releases.
"""

# built-in
from pathlib import Path
from typing import Any, Dict

# isort: off

# third-party
from vcorelib.task import Inbox, Outbox

from vmklib.tasks.release import GithubRelease

# isort: on

# internal
from .base import YambsTask

ApiResult = Dict[str, Any]


class YambsUploadRelease(YambsTask, GithubRelease):
    """A class for running the 'dist' command."""

    async def run(self, inbox: Inbox, outbox: Outbox, *args, **kwargs) -> bool:
        """Create a GitHub release."""

        cwd: Path = args[0]

        # Load the project configuration.
        config = self.native_config(cwd)

        # Ensure GitHub parameters are set.
        if config.project.owner is None:
            self.log.error("'project.github.owner' not set in configuration!")
            return False

        # Attempt to create a new release.
        return await self.release(
            cwd,
            config.project.owner,
            config.project.repo,
            config.project.version,
            dist=kwargs.get("dist", "dist"),
        )
