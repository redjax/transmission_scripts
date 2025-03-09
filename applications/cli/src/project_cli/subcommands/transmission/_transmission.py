from __future__ import annotations

import typing as t

from cyclopts import App, Parameter
from loguru import logger as log
import transmission_lib
import transmission_rpc

from .methods import return_controller, test_connection, count, delete, _list

__all__ = [
    "transmission_app",
    "test_transmission_connection",
    "count_torrents",
    "delete_torrents",
    "list_torrents",
]

transmission_app = App(
    "transmission", group="transmission", help="Transmission RPC commands."
)


@transmission_app.command(
    name="test",
    group="transmission",
    help="Test connection to Transmission RPC server.",
)
def test_transmission_connection(
    config_file: t.Annotated[
        str,
        Parameter(
            ["--config-file", "-c"],
            show_default=True,
            help="Path to a JSON configuration file for the client",
        ),
    ] = "configs/default.json",
    host: t.Annotated[str, Parameter(["--host"], show_default=True)] = "127.0.0.1",
    port: t.Annotated[int, Parameter(["--port"], show_default=True)] = 9091,
    username: t.Annotated[str, Parameter(["--username"], show_default=True)] = None,
    password: t.Annotated[str, Parameter(["--password"], show_default=True)] = None,
    protocol: t.Annotated[str, Parameter(["--protocol"], show_default=True)] = "http",
    path: t.Annotated[
        str, Parameter(["--rpc-path"], show_default=True)
    ] = "/transmission/rpc/",
):
    connect_success = test_connection(
        config_file=config_file,
        host=host,
        port=port,
        username=username,
        password=password,
        protocol=protocol,
        path=path,
    )

    return connect_success


@transmission_app.command(
    name="count",
    group="transmission",
    help="Count torrents on remote host.",
)
def count_torrents(
    config_file: t.Annotated[
        str,
        Parameter(
            ["--config-file", "-c"],
            show_default=True,
            help="Path to a JSON configuration file for the client",
        ),
    ] = "configs/default.json",
    host: t.Annotated[str, Parameter(["--host"], show_default=True)] = "127.0.0.1",
    port: t.Annotated[int, Parameter(["--port"], show_default=True)] = 9091,
    username: t.Annotated[str, Parameter(["--username"], show_default=True)] = None,
    password: t.Annotated[str, Parameter(["--password"], show_default=True)] = None,
    protocol: t.Annotated[str, Parameter(["--protocol"], show_default=True)] = "http",
    path: t.Annotated[
        str, Parameter(["--rpc-path"], show_default=True)
    ] = "/transmission/rpc/",
    status: t.Annotated[str, Parameter(["--status"], help="Torrent status")] = "all",
):
    log.info("Counting torrents in remote Transmission")
    num_torrents: int = count(
        config_file=config_file,
        host=host,
        port=port,
        username=username,
        password=password,
        protocol=protocol,
        path=path,
    )

    if not status == "all":
        log.info(f"Found {num_torrents} {status} torrent(s)")
    else:
        log.info(f"Found {num_torrents} torrent(s)")

    return num_torrents


@transmission_app.command(
    name=["delete", "rm"], group="transmission", help="Delete torrents."
)
def delete_torrents(
    config_file: t.Annotated[
        str,
        Parameter(
            ["--config-file", "-c"],
            show_default=True,
            help="Path to a JSON configuration file for the client",
        ),
    ] = "configs/default.json",
    host: t.Annotated[str, Parameter(["--host"], show_default=True)] = "127.0.0.1",
    port: t.Annotated[int, Parameter(["--port"], show_default=True)] = 9091,
    username: t.Annotated[str, Parameter(["--username"], show_default=True)] = None,
    password: t.Annotated[str, Parameter(["--password"], show_default=True)] = None,
    protocol: t.Annotated[str, Parameter(["--protocol"], show_default=True)] = "http",
    path: t.Annotated[
        str, Parameter(["--rpc-path"], show_default=True)
    ] = "/transmission/rpc/",
    torrent_id: t.Annotated[int, Parameter(["--id"], show_default=True)] | None = None,
    status: t.Annotated[
        str, Parameter(["--status"], show_default=True, help="Torrent status")
    ] = "all",
    delete_data: t.Annotated[
        bool,
        Parameter(
            ["--delete-data", "--rm-data"],
            show_default=True,
            help="Delete torrent data (files, etc.)",
        ),
    ] = False,
    dry_run: t.Annotated[
        bool,
        Parameter(
            ["--dry-run"],
            show_default=True,
            help="Do a dry run, where no 'live' actions are taken (read-only operations permitted).",
        ),
    ] = False,
) -> list[transmission_rpc.Torrent]:
    try:
        deleted_torrents: list[transmission_rpc.Torrent] = delete(
            config_file=config_file,
            host=host,
            port=port,
            username=username,
            password=password,
            protocol=protocol,
            path=path,
            torrent_id=torrent_id,
            status=status,
            delete_data=delete_data,
            dry_run=dry_run,
        )

        log.info(f"Deleted torrents ({len(deleted_torrents)}): {deleted_torrents}")

        return deleted_torrents
    except Exception as e:
        log.error(f"Error deleting torrent(s): {e}")
        return []


@transmission_app.command(
    name=["list", "show"],
    group="transmission",
    help="List torrents. Optional status filtering (e.g. 'finished', 'downloading', 'seeding', etc).",
)
def list_torrents(
    config_file: t.Annotated[
        str,
        Parameter(
            ["--config-file", "-c"],
            show_default=True,
            help="Path to a JSON configuration file for the client",
        ),
    ] = "configs/default.json",
    host: t.Annotated[str, Parameter(["--host"], show_default=True)] = "127.0.0.1",
    port: t.Annotated[int, Parameter(["--port"], show_default=True)] = 9091,
    username: t.Annotated[str, Parameter(["--username"], show_default=True)] = None,
    password: t.Annotated[str, Parameter(["--password"], show_default=True)] = None,
    protocol: t.Annotated[str, Parameter(["--protocol"], show_default=True)] = "http",
    path: t.Annotated[
        str, Parameter(["--rpc-path"], show_default=True)
    ] = "/transmission/rpc",
    status: t.Annotated[
        str, Parameter(["--status"], show_default=True, help="Torrent status")
    ] = "all",
) -> list[transmission_rpc.Torrent]:
    torrents = _list(
        config_file=config_file,
        host=host,
        port=port,
        username=username,
        password=password,
        protocol=protocol,
        path=path,
        status=status,
    )

    return torrents
