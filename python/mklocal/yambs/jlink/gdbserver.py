"""
A module for working with J-Link GDBServer.
"""

# built-in
from pathlib import Path

# internal
from . import JlinkTask

SWD_COMMON = ["-if", "SWD", "-speed", "auto"]

BOARD_ARGS = {
    "relax_kit": ["-device", "XMC4700-2048"] + SWD_COMMON,
    "grand_central": ["-device", "ATSAMD51P20A"] + SWD_COMMON,
    "pi_pico": ["-device", "RP2040_M0_0"] + SWD_COMMON,
}

PORTS = {"gdb": 2331, "swo": 2332, "telnet": 2333, "rtt": 19021}

COMMON_ARGS = [
    "-port",
    str(PORTS["gdb"]),
    "-swoport",
    str(PORTS["swo"]),
    "-telnetport",
    str(PORTS["telnet"]),
    "-RTTTelnetPort",
    str(PORTS["rtt"]),
    "-endian",
    "little",
    "-nogui",
    "-strict",
]


def jlink_gdbserver_task(
    board: str, third_party: Path, name: str = None
) -> JlinkTask:
    """Create a JLink GDB server task."""

    if name is None:
        name = board

    return JlinkTask(
        name,
        third_party,
        *BOARD_ARGS[board],
        *COMMON_ARGS,
        program="JLinkGDBServer"
    )
