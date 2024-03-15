"""
A module implementing task interfaces for the yambs project.
"""

# built-in
from pathlib import Path
from typing import Dict, List

# isort: off

# third-party
from vcorelib.task import Inbox, Outbox, Phony
from vcorelib.task.manager import TaskManager
from vcorelib.task.subprocess.run import register_http_server_task, is_windows
from yambs.config.common import DEFAULT_CONFIG
from yambs.config.native import Native

# isort: on

# internal
from mklocal.conntextual import register as register_conntextual
from mklocal.env import try_source
from vmklib.tasks.clean import Clean  # pylint: disable=wrong-import-order

from .base import YambsTask
from .dist import YambsDist
from .docs import register_docs
from .edit import GenerateTags
from .ifgen import register_ifgen
from .pico import register as register_pico
from .release import YambsUploadRelease
from .run import YambsRunApp
from .test import YambsRunTest
from .toolchains import register_toolchains

__all__ = [
    "Yambs",
    "YambsRunApp",
    "YambsRunTest",
    "GenerateTags",
    "YambsDist",
    "YambsUploadRelease",
]


class Yambs(YambsTask):
    """A task for generating ninja configurations."""

    async def run(self, inbox: Inbox, outbox: Outbox, *args, **kwargs) -> bool:
        """Generate ninja configuration files."""
        return await self.run_generate_build(args[0], inbox, **kwargs)


def register_yambs_native(
    manager: TaskManager,
    project: str,
    cwd: Path,
    substitutions: Dict[str, str],
) -> bool:
    """Register project tasks to the manager."""

    register_docs(manager, project, cwd, substitutions)

    # Source a 'site.env' if one is present.
    try_source(cwd.joinpath("site.env"))

    deps: List[str] = []

    # Targets for generating and building.
    manager.register(Yambs("g", cwd), deps)
    manager.register(Yambs("go", cwd, once=True), deps)
    manager.register(Yambs("gb", cwd, once=True, build=True), deps)
    manager.register(Yambs("gw", cwd, watch=True), deps)

    gen_build = ["gb"]

    # Targets for running binaries.
    manager.register(YambsRunApp("r", cwd), gen_build)
    manager.register(YambsRunTest("t", cwd), gen_build)
    manager.register(YambsRunTest("t-{pattern}", cwd), gen_build)

    # Build a distribution.
    manager.register(YambsDist("dist"), gen_build)

    config = Native.load(
        path=cwd.joinpath(DEFAULT_CONFIG), package_config="native.yaml"
    )

    build = cwd.joinpath("build")

    # A target for hosting code coverage.
    register_http_server_task(
        manager,
        build.joinpath(substitutions.get("variant", "debug")).with_suffix(
            ".html"
        ),
        "hc",
        deps,
    )

    # Remove build variants.
    clean_dirs = [build.joinpath(x) for x in config.data["variants"]]
    clean_dirs += [x.with_suffix(".html") for x in clean_dirs]
    manager.register(Clean("c", *clean_dirs), deps)

    # Generate tags and edit.
    manager.register(GenerateTags("edit", cwd), deps)

    # Upload a release.
    manager.register(YambsUploadRelease("release-only", cwd))
    manager.register(YambsUploadRelease("release", cwd), ["dist"])

    # YAML linting.
    manager.register(
        Phony("yaml"),
        (
            []
            if is_windows()
            else [
                "yaml-lint-local",
                "yaml-lint-manifest.yaml",
                "yaml-lint-yambs.yaml",
            ]
        ),
    )

    # Register additional workflow tasks.
    for register in [
        register_toolchains,
        register_ifgen,
    ]:
        register(manager, project, cwd, substitutions)

    register_conntextual(manager, project, cwd, substitutions, prefix="wa")

    register_pico(manager, cwd)

    return True
