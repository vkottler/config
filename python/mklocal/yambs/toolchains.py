"""
A module implementing project tasks for working with toolchains.
"""

# built-in
from pathlib import Path
from platform import machine
from typing import Dict

# isort: off

# third-party
from vcorelib.io.archive import make_archive
from vcorelib.io.types import DEFAULT_ARCHIVE_EXT
from vcorelib.task import Inbox, Outbox, Phony
from vcorelib.task.manager import TaskManager
from vcorelib.task.subprocess.run import SubprocessLogMixin
from vcorelib.math.time import nano_str
from vmklib.tasks.mixins.concrete import ConcreteOnceMixin

# isort: on

# internal
from experimental_lowqa.tasks.yambs.common import add_path
from experimental_lowqa.tasks.yambs.jlink import register_jlink
from experimental_lowqa.tasks.yambs.jlink.gdbserver import jlink_gdbserver_task

from .download import YambsDownload

BOARDS = ["relax_kit", "grand_central", "pi_pico"]


class CrosstoolTask(ConcreteOnceMixin, SubprocessLogMixin):
    """
    A class implementing a task for building toolchains with crosstool-ng.
    """

    async def run(self, inbox: Inbox, outbox: Outbox, *args, **kwargs) -> bool:
        """Build a specific toolchain."""

        cwd = args[0].joinpath(kwargs["toolchain"])
        return await self.exec("ct-ng", "-C", str(cwd), "build")


class PackToolchainTask(SubprocessLogMixin):
    """A task for packing a toolchain for distribution."""

    async def run(self, inbox: Inbox, outbox: Outbox, *args, **kwargs) -> bool:
        """Pack a specific toolchain into a compressed archive file."""

        toolchain: str = kwargs["toolchain"]
        root: Path = args[0]
        cwd = root.joinpath(toolchain)

        dest = root.joinpath("dist")
        output = dest.joinpath(
            f"{toolchain}-{machine()}.{DEFAULT_ARCHIVE_EXT}"
        )

        link = cwd.joinpath(toolchain)
        out = cwd.joinpath("out")
        if out.exists():
            out.rename(link)

        if not output.exists():
            result = make_archive(link, dst_dir=dest)
            assert result[0] is not None

            if result[0] != output:
                result[0].rename(output)

            self.logger.info(
                "Created '%s' in %s.",
                output,
                nano_str(result[1], is_time=True),
            )

        return True


class UserfsTask(SubprocessLogMixin):
    """A simple task for running userfs commands."""

    default_requirements = {"vmklib.init", "venv", "python-install-userfs"}

    def ufs(self, inbox: Inbox) -> str:
        """Get the path to the 'ufs' entry script."""

        return str(
            inbox["venv"]["venv{python_version}"]["bin"].joinpath("ufs")
        )

    async def run(self, inbox: Inbox, outbox: Outbox, *args, **kwargs) -> bool:
        """Generate a tags files."""

        cwd: Path = args[0]

        return await self.exec(
            self.ufs(inbox),
            "-C",
            str(cwd),
            kwargs["action"],
            "-c",
            ".",
            *args[1:],
        )


ALL_TOOLCHAINS = ["arm-picolibc-eabi", "riscv32-picolibc-elf"]


def register_toolchains(
    manager: TaskManager,
    project: str,
    cwd: Path,
    substitutions: Dict[str, str],
) -> None:
    """Register project tasks to the manager."""

    manager.register(UserfsTask("ufs-{action}", cwd, "-a"))

    manager.register(CrosstoolTask("crosstool-{toolchain}", cwd))

    manager.register(
        PackToolchainTask("pack-{toolchain}", cwd), ["crosstool-{toolchain}"]
    )

    manager.register(
        Phony("toolchains"), [f"pack-{x}" for x in ALL_TOOLCHAINS]
    )
    for toolchain in ALL_TOOLCHAINS:
        add_path(cwd.joinpath("toolchains", toolchain, "bin"))

    third_party = cwd.joinpath("third-party")

    register_jlink(manager, third_party)
    for board in BOARDS:
        assert manager.register(jlink_gdbserver_task(board, third_party))

    # Register a task for downloading toolchains.
    manager.register(
        YambsDownload("download-toolchains", cwd, "-p", machine())
    )

    del project
    del substitutions
