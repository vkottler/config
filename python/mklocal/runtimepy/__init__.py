"""
A module for tasks related to the runtimepy project.
"""

# built-in
from pathlib import Path

# third-party
from vcorelib.task import Inbox, Outbox
from vcorelib.task.subprocess.run import SubprocessLogMixin


class ArbiterTask(SubprocessLogMixin):
    """A task for running the runtime arbiter."""

    default_requirements = {"vmklib.init", "venv", "python-editable"}

    async def run(self, inbox: Inbox, outbox: Outbox, *args, **kwargs) -> bool:
        """Generate ninja configuration files."""

        cwd: Path = args[0]

        configs = cwd.joinpath("local", "arbiter")

        config = configs.joinpath(kwargs.get("config", "test") + ".yaml")

        cli_args = [
            str(
                inbox["venv"]["venv{python_version}"]["bin"].joinpath(
                    "runtimepy"
                )
            )
        ]

        if kwargs.get("verbose", False):
            cli_args.append("--verbose")

        cli_args += ["arbiter", str(config)]

        return await self.exec(*cli_args)
