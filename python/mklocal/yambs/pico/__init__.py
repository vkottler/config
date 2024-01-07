"""
A module implementing tasks for RP2040 boards.
"""

# built-in
import asyncio
from pathlib import Path

# isort: off

# third-party
from vmklib.tasks.mixins.concrete import ConcreteOnceMixin
from vcorelib.task import Inbox, Outbox
from vcorelib.task.manager import TaskManager
from vcorelib.task.subprocess.run import SubprocessLogMixin

# internal
from ..base import YambsTask
from ..common import add_program_path

# isort: on

PIOASM_DIR = ["pico-sdk", "tools", "pioasm"]


class BuildPioasm(ConcreteOnceMixin, SubprocessLogMixin):
    """A task for ensuring pioasm is built and available for use."""

    async def run(self, inbox: Inbox, outbox: Outbox, *args, **kwargs) -> bool:
        """Build pioasm."""

        root: Path = args[0]

        pioasm_dir = root.joinpath(*PIOASM_DIR)
        build_dir = pioasm_dir.joinpath("build")

        result = True

        pioasm = build_dir.joinpath("pioasm")

        # Ensure the program is built.
        if not pioasm.is_file():
            result &= await self.shell_cmd_in_dir(build_dir, ["cmake", ".."])
            result &= await self.shell_cmd_in_dir(build_dir, ["ninja"])

        return result


class PicotoolDeploy(YambsTask):
    """A class implementing a simple picotool-based firmware deploy."""

    default_variant = "pico"

    async def run(self, inbox: Inbox, outbox: Outbox, *args, **kwargs) -> bool:
        """Perform a firmware update using picotool."""

        root: Path = args[0]

        entry = await self.select_app_variant(
            root, app=kwargs.get("app", ""), variant=kwargs.get("variant")
        )

        result = False

        if entry:
            entry = entry.with_suffix(".uf2")
            if entry.is_file():
                assert await self.exec("picotool", "reboot", "-f", "-u")
                await asyncio.sleep(2.0)

                # Perform load then reboot.
                assert await self.exec("picotool", "info")
                assert await self.exec("picotool", "load", str(entry))
                assert await self.exec("picotool", "reboot")
                result = True

        return result


def register(manager: TaskManager, cwd: Path) -> None:
    """Register tasks related to the Pi Pico."""

    manager.register(BuildPioasm("pioasm", cwd))

    add_program_path(
        "pioasm",
        cwd,
        *PIOASM_DIR,
        "build",
        "pioasm",
        update_path=True,
        local_bin=True
    )

    manager.register(PicotoolDeploy("pd", cwd), ["gb"])
