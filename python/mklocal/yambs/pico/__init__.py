"""
A module implementing tasks for RP2040 boards.
"""

# built-in
from pathlib import Path

# third-party
from vcorelib.task import Inbox, Outbox
from vcorelib.task.manager import TaskManager
from vcorelib.task.subprocess.run import SubprocessLogMixin

from vmklib.tasks.mixins.concrete import ConcreteOnceMixin

# internal
from ..common import add_program_path

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


class PicotoolDeploy(SubprocessLogMixin):
    """A class implementing a simple picotool-based firmware deploy."""

    async def run(self, inbox: Inbox, outbox: Outbox, *args, **kwargs) -> bool:
        """Perform a firmware update using picotool."""

        root: Path = args[0]
        print(root)

        # Always attempt to build. Keep this?
        # assert await self.exec("ninja")

        # Perform load then reboot.
        # assert await self.exec(
        #     "picotool", "load", str(elf_path.with_suffix(".uf2"))
        # )
        # assert await self.exec("picotool", "reboot")

        return True


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

    manager.register(PicotoolDeploy("picotool", cwd), ["gb"])
