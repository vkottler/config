"""
A module for project-specific SEGGER J-Link tasks.
"""

# built-in
from pathlib import Path
from typing import Optional

# third-party
from vcorelib.io.archive import extractall
from vcorelib.task import Inbox, Outbox
from vcorelib.task.manager import TaskManager
from vcorelib.task.subprocess.run import SubprocessLogMixin

# internal
from ..common import add_path, add_program_path
from ..udev import install_udev_rule

JLINK_URL = "https://www.segger.com/downloads/jlink"

OS = "Linux"
ARCH = "x86_64"
TYPE = "tgz"
JLINK_PKG = f"JLink_{OS}_{ARCH}.{TYPE}"


def find_jlink_dir(path: Path) -> Optional[Path]:
    """Find the JLink extracted software directory."""

    result = None

    for item in path.iterdir():
        if item.name.startswith("JLink"):
            result = path.joinpath(item)
            return result

    return None


class JlinkExtract(SubprocessLogMixin):
    """A class for extracting J-Link software."""

    async def run(self, inbox: Inbox, outbox: Outbox, *args, **kwargs) -> bool:
        """Run the task."""

        third_party = args[0]

        archive = third_party.joinpath("tarballs", JLINK_PKG)

        result = True

        if not archive.is_file():
            archive.parent.mkdir(parents=True, exist_ok=True)
            result &= await self.exec(
                "wget",
                "--post-data=accept_license_agreement=accepted"
                "&non_emb_ctr=confirmed&submit=Download+software",
                f"{JLINK_URL}/{JLINK_PKG}",
                "-O",
                archive,
            )

        jlink_dir = find_jlink_dir(third_party)
        if jlink_dir is not None:
            outbox["dir"] = jlink_dir
        elif result:
            extractall(archive, dst=third_party)
            outbox["dir"] = find_jlink_dir(third_party)

        link = third_party.joinpath("jlink")
        if not link.is_symlink() and outbox["dir"] is not None:
            link.symlink_to(outbox["dir"], target_is_directory=True)

        if link.is_symlink():
            await install_udev_rule(self, link.joinpath("99-jlink.rules"))

        return outbox["dir"] is not None and result


class JlinkTask(SubprocessLogMixin):
    """A class for running J-Link software."""

    default_requirements = {"vmklib.init", "extract-jlink"}

    async def run(self, inbox: Inbox, outbox: Outbox, *args, **kwargs) -> bool:
        """Run the task."""

        third_party = args[0]
        return await self.exec(
            third_party.joinpath("jlink", kwargs["program"]), *args[1:]
        )


def register_jlink(manager: TaskManager, third_party: Path) -> bool:
    """Register SEGGER JLink-related tasks."""

    manager.register(JlinkExtract("extract-jlink", third_party), [])
    jlink = third_party.joinpath("jlink")

    # Add useful references to programs.
    add_path(jlink)
    for jlink_prog in ["JLinkGDBServer"]:
        add_program_path(jlink_prog, jlink)

    manager.register(JlinkTask("jlink-{program}", third_party), [])

    return True
