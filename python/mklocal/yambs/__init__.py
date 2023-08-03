"""
A module implementing task interfaces for the yambs project.
"""

# built-in
from pathlib import Path
from typing import Dict, List

# isort: off

# third-party
from vcorelib.task import Inbox, Outbox
from vcorelib.task.manager import TaskManager
from vcorelib.task.subprocess.run import SubprocessShellStreamed
from yambs.config.common import DEFAULT_CONFIG
from yambs.config.native import Native

# isort: on

# internal
from mklocal.env import try_source
from vmklib.tasks.clean import Clean

from .base import YambsTask
from .dist import YambsDist
from .edit import GenerateTags
from .release import YambsUploadRelease
from .run import YambsRunApp
from .test import YambsRunTest

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

    del project

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
    cov = build.joinpath(substitutions.get("variant", "debug")).with_suffix(
        ".html"
    )
    manager.register(
        SubprocessShellStreamed(
            "hc", cmd=(f"cd {cov} && python -m http.server 0")
        ),
        deps,
    )

    # Remove build variants.
    clean_dirs = [build.joinpath(x) for x in config.data["variants"]]
    clean_dirs += [x.with_suffix(".html") for x in clean_dirs]
    manager.register(Clean("c", *clean_dirs), deps)

    # Generate tags and edit.
    manager.register(GenerateTags("edit", cwd), deps)

    # Upload a release.
    manager.register(YambsUploadRelease("release", cwd), ["dist"])

    return True
