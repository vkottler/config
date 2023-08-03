"""
A module for project documentation tasks.
"""

# third-party
from vcorelib.task import Inbox, Outbox
from vcorelib.task.subprocess.run import SubprocessLogMixin


class SphinxTask(SubprocessLogMixin):
    """A class to facilitate generating documentatino with sphinx."""

    default_requirements = {"python-install-sphinx"}

    async def run(self, inbox: Inbox, outbox: Outbox, *args, **kwargs) -> bool:
        """Generate ninja configuration files."""

        print("yup")

        return True
