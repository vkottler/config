"""
A module for Python-project task registration.
"""

# built-in
from pathlib import Path
from typing import Dict

# third-party
from vcorelib.task import Phony
from vcorelib.task.manager import TaskManager
from vcorelib.task.subprocess.run import is_windows

# internal
from mklocal.docs import SphinxTask
from mklocal.runtimepy import ArbiterTask


def register(
    manager: TaskManager,
    project: str,
    cwd: Path,
    substitutions: Dict[str, str],
) -> bool:
    """Register project tasks to the manager."""

    # Don't run yamllint on Windows because it will fail on newlines.
    manager.register(
        Phony("yaml"),
        [] if is_windows() else ["yaml-lint-local", "yaml-lint-manifest.yaml"],
    )

    if project == "runtimepy":
        manager.register(ArbiterTask("r", cwd))

    manager.register(SphinxTask("docs", cwd))

    del substitutions

    return True


register_python = register
