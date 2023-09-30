"""
A module implementing project tasks for working with toolchains.
"""

# built-in
from pathlib import Path
from typing import Dict

# isort: off

# third-party
from vcorelib.task import Inbox, Outbox
from vcorelib.task.manager import TaskManager
from vcorelib.task.subprocess.run import SubprocessLogMixin

# isort: on


class UserfsTask(SubprocessLogMixin):
    """A simple task for running userfs commands."""

    default_requirements = {"vmklib.init", "venv", "python-install-userfs"}

    def ufs(self, inbox: Inbox) -> str:
        """Get the path to the 'mbs' entry script."""

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
            *args[1:]
        )


def register_toolchains(
    manager: TaskManager,
    project: str,
    cwd: Path,
    substitutions: Dict[str, str],
) -> None:
    """Register project tasks to the manager."""

    manager.register(UserfsTask("ufs-{action}", cwd, "-a"))

    del project
    del substitutions
