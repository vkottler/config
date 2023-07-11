"""
A module for working with GitHub releases.
"""

# built-in
from asyncio import subprocess
from json import loads
from typing import Any, NamedTuple, Optional

# third-party
import requests
from vcorelib.asyncio.cli import handle_process_cancel
from vcorelib.task import Inbox, Outbox

# internal
from .base import YambsTask


def latest_release(owner: str, repo: str) -> Optional[dict[str, Any]]:
    """Attempt to get the latest release metadata from a GitHub repository."""

    result = None

    response = requests.get(
        f"https://api.github.com/repos/{owner}/{repo}/releases/latest",
        headers={"Accept": "application/vnd.github+json"},
        timeout=10,
    )
    if response.ok:
        result = response.json()

    return result


class CommandResult(NamedTuple):
    """A container for a system command result."""

    code: int
    stdout: str
    stderr: str


def repo_url(
    owner: str, repo: str, kind: str = "api", endpoint: str = "releases"
) -> str:
    """Get a GitHub API URL."""
    return f"https://{kind}.github.com/repos/{owner}/{repo}/{endpoint}"


class YambsUploadRelease(YambsTask):
    """A class for running the 'dist' command."""

    curl_args = [
        "-L",
        "-H",
        "Accept: application/vnd.github+json",
        "-H",
        "X-GitHub-Api-Version: 2022-11-28",
    ]

    async def run_curl(self, *args: str) -> CommandResult:
        """Run a curl command."""

        proc, stdout, stderr = await handle_process_cancel(
            await self.subprocess_exec(
                "curl",
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

    async def latest_release(self, owner: str, repo: str) -> dict[str, Any]:
        """Attempt to get the latest GitHub release for a repository."""

        result = await self.run_curl(
            *self.curl_args,
            f"{repo_url(owner, repo)}/latest",
        )
        return loads(result.stdout)  # type: ignore

    async def run(self, inbox: Inbox, outbox: Outbox, *args, **kwargs) -> bool:
        """Generate ninja configuration files."""

        # Need to get project metadata - repo owner and name.

        latest = await self.latest_release("vkottler", "yambs-sample")

        if latest.get("message", "") == "Not Found":
            self.log.warning("No latest release found.")

        # Check if the current version is newer than the latest release, if
        # not, skip creating a new release.
        else:
            pass

        # Create a release with the 'Create a release' API.

        # Use 'Upload a release asset' API to upload all files in the 'dist'
        # directory to the new release.

        return False
