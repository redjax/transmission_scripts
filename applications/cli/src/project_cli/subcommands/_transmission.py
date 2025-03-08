import typing as t

import transmission_lib
import transmission_rpc

from cyclopts import App, Group, Parameter
from loguru import logger as log

__all__ = ["transmission_app", "test_transmission_connection", "count_torrents"]

transmission_app = App(
    "transmission", group="transmission", help="Transmission RPC commands."
)


def return_controller(
    config_file: str,
    host: str,
    port: int,
    username: str,
    password: str,
    protocol: str,
    path: str,
) -> transmission_lib.TransmissionRPCController:
    if config_file:
        log.debug(f"Config file: {config_file}")

        transmission_settings: transmission_lib.TransmissionClientSettings = (
            transmission_lib.get_transmission_settings(config_file)
        )
    else:
        transmission_settings: transmission_lib.TransmissionClientSettings = (
            transmission_lib.TransmissionClientSettings(
                host=host,
                port=port,
                username=username,
                password=password,
                protocol=protocol,
                path=path,
            )
        )

    transmission_controller: transmission_lib.TransmissionRPCController = (
        transmission_lib.get_transmission_controller(
            transmission_settings=transmission_settings
        )
    )

    return transmission_controller


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
    ],
    host: t.Annotated[str, Parameter(["--host"], show_default=True)] = "127.0.0.1",
    port: t.Annotated[int, Parameter(["--port"], show_default=True)] = 9091,
    username: t.Annotated[str, Parameter(["--username"], show_default=True)] = None,
    password: t.Annotated[str, Parameter(["--password"], show_default=True)] = None,
    protocol: t.Annotated[str, Parameter(["--protocol"], show_default=True)] = "http",
    path: t.Annotated[
        str, Parameter(["--rpc-path"], show_default=True)
    ] = "/transmission/rpc",
):
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

    log.info(f"Connecting to Transmission on host '{transmission_controller.host}'")
    connect_success = transmission_controller.test_connection()

    if connect_success:
        log.success("Connection successful.")
    else:
        log.error("Connection failed.")


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
    ] = "/transmission/rpc",
    status: t.Annotated[str, Parameter(["--status"], help="Torrent status")] = "all",
):
    VALID_TORRENT_STATES: list = transmission_lib.TORRENT_STATES.copy() + [
        "finished",
        "completed",
    ]

    if (
        not (status == "all" or status == "finished")
        and status not in VALID_TORRENT_STATES
    ):
        log.error(
            f"Invalid torrent status: {status}. Must be one of: {VALID_TORRENT_STATES}"
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

    log.info(f"Connecting to Transmission on host '{transmission_controller.host}'")

    num_torrents: int = transmission_controller.count_torrents(status=status)
    if not status == "all":
        log.info(f"Found {num_torrents} {status} torrent(s)")
    else:
        log.info(f"Found {num_torrents} torrent(s)")
