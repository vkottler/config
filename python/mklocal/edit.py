"""
A module implementing a target for preparing tags for editing.
"""

# built-in
import os
from pathlib import Path

# third-party
from vcorelib.paths import rel
from vcorelib.task import Inbox, Outbox
from vcorelib.task.subprocess.run import SubprocessLogMixin

# internal
from mklocal.env import real_sources


class GenerateTags(SubprocessLogMixin):
    """A class implementing a task for generating tags files."""

    default_editor = "vim"
    languages = "C,C++"

    extra_source_candidates = [
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
    ]
    extra_excludes: list[tuple[str, ...]] = []

    async def run(self, inbox: Inbox, outbox: Outbox, *args, **kwargs) -> bool:
        """Generate a tags files."""

        root: Path = args[0]

        # Remove existing tags.
        tags = root.joinpath("tags")
        tags.unlink(missing_ok=True)

        common = [
            "ctags",
            "-f",
            str(rel(tags, base=root)),
            f"--languages={self.languages}",
        ]

        src = root.joinpath("src")

        # Standard source paths.
        sources = [src]

        # Additional source paths.
        sources += list(real_sources(root, self.extra_source_candidates))

        # Tag third-party dependencies.
        third_party = root.joinpath("third-party", "include")
        if third_party.is_dir():
            sources.append(third_party)

        # Toolchains.
        toolchain = kwargs.get("toolchain", "arm-picolibc-eabi")
        toolchain_include = root.joinpath(
            "toolchains", toolchain, toolchain, "include"
        )
        if toolchain_include.is_dir():
            sources.append(toolchain_include)

        result = True

        if sources:
            # Standard excludes.
            excludes = [
                x
                for x in [
                    src.joinpath("third-party"),
                    src.joinpath("data"),
                    root.joinpath("tests", "data"),
                ]
                if x.is_dir()
            ]

            # Create initial tags file.
            result = await self.shell_cmd_in_dir(
                root,
                common
                + list(
                    f"--exclude={rel(x, base=root)}"
                    for x in excludes
                    + list(real_sources(root, self.extra_excludes))
                )
                + ["-R"]
                + list(str(rel(x, base=root)) for x in sources),
            )

        # Run editor.
        if result and kwargs.get("edit", True):
            result = await self.shell_cmd_in_dir(
                root, [os.environ.get("EDITOR", self.default_editor)]
            )

        return result
