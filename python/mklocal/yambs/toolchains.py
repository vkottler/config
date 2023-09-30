"""
A module implementing project tasks for working with toolchains.
"""

# built-in
from pathlib import Path
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
        output = dest.joinpath(f"{toolchain}.{DEFAULT_ARCHIVE_EXT}")

        link = cwd.joinpath(toolchain)
        out = cwd.joinpath("out")
        if out.exists():
            out.rename(link)

        if not output.exists():
            result = make_archive(link, dst_dir=dest)
            assert result[0] is not None
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

    toolchains = ["arm-picolibc-eabi"]
    manager.register(Phony("toolchains"), [f"pack-{x}" for x in toolchains])

    del project
    del substitutions
