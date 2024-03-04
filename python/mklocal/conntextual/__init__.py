"""
A module capable of registering workflow tasks for invoking project-specific
conntextual tasks.
"""

# built-in
from pathlib import Path
from typing import Any, Dict, List

# isort: off

# third-party
from vcorelib.io import ARBITER
from vcorelib.io.types import FileExtension
from vcorelib.paths.context import tempfile
from vcorelib.task import Inbox, Outbox
from vcorelib.task.manager import TaskManager
from vcorelib.task.subprocess.run import SubprocessLogMixin

# isort: on

# internal
from ..prompts import manual_select


class ConntextualTask(SubprocessLogMixin):
    """A task for running conntextual."""

    default_requirements = {
        "vmklib.init",
        "venv",
        "python-editable",
        "python-install-conntextual",
    }

    async def run(self, inbox: Inbox, outbox: Outbox, *args, **kwargs) -> bool:
        """Generate ninja configuration files."""

        # check for data files in 'configs'
        configs = {}

        root: Path = args[0].joinpath("tasks")
        for path in root.iterdir():
            if path.is_file():
                ext = FileExtension.from_path(path)
                if ext is not None and ext.is_data():
                    configs[path.with_suffix("").name] = path

        app = manual_select(
            "app", configs, default=kwargs.get("app", "default")
        )

        result = False
        if app is not None:
            config_args = [str(configs[app])]

            # Add extra data.
            extra_data: Dict[str, Any] = args[1]
            with tempfile(suffix=".yaml") as temp_config:
                ARBITER.encode(temp_config, {"config": extra_data})
                config_args.append(str(temp_config))

                result = await self.exec(
                    str(
                        inbox["venv"]["venv{python_version}"]["bin"].joinpath(
                            "conntextual"
                        )
                    ),
                    "ui",
                    *args[2],
                    *config_args
                )

        return result


def register(
    manager: TaskManager,
    project: str,
    cwd: Path,
    substitutions: Dict[str, str],
) -> bool:
    """Register project tasks to the manager."""

    # May as well forward everything to the 'config' data.
    extra_data = {
        "project": project,
        "cwd": str(cwd),
        "substitutions": substitutions,
    }

    standard: List[str] = []
    headless: List[str] = ["-v", "headless"]

    manager.register(ConntextualTask("r", cwd, extra_data, standard))
    manager.register(ConntextualTask("rh", cwd, extra_data, headless))
    manager.register(ConntextualTask("r-{app}", cwd, extra_data, standard))
    manager.register(ConntextualTask("rh-{app}", cwd, extra_data, headless))

    return True
