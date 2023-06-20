"""
A module implementing interfaces for running built binaries.
"""

# built-in
from pathlib import Path

# third-party
from vcorelib.task import Inbox, Outbox

# internal
from ..prompts import manual_select
from .base import YambsTask


class YambsRun(YambsTask):
    """A class for running built binaries."""

    async def run(self, inbox: Inbox, outbox: Outbox, *args, **kwargs) -> bool:
        """Generate ninja configuration files."""

        root: Path = args[0]
        data = self.apps(root)

        # Select an application.
        app = manual_select("app", data["all"], default=kwargs.get("app", ""))

        app_data = data["all"][app]

        # Select a variant.
        variant = manual_select(
            "variant",
            app_data["variants"],
            default=kwargs.get("variant", "debug"),
        )
        entry = app_data["variants"][variant]

        result = True

        # Build if the file isn't there.
        if not Path(entry).is_file():
            result = await self.handle_build()

        # Run the application.
        if result:
            result = await self.exec(entry)

        return result
