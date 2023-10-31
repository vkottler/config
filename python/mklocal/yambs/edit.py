"""
A module implementing a target for preparing tags for editing.
"""

# built-in
import os
from pathlib import Path
from typing import List

# third-party
from vcorelib.task import Inbox, Outbox

# internal
from .base import YambsTask


def get_extra_sources(root: Path) -> List[str]:
    """Add extra source directories that may be used."""

    result: List[str] = []

    for candidate in [
        ("pico-sdk", "src", "boards"),
        ("pico-sdk", "src", "common"),
        ("pico-sdk", "src", "rp2_common"),
        ("pico-sdk", "src", "rp2040"),
        ("RP2040-HAT-C",),
        ("ioLibrary_Driver", "Ethernet"),
        ("ioLibrary_Driver", "Internet", "DHCP"),
        ("ioLibrary_Driver", "Internet", "DNS"),
        # Create tags for this at some point?
        # ("pico-sdk", "lib", "tinyusb", "src"),
    ]:
        full = root.joinpath(*candidate)
        if full.is_dir():
            result.append(str(full))

    return result


class GenerateTags(YambsTask):
    """A class implementing a task for generating tags files."""

    default_editor = "vim"

    async def run(self, inbox: Inbox, outbox: Outbox, *args, **kwargs) -> bool:
        """Generate a tags files."""

        root: Path = args[0]

        # Remove existing tags.
        tags = root.joinpath("tags")
        tags.unlink(missing_ok=True)

        common = ["ctags", "-f", str(tags), "--languages=C,C++"]

        src = root.joinpath("src")

        sources = [str(src)] + get_extra_sources(root)

        # Tag third-party dependencies.
        third_party = root.joinpath("third-party", "include")
        if third_party.is_dir():
            sources.append(str(third_party))

        # Toolchains.
        toolchain = kwargs.get("toolchain", "arm-picolibc-eabi")
        toolchain_include = root.joinpath(
            "toolchains", toolchain, toolchain, "include"
        )
        if toolchain_include.is_dir():
            sources.append(str(toolchain_include))

        # Create initial tags file.
        result = await self.shell_cmd_in_dir(
            root,
            common
            + [f"--exclude={src.joinpath('third-party')}", "-R"]
            + sources,
        )

        # Run editor.
        if result and kwargs.get("edit", True):
            result = await self.shell_cmd_in_dir(
                root, [os.environ.get("EDITOR", self.default_editor)]
            )

        return result
