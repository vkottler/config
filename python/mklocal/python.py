"""
A module for Python-project task registration.
"""

# built-in
from copy import copy
from pathlib import Path
from typing import Dict

# isort: off

# third-party
from vcorelib.task import Inbox, Outbox, Phony
from vcorelib.task.manager import TaskManager
from vcorelib.task.subprocess.run import is_windows, register_http_server_task

# isort: on

# internal
from mklocal.conntextual import register as register_conntextual
from mklocal.docs import SphinxTask
from mklocal.edit import GenerateTags
from vmklib.tasks.clean import Clean  # pylint: disable=wrong-import-order


def to_slug(data: str) -> str:
    """Get a slug from a string."""
    return data.replace("-", "_")


class PythonTags(GenerateTags):
    """A class implementing a task for generating tags files."""

    languages = "Python"

    extra_source_candidates = [
        ("tasks",),
        ("tests",),
        (Path.home(), "src", "python", "cpython", "Lib"),
    ]

    async def run(self, inbox: Inbox, outbox: Outbox, *args, **kwargs) -> bool:
        """Generate a tags files."""

        root: Path = args[0]

        py_root = root.joinpath(to_slug(root.name))

        src = root.joinpath("src")
        if not src.exists() and py_root.is_dir():
            src.symlink_to(py_root, target_is_directory=True)

        self.extra_source_candidates = copy(type(self).extra_source_candidates)

        # Add extra source candidates for other Python projects.
        for candidate in ["vcorelib", "runtimepy", "svgen"]:
            if root.name != candidate:
                self.extra_source_candidates.append(
                    ("..", candidate, to_slug(candidate))
                )

        return await super().run(inbox, outbox, *args, **kwargs)


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

    del substitutions

    return True


register_python = register
