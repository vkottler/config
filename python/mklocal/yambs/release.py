"""
A module for working with GitHub releases.
"""

# built-in
from json import loads
import os
from pathlib import Path
from typing import Any

# third-party
from vcorelib.task import Inbox, Outbox
from vmklib.tasks.github import COMMON_ARGS, ensure_api_token, repo_url
from vmklib.tasks.mixins import CurlMixin, curl_headers

# internal
from .base import YambsTask

ApiResult = dict[str, Any]


class YambsUploadRelease(YambsTask, CurlMixin):
    """A class for running the 'dist' command."""

    async def create_release(
        self, owner: str, repo: str, data: dict[str, Any]
    ) -> ApiResult:
        """Attempt to create a release."""

        result = await self.curl(
            *COMMON_ARGS, repo_url(owner, repo), post_data=data
        )
        return loads(result.stdout)  # type: ignore

    async def upload_release_asset(
        self, owner: str, repo: str, release_id: int, path: Path
    ) -> ApiResult:
        """Attempt to upload a release asset."""

        result = await self.curl(
            *COMMON_ARGS,
            (
                f"{repo_url(owner, repo, kind='uploads')}/{release_id}/assets"
                f"?name={path.name}"
            ),
            *curl_headers({"Content-Type": "application/octet-stream"}),
            "--data-binary",
            f"@{path}",
            method="POST",
        )
        return loads(result.stdout)  # type: ignore

    async def run(self, inbox: Inbox, outbox: Outbox, *args, **kwargs) -> bool:
        """Generate ninja configuration files."""

        # Check for API key in environment.
        if "GITHUB_API_TOKEN" not in os.environ:
            self.log.error(
                "Environment variable 'GITHUB_API_TOKEN' is not set!"
            )
            return False

        # Set token header.
        ensure_api_token(os.environ["GITHUB_API_TOKEN"])

        cwd: Path = args[0]

        # Load the project configuration.
        config = self.native_config(cwd)

        # Ensure GitHub parameters are set.
        if config.project.owner is None:
            self.log.error("'project.github.owner' not set in configuration!")
            return False

        # Attempt to create a new release.
        result = await self.create_release(
            config.project.owner,
            config.project.repo,
            {
                "tag_name": config.project.version,
                "generate_release_notes": True,
            },
        )
        if "message" in result and result["message"] == "Validation Failed":
            self.log.warning("Release at current version already exists.")
            return True

        release_id = result["id"]

        # Use 'Upload a release asset' API to upload all files in the 'dist'
        # directory to the new release.
        for item in cwd.joinpath("dist").iterdir():
            result = await self.upload_release_asset(
                config.project.owner, config.project.repo, release_id, item
            )
            self.log.info("Uploaded '%s'.", result["browser_download_url"])

        return True
