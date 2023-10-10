"""
A module for running interface-generator tasks.
"""

# built-in
from pathlib import Path
from typing import Dict

# third-party
from vcorelib.task import Inbox, Outbox
from vcorelib.task.manager import TaskManager

# internal
from .base import YambsTask


class IfgenTask(YambsTask):
    """A task for running interface-generator commands."""

    default_requirements = YambsTask.default_requirements | {
        "python-install-ifgen"
    }

    def ifgen(self, inbox: Inbox) -> str:
        """Get the path to the 'mbs' entry script."""
        return self.python_script("ig", inbox)

    async def run(self, inbox: Inbox, outbox: Outbox, *args, **kwargs) -> bool:
        """Run the interface generator."""

        cwd: Path = args[0]

        cmd = "gen"
        params = []

        # Generate interfaces for a chip based on SVD.
        if "chip" in kwargs:
            cmd = "svd"
            params.append("-o")
            package = kwargs.get("package", "ifgen")
            params.append(package)
            params.append(f"package://{package}/svd/{kwargs['chip']}.svd")

        result = await self.exec(
            self.ifgen(inbox), "-C", str(cwd), cmd, *params
        )

        # Format generated code.
        if cmd != "svd" and result:
            result &= await self.exec("ninja", "format")

        return result


def register_ifgen(
    manager: TaskManager,
    project: str,
    cwd: Path,
    substitutions: Dict[str, str],
) -> None:
    """Register project tasks to the manager."""

    manager.register(IfgenTask("ifgen-svd-{chip}", cwd))
    manager.register(IfgenTask("ifgen", cwd))

    del project
    del substitutions
