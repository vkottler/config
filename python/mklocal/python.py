"""
A module for Python-project task registration.
"""

# built-in
from pathlib import Path
from shutil import rmtree
from typing import Dict

# isort: off

# internal
from experimental_lowqa.tasks.conntextual import (
    register as register_conntextual,
)
from experimental_lowqa.tasks.docs import SphinxTask
from experimental_lowqa.tasks.python import PythonTags

# third-party
from vcorelib.task import Phony, Inbox, Outbox
from vcorelib.task.manager import TaskManager
from vcorelib.task.subprocess.run import (
    is_windows,
    register_http_server_task,
    SubprocessLogMixin,
)

from vmklib.tasks.clean import Clean  # pylint: disable=wrong-import-order
from vmklib.tasks.python import PREFIX

# isort: on


class SvgenTask(SubprocessLogMixin):
    """A task for running svgen."""

    default_requirements = {"venv", PREFIX + "install-svgen"}

    async def run(self, inbox: Inbox, outbox: Outbox, *args, **kwargs) -> bool:
        """Generate a tags files."""

        variant = kwargs.get("variant", "default")

        tasks = Path("tasks", "svgen")
        build = Path("build", "svgen", variant)

        if build.is_dir() and kwargs.get("clean"):
            rmtree(build)
        build.mkdir(parents=True, exist_ok=True)

        svgen_args = [
            "-c",
            str(tasks.joinpath(f"{variant}.yaml")),
            "-o",
            str(build.joinpath(f"{variant}.svg")),
        ]

        if kwargs.get("images"):
            svgen_args.append("--images")

        svgen_args.append(str(tasks.joinpath(f"{variant}.py")))

        return await self.exec(
            str(inbox["venv"]["venv{python_version}"]["python"]),
            "-m",
            "svgen",
            *svgen_args,
        )


def register(
    manager: TaskManager,
    project: str,
    cwd: Path,
    substitutions: Dict[str, str],
) -> bool:
    """Register project tasks to the manager."""

    register_conntextual(manager, project, cwd, substitutions)

    manager.register(PythonTags("e", cwd))

    # Don't run yamllint on Windows because it will fail on newlines.
    manager.register(
        Phony("yaml"),
        (
            []
            if is_windows()
            else [
                "yaml-lint-local",
                "yaml-lint-tasks",
                "yaml-lint-manifest.yaml",
                f"yaml-lint-{project.replace('-', '_')}",
            ]
        ),
    )

    # Use conntextual 'r' style target instead.
    # if project == "runtimepy":
    #     manager.register(ArbiterTask("r", cwd))

    # Documentation tasks.
    manager.register(SphinxTask("docs", cwd, project))

    docs_dir = cwd.joinpath("docs")

    manager.register(Clean("clean-docs", docs_dir))

    register_http_server_task(
        manager, docs_dir.joinpath("_build"), "hd", ["docs"]
    )

    # SVG tasks.
    manager.register(SvgenTask("svgen"))
    manager.register(SvgenTask("svgeni", images=True))

    del substitutions

    return True


register_python = register
