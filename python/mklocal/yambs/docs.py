"""
A module implementing a documentation-building task.
"""

# built-in
from pathlib import Path
from shutil import copyfile, copytree, rmtree
from typing import Dict

# third-party
from vcorelib.task import Inbox, Outbox, Phony
from vcorelib.task.manager import TaskManager
from vcorelib.task.subprocess.run import register_http_server_task

# internal
from vmklib.tasks.clean import Clean

from .base import YambsTask


class YambsDist(YambsTask):
    """A class for running the 'docs' command."""

    async def run(self, inbox: Inbox, outbox: Outbox, *args, **kwargs) -> bool:
        """Generate ninja configuration files."""

        docs_dir: Path = args[0]
        cwd = docs_dir.parent

        # README dependencies.
        for subdir in ["im", "md"]:
            if cwd.joinpath(subdir).is_dir():
                rmtree(docs_dir.joinpath(subdir), ignore_errors=True)
                copytree(cwd.joinpath(subdir), docs_dir.joinpath(subdir))

        venv_bin = inbox["venv"]["venv{python_version}"]["bin"]

        result = await self.shell_cmd_in_dir(
            docs_dir, [str(venv_bin.joinpath("sphinx-build")), ".", "_build"]
        )

        # Create docs/dist for packaging.
        if result:
            dest = docs_dir.joinpath("dist")
            rmtree(dest, ignore_errors=True)
            dest.mkdir()

            for item in docs_dir.joinpath("_build").iterdir():
                if item.name in {
                    "_modules",
                    "_static",
                    "_images",
                    "generated",
                }:
                    copytree(item, dest.joinpath(item.name))
                elif item.suffix in {".html", ".js"}:
                    copyfile(item, dest.joinpath(item.name))

        return result


def register_docs(
    manager: TaskManager,
    project: str,
    cwd: Path,
    substitutions: Dict[str, str],
) -> None:
    """Register a documentation-generation task."""

    del project
    del substitutions

    docs_dir = cwd.joinpath("docs")

    manager.register(YambsDist("docs", docs_dir))
    manager.register(Phony("d"), ["docs"])

    manager.register(
        Clean(
            "clean-docs",
            docs_dir.joinpath("_build"),
            docs_dir.joinpath("generated"),
            docs_dir.joinpath("xml"),
        )
    )

    register_http_server_task(
        manager, docs_dir.joinpath("_build"), "hd", ["docs"]
    )
