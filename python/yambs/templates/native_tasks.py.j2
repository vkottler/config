"""
A module for project-specific task registration.
"""

# built-in
from pathlib import Path
from subprocess import run
from typing import Dict

# third-party
from vcorelib.task.manager import TaskManager


def audit_local_tasks() -> None:
    """Ensure that shared task infrastructure is present."""

    local = Path(__file__).parent.joinpath("local")
    if local.is_symlink():
        return

    # If it's not a symlink, it shouldn't be any other kind of file.
    assert not local.exists()

    # Ensure sub-module implementation is present.
    config = local.parent.parent.joinpath("config")
    assert config.is_dir()

    # Initialize submodules if we don't see the directory we're looking for.
    vmklib = config.joinpath("python", "vmklib")
    if not vmklib.is_dir():
        run(
            ["git", "-C", str(config.parent), "submodule", "update", "--init"],
            check=True,
        )

    # Create the link.
    local.symlink_to(vmklib)


def register(
    manager: TaskManager,
    project: str,
    cwd: Path,
    substitutions: Dict[str, str],
) -> bool:
    """Register project tasks to the manager."""

    audit_local_tasks()

    from local import register_yambs_native

    return register_yambs_native(manager, project, cwd, substitutions)
