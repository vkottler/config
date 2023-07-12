"""
A module for working with curl commands.
"""

# built-in
from asyncio import subprocess
from json import dumps
from typing import Any, Dict, Iterator, NamedTuple

# third-party
from vcorelib.asyncio.cli import handle_process_cancel
from vcorelib.task.subprocess.run import SubprocessLogMixin


class CommandResult(NamedTuple):
    """A container for a system command result."""

    code: int
    stdout: str
    stderr: str


def curl_headers(data: dict[str, str]) -> Iterator[str]:
    """Get header arguments for curl based on some header data."""

    for key, value in data.items():
        yield "-H"
        yield f"{key}: {value}"


class CurlMixin(SubprocessLogMixin):
    """A task for generating ninja configurations."""

    async def curl(
        self,
        *args: str,
        post_data: Dict[str, Any] = None,
        method: str = None,
    ) -> CommandResult:
        """Run a curl command."""

        extra_args = []

        if post_data is not None:
            extra_args.extend(["-d", dumps(post_data)])
            if method is None:
                method = "POST"
            assert method == "POST"

        if method is not None:
            extra_args.extend(["-X", method])

        proc, stdout, stderr = await handle_process_cancel(
            await self.subprocess_exec(
                "curl",
                *extra_args,
                *args,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
            ),
            self.name,
            self.log,
        )

        assert proc.returncode is not None
        assert stdout is not None
        assert stderr is not None

        return CommandResult(proc.returncode, stdout.decode(), stderr.decode())
