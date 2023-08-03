"""
A module for project documentation tasks.
"""

# built-in
from pathlib import Path

# third-party
from vcorelib.task import Inbox, Outbox
from vcorelib.task.subprocess.run import SubprocessLogMixin


class SphinxTask(SubprocessLogMixin):
    """A class to facilitate generating documentatino with sphinx."""

    default_requirements = {"venv", "python-install-sphinx", "python-editable"}

    async def run(self, inbox: Inbox, outbox: Outbox, *args, **kwargs) -> bool:
        """Generate ninja configuration files."""

        cwd: Path = args[0]
        project: str = args[1]

        venv_bin = inbox["venv"]["venv{python_version}"]["bin"]

        # Generate sources with apidoc.
        result = await self.shell_cmd_in_dir(
            cwd.joinpath("docs"),
            [
                str(venv_bin.joinpath("sphinx-apidoc")),
                str(Path("..", project.replace("-", "_"))),
                "-A",
                f"\"{kwargs.get('author', 'Vaughn Kottler')}\"",
                "-f",
                "-F",
                "-o",
                ".",
            ],
        )

        # Build.
        if result:
            result = await self.shell_cmd_in_dir(
                cwd.joinpath("docs"),
                [
                    str(venv_bin.joinpath("sphinx-build")),
                    "-W",
                    ".",
                    "_build",
                ],
            )

        return result
