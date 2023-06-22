"""
A module for working with gcov outputs.
"""

# built-in
from pathlib import Path
from typing import Iterator


def gcov_data(root: Path) -> Iterator[Path]:
    """Find all gcov data files from a root directory."""

    for item in root.iterdir():
        if item.is_dir():
            yield from gcov_data(item)
        elif item.suffix == ".gcda":
            yield item


def remove_gcov_data(root: Path) -> None:
    """
    Remove all files ending in .gcda, starting from the provided directory.
    """
    for item in gcov_data(root):
        item.unlink()
