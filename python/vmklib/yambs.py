"""
A module implementing task interfaces for the yambs project.
"""

# built-in
from pathlib import Path

# third-party
from vcorelib.task import Inbox, Outbox
from vcorelib.task.subprocess.run import SubprocessLogMixin


class Yambs(SubprocessLogMixin):
    """A task for generating ninja configurations."""

    default_requirements = {"vmklib.init", "venv", "python-install-yambs"}

    async def run(self, inbox: Inbox, outbox: Outbox, *args, **kwargs) -> bool:
        """Generate ninja configuration files."""

        root: Path = args[0]

        early = False

        if (
            kwargs.get("once", False)
            and root.joinpath("build.ninja").is_file()
        ):
            early = True

        result = True

        if kwargs.get("build", False):
            result = await self.exec(kwargs.get("ninja", "ninja"))

        if early:
            return result

        params = [kwargs.get("command", "native")]
        if kwargs.get("watch", False):
            params.append("-w")

        return await self.exec(
            str(inbox["venv"]["venv{python_version}"]["bin"].joinpath("mbs")),
            "-C",
            str(root),
            *params,
        )
