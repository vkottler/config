"""
A module implementing task interfaces for the yambs project.
"""

# third-party
from vcorelib.task import Inbox, Outbox

# internal
from .base import YambsTask
from .dist import YambsDist
from .edit import GenerateTags
from .run import YambsRunApp
from .test import YambsRunTest

__all__ = ["Yambs", "YambsRunApp", "YambsRunTest", "GenerateTags", "YambsDist"]


class Yambs(YambsTask):
    """A task for generating ninja configurations."""

    async def run(self, inbox: Inbox, outbox: Outbox, *args, **kwargs) -> bool:
        """Generate ninja configuration files."""
        return await self.run_generate_build(args[0], inbox, **kwargs)
