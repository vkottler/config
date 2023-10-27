"""
A module implementing interfaces for running built binaries.
"""

# built-in
import os
from pathlib import Path

# third-party
from vcorelib.task import Inbox, Outbox

# internal
from .base import YambsTask


class YambsRunApp(YambsTask):
    """A class for running built binaries."""

    async def run_app(
        self, root: Path, app: str = "", variant: str = None
    ) -> bool:
        """Run a single application."""

        entry = await self.select_app_variant(root, app=app, variant=variant)

        result = False

        # Run the application.
        if entry is not None and entry.is_file():
            result = await self.exec(str(entry), env=os.environ)

        return result

    async def run(self, inbox: Inbox, outbox: Outbox, *args, **kwargs) -> bool:
        """Generate ninja configuration files."""

        return await self.run_app(
            args[0],
            app=kwargs.get("app", ""),
            variant=kwargs.get("variant", self.default_variant),
        )
