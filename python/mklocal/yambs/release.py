"""
A module for working with GitHub releases.
"""

# third-party
from vcorelib.task import Inbox, Outbox

# internal
from .base import YambsTask


class YambsUploadRelease(YambsTask):
    """A class for running the 'dist' command."""

    async def run(self, inbox: Inbox, outbox: Outbox, *args, **kwargs) -> bool:
        """Generate ninja configuration files."""

        return False
