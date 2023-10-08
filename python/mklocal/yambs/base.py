"""
A module implementing task interfaces for the yambs project.
"""

# built-in
from functools import lru_cache
from pathlib import Path
from typing import Any, Dict

# isort: off

# third-party
from vcorelib.io import ARBITER
from vcorelib.task import Inbox
from vcorelib.task.subprocess.run import SubprocessLogMixin
from yambs.config.native import Native, load_native

# isort: on


class YambsTask(SubprocessLogMixin):
    """A task for generating ninja configurations."""

    default_requirements = {"vmklib.init", "venv", "python-install-yambs"}

    default_variant = "debug"

    @lru_cache(1)
    def apps(self, root: Path) -> Dict[str, Any]:
        """Load data about applications."""
        return ARBITER.decode(
            root.joinpath("ninja", "apps.json"), require_success=True
        ).data

    @lru_cache(1)
    def native_config(self, root: Path) -> Native:
        """Load a configuration for a native-build project."""
        return load_native(root=root)

    def build_dir(self, root: Path, variant: str) -> Path:
        """Get the path to a variant's build directory."""
        return root.joinpath("build", variant)

    def python_script(self, entry: str, inbox: Inbox) -> str:
        """Get the path to a python script in the virtual environment."""
        return str(
            inbox["venv"]["venv{python_version}"]["bin"].joinpath(entry)
        )

    def mbs(self, inbox: Inbox) -> str:
        """Get the path to the 'mbs' entry script."""
        return self.python_script("mbs", inbox)

    async def handle_build(
        self,
        *args,
        build: bool = True,
        ninja: str = "ninja",
        target: str = None,
    ) -> bool:
        """Attempt a ninja command."""

        result = True
        if build:
            all_args = [*args]
            if target is not None:
                all_args.append(target)

            result = await self.exec(ninja, *all_args)
        return result

    async def run_generate_build(
        self, root: Path, inbox: Inbox, **kwargs
    ) -> bool:
        """Attempt to generate ninja files and/or build."""

        result = True

        if not (
            kwargs.get("once", False)
            and root.joinpath("build.ninja").is_file()
        ):
            params = [kwargs.get("command", "native")]
            if kwargs.get("watch", False):
                params.append("-w")

            result = await self.exec(self.mbs(inbox), "-C", str(root), *params)

        if result:
            result = await self.handle_build(
                build=kwargs.get("build", False),
                ninja=kwargs.get("ninja", "ninja"),
                target=kwargs.get("variant"),
            )

        return result
