"""
A module for Python-project task registration.
"""

# built-in
from pathlib import Path
from typing import Dict

# isort: off

# third-party
from vcorelib.task import Phony
from vcorelib.task.manager import TaskManager
from vcorelib.task.subprocess.run import is_windows, register_http_server_task

# isort: on

# internal
from mklocal.conntextual import register as register_conntextual
from mklocal.docs import SphinxTask
from mklocal.runtimepy import ArbiterTask
from vmklib.tasks.clean import Clean  # pylint: disable=wrong-import-order


def register(
    manager: TaskManager,
    project: str,
    cwd: Path,
    substitutions: Dict[str, str],
) -> bool:
    """Register project tasks to the manager."""

    register_conntextual(manager, project, cwd, substitutions)

    # Don't run yamllint on Windows because it will fail on newlines.
    manager.register(
        Phony("yaml"),
        []
        if is_windows()
        else [
            "yaml-lint-local",
            "yaml-lint-tasks",
            "yaml-lint-manifest.yaml",
            f"yaml-lint-{project.replace('-', '_')}",
        ],
    )

    if project == "runtimepy":
        manager.register(ArbiterTask("r", cwd))

    # Documentation tasks.
    manager.register(SphinxTask("docs", cwd, project))

    docs_dir = cwd.joinpath("docs")

    manager.register(Clean("clean-docs", docs_dir))

    register_http_server_task(
        manager, docs_dir.joinpath("_build"), "hd", ["docs"]
    )

    del substitutions

    return True


register_python = register
