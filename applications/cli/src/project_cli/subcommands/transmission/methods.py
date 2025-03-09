from loguru import logger as log

import transmission_lib

__all__ = ["return_controller", "test_connection"]


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


def test_connection(
    config_file: dict,
    host: str = "127.0.0.1",
    port: int = 9091,
    username: str | None = None,
    password: str | None = None,
    protocol: str | None = "http",
    path: str = "/transmission/rpc/",
) -> bool:
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
    try:
        connect_success = transmission_controller.test_connection()
    except Exception as exc:
        msg = f"({type(exc)}) Error testing connection. Details: {exc}"
        log.error(msg)

        connect_success = False

    if connect_success:
        log.success("Connection successful.")
    else:
        log.error("Connection failed.")

    return connect_success
