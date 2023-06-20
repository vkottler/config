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


class YambsRunApp(YambsTask):
    """A class for running built binaries."""

    async def run_app(
        self,
        root: Path,
        app: str = "",
        variant: str = YambsTask.default_variant,
    ) -> bool:
        """Run a single application."""

        data = self.apps(root)

        # Select an application.
        app_sel = manual_select("app", data["all"], default=app)
        if app_sel is None:
            return False

        app_data = data["all"][app_sel]

        # Select a variant.
        variant_sel = manual_select(
            "variant",
            app_data["variants"],
            default=variant,
        )
        if variant_sel is None:
            return False

        entry = app_data["variants"][variant_sel]

        result = True

        # Build if the file isn't there.
        if not Path(entry).is_file():
            result = await self.handle_build()

        # Run the application.
        if result:
            result = await self.exec(entry)

        return result

    async def run(self, inbox: Inbox, outbox: Outbox, *args, **kwargs) -> bool:
        """Generate ninja configuration files."""

        return await self.run_app(
            args[0],
            app=kwargs.get("app", ""),
            variant=kwargs.get("variant", self.default_variant),
        )
