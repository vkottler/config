"""
A module implementing interfaces for running test binaries.
"""

# built-in
import asyncio
from asyncio.subprocess import PIPE
import os
from pathlib import Path
from re import search
from typing import Tuple

# third-party
from vcorelib.asyncio.cli import ProcessResult, handle_process_cancel
from vcorelib.task import Inbox, Outbox

# internal
from .base import YambsTask


def test_name(path: Path) -> str:
    """wGet the name of a test script."""
    return path.with_suffix("").name


class YambsRunTest(YambsTask):
    """A class for running built-binary unit tests."""

    async def capture(
        self, path: Path, *args, shell: bool = False, **kwargs
    ) -> Tuple[str, ProcessResult]:
        """Run a subprocess and capture the output."""

        method = self.subprocess_shell if shell else self.subprocess_exec

        name = test_name(path)

        return name, await handle_process_cancel(
            await method(  # type: ignore
                str(path), *args, stdout=PIPE, stderr=PIPE, **kwargs
            ),
            name,
            self.logger,
        )

    async def run(self, inbox: Inbox, outbox: Outbox, *args, **kwargs) -> bool:
        """Run unit tests."""

        root: Path = args[0]
        data = self.apps(root)

        # Filter scripts by pattern.
        pattern = kwargs.get("pattern", ".*")

        # Run all the tests.
        result = await asyncio.gather(
            *(
                self.capture(test, env=os.environ)
                for test in [
                    test
                    # Aggregate scripts to run.
                    for test in [
                        Path(
                            data["all"][test_name]["variants"][
                                kwargs.get("variant", self.default_variant)
                            ]
                        )
                        for test_name in data["tests"]
                    ]
                    if search(pattern, test_name(test)) is not None
                ]
            )
        )

        # Check if all the tests pass.
        success = all(x.proc.returncode == 0 for _, x in result)

        # If any tests failed, print their output.
        if not success:
            for name, proc in result:
                if proc.proc.returncode != 0:
                    stdout = proc.stdout.decode()
                    if stdout:
                        print(f"(failed) '{name}' stdout:")
                        print(stdout, end="")

                    stderr = proc.stderr.decode()
                    if stderr:
                        print(f"(failed) '{name}' stderr:")
                        print(stderr, end="")

        return success
