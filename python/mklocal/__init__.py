"""
A module exposing task registration interfaces for different kinds of projects.
"""

# built-in
from pathlib import Path
from typing import Dict, List

# third-party
from vcorelib.task.manager import TaskManager
from vcorelib.task.subprocess.run import SubprocessShellStreamed
from yambs.config.common import DEFAULT_CONFIG
from yambs.config.native import Native

# internal
from .clean import Clean
from .env import try_source
from .yambs import Yambs, YambsRunApp, YambsRunTest


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

    # Targets for running binaries.
    manager.register(YambsRunApp("r", cwd), ["gb"])
    manager.register(YambsRunTest("t", cwd), ["gb"])
    manager.register(YambsRunTest("t-{pattern}", cwd), ["gb"])

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
    manager.register(
        Clean("c", *clean_dirs),
        deps,
    )

    return True
