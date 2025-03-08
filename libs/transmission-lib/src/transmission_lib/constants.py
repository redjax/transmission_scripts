from __future__ import annotations

__all__ = ["TORRENT_STATES"]

TORRENT_STATES: list[str] = [
    "check pending",
    "checking",
    "downloading",
    "download pending",
    "seeding",
    "seed pending",
    "stopped",
]
