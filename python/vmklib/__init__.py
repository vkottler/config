"""
A module exposing task registration interfaces for different kinds of projects.
"""

# built-in
from pathlib import Path
from typing import Dict, List

# third-party
from vcorelib.task.manager import TaskManager

# internal
from .yambs import Yambs, YambsRunApp, YambsRunTest


def register_yambs_native(
    manager: TaskManager,
    project: str,
    cwd: Path,
    substitutions: Dict[str, str],
) -> bool:
    """Register project tasks to the manager."""

    del project
    del substitutions

    deps: List[str] = []

    # Targets for generating and building.
    manager.register(Yambs("g", cwd), deps)
    manager.register(Yambs("go", cwd, once=True), deps)
    manager.register(Yambs("gb", cwd, once=True, build=True), deps)
    manager.register(Yambs("gw", cwd, watch=True), deps)

    # Targets for running binaries.
    manager.register(YambsRunApp("r", cwd), ["gb"])
    manager.register(YambsRunTest("t", cwd), ["gb"])
    manager.register(YambsRunTest("t-{pattern}", cwd), ["gb"])

    return True
