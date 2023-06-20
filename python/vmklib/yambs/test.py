"""
A module implementing interfaces for running test binaries.
"""

# built-in
from pathlib import Path

# third-party
from vcorelib.task import Inbox, Outbox

# internal
from .base import YambsTask


class YambsRunTest(YambsTask):
    """A class for running built-binary unit tests."""

    async def run(self, inbox: Inbox, outbox: Outbox, *args, **kwargs) -> bool:
        """Run unit tests."""

        root: Path = args[0]
        data = self.apps(root)

        # Aggregate scripts to run.
        entries = [
            data["all"][x]["variants"][
                kwargs.get("variant", self.default_variant)
            ]
            for x in data["tests"]
        ]
        print(entries)

        # Filter scripts by pattern.
        pattern = kwargs.get("pattern", ".*")
        print(pattern)

        return True
