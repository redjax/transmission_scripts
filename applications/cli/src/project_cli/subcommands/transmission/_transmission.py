from __future__ import annotations

import typing as t

from cyclopts import App, Parameter
from loguru import logger as log
import transmission_lib
import transmission_rpc

from .methods import return_controller, test_connection

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
    ],
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

    if (
        not (status == "all" or status == "finished")
        and status not in transmission_lib.VALID_TORRENT_STATES
    ):
        log.error(
            f"Invalid torrent status: {status}. Must be one of: {transmission_lib.VALID_TORRENT_STATES}"
        )
        return

    transmission_controller: transmission_lib.TransmissionRPCController = (
        return_controller(
            config_file,
            host,
            port,
            username,
            password,
            protocol,
            path,
        )
    )

    log.info(
        f"Counting torrent(s){' with status: ' + status if not status == 'all' else ''} on host '{transmission_controller.host}'"
    )

    num_torrents: int = transmission_controller.count_torrents(status=status)
    if not status == "all":
        log.info(f"Found {num_torrents} {status} torrent(s)")
    else:
        log.info(f"Found {num_torrents} torrent(s)")


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
    ],
    host: t.Annotated[str, Parameter(["--host"], show_default=True)] = "127.0.0.1",
    port: t.Annotated[int, Parameter(["--port"], show_default=True)] = 9091,
    username: t.Annotated[str, Parameter(["--username"], show_default=True)] = None,
    password: t.Annotated[str, Parameter(["--password"], show_default=True)] = None,
    protocol: t.Annotated[str, Parameter(["--protocol"], show_default=True)] = "http",
    path: t.Annotated[
        str, Parameter(["--rpc-path"], show_default=True)
    ] = "/transmission/rpc/",
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
    if (
        not (status == "all" or status == "finished")
        and status not in transmission_lib.VALID_TORRENT_STATES
    ):
        log.error(
            f"Invalid torrent status: {status}. Must be one of: {transmission_lib.VALID_TORRENT_STATES}"
        )
        return []

    transmission_controller: transmission_lib.TransmissionRPCController = (
        return_controller(
            config_file,
            host,
            port,
            username,
            password,
            protocol,
            path,
        )
    )

    log.info(
        f"Deleting torrent(s){' with status: ' + status if not status == 'all' else ''} on host '{transmission_controller.host}'"
    )

    delete_torrents: list[transmission_rpc.Torrent] = (
        transmission_controller.delete_torrent_by_status(
            status=status, remove_files=delete_data, dry_run=dry_run
        )
    )

    if dry_run:
        log.info(
            f"Dry run complete. {len(delete_torrents)} torrent(s) would have been deleted."
        )

        return []

    log.info(
        f"Deleted {len(delete_torrents)}{f' with status: {status}' if not status == 'all' else ''} torrent(s)"
    )

    return delete_torrents


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
    ] = "/transmission/rpc/",
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
) -> list[transmission_rpc.Torrent]:
    if (
        not (status == "all" or status == "finished")
        and status not in transmission_lib.VALID_TORRENT_STATES
    ):
        log.error(
            f"Invalid torrent status: {status}. Must be one of: {transmission_lib.VALID_TORRENT_STATES}"
        )
        return []

    transmission_controller: transmission_lib.TransmissionRPCController = (
        return_controller(
            config_file,
            host,
            port,
            username,
            password,
            protocol,
            path,
        )
    )

    log.info(
        f"Getting torrent(s){' with status: ' + status if not status == 'all' else ''} from host '{transmission_controller.host}'"
    )

    torrents: list[transmission_rpc.Torrent] = (
        transmission_controller.get_all_torrents()
    )

    if not status == "all":
        filtered_torrents = [t for t in torrents if t.status == status]
        torrents = filtered_torrents

    if len(torrents) == 0:
        log.info(
            f"No torrents{ ' with status: ' + status if not status == 'all' else ''} found on host '{transmission_controller.host}'"
        )
        return []

    log.info(
        f"Torrent(s) {len(torrents)}{f' with status: {status}' if not status == 'all' else ''}: {[t.name for t in torrents]}"
    )

    return torrents
