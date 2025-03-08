from __future__ import annotations

import logging

from dataclasses import dataclass, field
import typing as t
import json

log = logging.getLogger(__name__)

__all__ = ["TransmissionClientSettings", "get_transmission_settings"]


@dataclass
class TransmissionClientSettings:
    """Dataclasss to store settings for Transmission RPC client.

    Attributes:
        host (str): Hostname of Transmission RPC server.
        port (int): Port of Transmission RPC server.
        protocol (str): Protocol of Transmission RPC server.
        path (str): RPC URL of Transmission RPC server.
        username (str): Username of Transmission RPC server.
        password (str): Password of Transmission RPC server.

    """

    host: t.Optional[str] = field(default=None)
    port: t.Union[str, int] = field(default=9091)
    protocol: str = field(default="http")
    path: str = field(default="/transmission/rpc")
    username: str = field(default=None)
    password: str = field(default=None, repr=False)


def load_config(config_file: str) -> dict:
    log.debug(f"Reading configuration from '{config_file}'")
    try:
        with open(config_file, "r") as f:
            config = json.load(f)

        return config
    except Exception as e:
        raise Exception(f"Failed to load config file: {e}")


def get_transmission_settings(config_file: str) -> TransmissionClientSettings:
    config = load_config(config_file)
    transmission_settings = TransmissionClientSettings(**config)

    return transmission_settings
