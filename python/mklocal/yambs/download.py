"""
A module implementing a yambs-download task.
"""

# built-in
from pathlib import Path

# third-party
from vcorelib.task import Inbox, Outbox

# internal
from .base import YambsTask


class YambsDownload(YambsTask):
    """A simple task for running mbs download."""

    async def run(self, inbox: Inbox, outbox: Outbox, *args, **kwargs) -> bool:
        """Build a specific toolchain."""

        cwd: Path = args[0]
        return await self.exec(
            self.mbs(inbox), "-C", str(cwd), "download", *args[1:]
        )
