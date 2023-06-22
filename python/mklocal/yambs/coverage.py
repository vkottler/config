"""
A module for managing code-coverage interfaces.
"""

# built-in
from pathlib import Path
from typing import Set

# internal
from .base import YambsTask
from .gcov import remove_gcov_data


class CoverageManager:
    """A class facilitating HTML code-coverage generation."""

    def __init__(self, task: YambsTask, root: Path, variant: str) -> None:
        """Initialize this coverage manager."""

        self.task = task
        self.root = root
        self.variant = variant
        self.build_dir = self.task.build_dir(self.root, self.variant)

        self.info_files: Set[Path] = set()

        self.lcov_args = ["-q", "-d", str(self.build_dir)]

    async def init(self) -> None:
        """Initialize code-coverage gathering."""

        # Remove coverage from any previous run.
        remove_gcov_data(self.build_dir)

        # Initialize coverage data.
        info = self.build_dir.joinpath("base.info")
        await self.task.exec(
            "lcov", "-i", "-c", *self.lcov_args, "-o", str(info)
        )
        self.info_files.add(info)

    async def _finalize(self) -> Path:
        """Finalize .info data into a single file."""

        args = []
        while self.info_files:
            args.append("-a")
            args.append(str(self.info_files.pop()))

        final = self.build_dir.joinpath("final.info")
        await self.task.exec("lcov", *self.lcov_args, *args, "-o", str(final))
        return final

    async def generate(self) -> Path:
        """Generate final coverage data and HTML."""

        # Collect coverage from the run.
        info = self.build_dir.joinpath("run.info")
        await self.task.exec("lcov", "-c", *self.lcov_args, "-o", str(info))
        self.info_files.add(info)

        output = self.build_dir.with_suffix(".html")

        # Finalize coverage and generate HTML.
        await self.task.exec(
            "genhtml",
            "--dark-mode",
            "-q",
            "-o",
            str(output),
            str(await self._finalize()),
        )
        return output
