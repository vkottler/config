"""
A module implementing interfaces for building source distributions.
"""

# third-party
from vcorelib.task import Inbox, Outbox

# internal
from .base import YambsTask


class YambsDist(YambsTask):
    """A class for running the 'dist' command."""

    async def run(self, inbox: Inbox, outbox: Outbox, *args, **kwargs) -> bool:
        """Generate ninja configuration files."""

        return await self.exec(self.mbs(inbox), "dist")
