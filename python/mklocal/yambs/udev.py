"""
A module for udev-rule tasks.
"""

# built-in
from pathlib import Path

# third-party
from vcorelib.task.subprocess.run import SubprocessLogMixin


async def install_udev_rule(task: SubprocessLogMixin, path: Path) -> bool:
    """Install a udev rule."""

    result = True

    dst = Path("/usr/lib/udev/rules.d", path.name)
    if not dst.is_file():
        result &= await task.exec(
            "sudo", "ln", "-s", str(path.resolve()), str(dst)
        )
        result &= await task.exec(
            "sudo", "udevadm", "control", "--reload-rules"
        )
        result &= await task.exec("sudo", "udevadm", "trigger")

    return result
