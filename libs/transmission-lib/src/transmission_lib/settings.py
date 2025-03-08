from __future__ import annotations

from dataclasses import dataclass, field
import typing as t

__all__ = ["TransmissionClientSettings"]


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
