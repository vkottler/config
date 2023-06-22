"""
A module implementing task interfaces for the yambs project.
"""

# third-party
from vcorelib.task import Inbox, Outbox

# internal
from .base import YambsTask
from .run import YambsRunApp
from .test import YambsRunTest

__all__ = ["Yambs", "YambsRunApp", "YambsRunTest"]


class Yambs(YambsTask):
    """A task for generating ninja configurations."""

    async def run(self, inbox: Inbox, outbox: Outbox, *args, **kwargs) -> bool:
        """Generate ninja configuration files."""
        return await self.run_generate_build(args[0], inbox, **kwargs)
