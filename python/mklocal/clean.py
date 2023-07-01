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

        keep = kwargs.get("keep")

        for arg in args:
            if arg.exists() and keep is None or keep not in arg.name:
                self.logger.info("Removing '%s'.", arg)
            rmtree(arg, ignore_errors=True)

        return True
