from loguru import logger as log

import transmission_lib
import transmission_rpc

__all__ = ["return_controller", "test_connection", "count", "delete", "_list"]


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


def count(
    config_file: str = "configs/default.json",
    host: str = "127.0.0.1",
    port: int = 9091,
    username: str | None = None,
    password: str | None = None,
    protocol: str = "http",
    path: str = "/transmission/rpc/",
    status: str = "all",
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

    log.debug(
        f"Counting torrent(s){' with status: ' + status if not status == 'all' else ''} on host '{transmission_controller.host}'"
    )

    num_torrents: int = transmission_controller.count_torrents(status=status)
    log.debug(f"[STATUS: {status}, COUNT: {num_torrents}]")

    return num_torrents


def delete(
    config_file: str = "configs/default.json",
    host: str = "127.0.0.1",
    port: int = 9091,
    username: str | None = None,
    password: str | None = None,
    protocol: str = "http",
    path: str = "/transmission/rpc/",
    torrent_id: int | None = None,
    status: str = "all",
    delete_data: bool = False,
    dry_run: bool = False,
) -> list[transmission_rpc.Torrent]:
    if not torrent_id:
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

    if torrent_id:
        log.debug(
            f"Deleting torrent with ID '{torrent_id}' on host '{transmission_controller.host}'"
        )

        if dry_run:
            log.info(
                f"Dry run complete. {len(delete_torrents)} torrent(s) would have been deleted."
            )

            return []

        delete_torrents: list[transmission_rpc.Torrent] = (
            transmission_controller.delete_torrent_by_id(
                torrent_id=torrent_id, remove_files=delete_data
            )
        )

        return delete_torrents

    log.debug(
        f"Deleting torrent(s){' with status: ' + status if not status == 'all' else ''} on host '{transmission_controller.host}'"
    )

    if dry_run:
        log.info(
            f"Dry run complete. {len(delete_torrents)} torrent(s) would have been deleted."
        )

        return []

    delete_torrents: list[transmission_rpc.Torrent] = (
        transmission_controller.delete_torrent_by_status(
            status=status, remove_files=delete_data, dry_run=dry_run
        )
    )

    log.debug(
        f"Deleted {len(delete_torrents)}{f' with status: {status}' if not status == 'all' else ''} torrent(s)"
    )

    return delete_torrents


def _list(
    config_file: str = "configs/default.json",
    host: str = "127.0.0.1",
    port: int = 9091,
    username: str | None = None,
    password: str | None = None,
    protocol: str | None = "http",
    path: str = "/transmission/rpc",
    status: str = "all",
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

    log.debug(
        f"Getting torrent(s){' with status: ' + status if not status == 'all' else ''} from host '{transmission_controller.host}'"
    )

    torrents: list[transmission_rpc.Torrent] = (
        transmission_controller.get_all_torrents()
    )

    if not status == "all":
        filtered_torrents = [t for t in torrents if t.status == status]
        torrents = filtered_torrents

    if status == "finished":
        filtered_torrents = [t for t in torrents if t.done_date]
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
