import typing as t

import transmission_lib
import transmission_rpc

from cyclopts import App, Group, Parameter
from loguru import logger as log

__all__ = ["transmission_app", "test_transmission_connection"]

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
    ],
    host: t.Annotated[
        str, Parameter(["--host", "-H"], show_default=True)
    ] = "127.0.0.1",
    port: t.Annotated[int, Parameter(["--port", "-p"], show_default=True)] = 9091,
    username: t.Annotated[
        str, Parameter(["--username", "-u"], show_default=True)
    ] = None,
    password: t.Annotated[
        str, Parameter(["--password", "-pw"], show_default=True)
    ] = None,
    protocol: t.Annotated[
        str, Parameter(["--protocol", "-proto"], show_default=True)
    ] = "http",
    path: t.Annotated[
        str, Parameter(["--rpc-path", "-r"], show_default=True)
    ] = "/transmission/rpc",
):
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

    log.info(f"Connecting to Transmission on host '{transmission_settings.host}'")
    connect_success = transmission_controller.test_connection()

    if connect_success:
        log.success("Connection successful.")
    else:
        log.error("Connection failed.")
