"""
A module for working with GitHub APIs.
"""

# internal
from .curl import curl_headers


def repo_url(
    owner: str, repo: str, kind: str = "api", endpoint: str = "releases"
) -> str:
    """Get a GitHub API URL."""
    return f"https://{kind}.github.com/repos/{owner}/{repo}/{endpoint}"


API_VERSION = "2022-11-28"
COMMON_ARGS = ["-L"] + list(
    curl_headers(
        {
            "Accept": "application/vnd.github+json",
            "X-GitHub-Api-Version": API_VERSION,
        }
    )
)
TOKEN_ADDED = False


def ensure_api_token(token: str) -> None:
    """Ensure the API token header is added to the curl arguments."""

    global TOKEN_ADDED  # pylint: disable=global-statement
    if TOKEN_ADDED:
        return

    COMMON_ARGS.extend(
        list(curl_headers({"Authorization": f"Bearer {token}"}))
    )
    TOKEN_ADDED = True
