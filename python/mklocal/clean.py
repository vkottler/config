"""
A module for implementing clean tasks.
"""

# internal
from shutil import rmtree

# third-party
from vcorelib.task import Inbox, Outbox
from vmklib.tasks import VmklibBase


class Clean(VmklibBase):
    """A class for removing files and directories."""

    async def run(self, inbox: Inbox, outbox: Outbox, *args, **kwargs) -> bool:
        """Generate ninja configuration files."""

        for arg in args:
            if arg.exists():
                self.logger.info("Removing '%s'.", arg)
            rmtree(arg, ignore_errors=True)

        return True
