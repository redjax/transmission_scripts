from __future__ import annotations

import random
import typing as t

from .controllers import TransmissionRPCController
from .settings import TransmissionClientSettings

from loguru import logger as log
import transmission_rpc
from transmission_rpc.torrent import File, FileStat, Torrent, Tracker, TrackerStats

__all__ = [
    "debug_print_torrent",
    "extract_fields",
    "prepare_torrent_dict",
    "select_random_torrent",
    "select_random_for_delete",
    "remove_finished",
    "select_finished",
    "get_transmission_controller",
    "get_transmission_client",
    "get_torrents",
    "select_random_torrent",
    "select_finished",
    "select_random_for_delete",
    "remove_finished",
]


def debug_print_torrent(torrent: Torrent = None) -> None:
    if not torrent:
        raise ValueError("Missing Torrent to debug")

    if not isinstance(torrent, Torrent):
        raise TypeError(
            f"Invalid type for torrent: ({type(torrent)}). Must be of type transmission_rpc.Torrent"
        )

    def loop_dict(torrent_dict: dict = None):
        for k, v in torrent_dict.items():
            if isinstance(torrent_dict[k], list):
                for i in torrent_dict[k]:
                    if isinstance(i, dict):
                        loop_dict(torrent_dict=i)
                    else:
                        log.debug(f"List [{k}] Value ({type(i)}): {i}")

            elif isinstance(torrent_dict[k], dict):
                loop_dict(torrent_dict=torrent_dict[k])

            else:
                log.debug(
                    f"Key: {k}, Value ({type(torrent_dict[k])}): {torrent_dict[k]}"
                )

    loop_dict(torrent.__dict__)


def extract_fields(
    _input: list[t.Union[FileStat, TrackerStats, Tracker]] = None,
) -> list[dict]:
    """Extract the .fields property from a list of FileStat, TrackerStats, or Trackers."""
    if not _input:
        raise ValueError("Missing input to extract values from")

    if not isinstance(_input, list):
        raise TypeError(f"Invalid type for input: ({type(_input)})")

    field_objects = []

    for i in _input:
        fields: dict = i.fields

        field_objects.append(fields)

    return field_objects


def prepare_torrent_dict(torrent: Torrent = None) -> dict:
    """Return a dict with only the values/fields I care about from a Torrent."""
    if not torrent:
        raise ValueError("Missing Torrent value")

    if not isinstance(torrent, Torrent):
        log.error(
            TypeError(
                f"Invalid type for torrent object: ({type(torrent)}). Must be of type transmission_rpc.Torrent"
            )
        )
        pass

    torrent_dict = {
        "id": torrent.id,
        "name": torrent.name,
        "activity_date": torrent.activity_date,
        "date_active": torrent.date_active,
        "date_added": torrent.date_added,
        "date_started": torrent.date_started,
        "done_date": torrent.done_date or None,
        "is_finished": torrent.is_finished,
        "corrupt_ever": torrent.corrupt_ever,
        # "creator": torrent.creator,
        "desired_available": torrent.desired_available,
        "download_dir": torrent.download_dir,
        "download_limit": torrent.download_limit,
        "download_limited": torrent.download_limited,
        "downloaded_ever": torrent.downloaded_ever,
        "downloading": torrent.downloading,
        "download_pending": torrent.download_pending,
        "edit_date": torrent.edit_date,
        "eta": torrent.eta,
        "eta_idle": torrent.eta_idle,
        "error": torrent.error,
        "error_string": torrent.error_string,
        # "file_stats": torrent.file_stats,
        # "file_stats": extract_fields(torrent.file_stats),
        # "files": torrent.files(),
        "files": torrent.files(),
        "hashString": torrent.hashString,
        "have_unchecked": torrent.have_unchecked,
        "have_valid": torrent.have_valid,
        "is_private": torrent.is_private,
        "is_stalled": torrent.is_stalled,
        "labels": torrent.labels,
        "left_until_done": torrent.left_until_done,
        "magnet_link": torrent.magnet_link,
        "max_connected_peers": torrent.max_connected_peers,
        "peer_limit": torrent.peer_limit,
        "peers": torrent.peers,
        "peers_connected": torrent.peers_connected,
        "peers_from": torrent.peers_from,
        "percent_done": torrent.percent_done,
        "queue_position": torrent.queue_position,
        "rate_download": torrent.rate_download,
        "rate_upload": torrent.rate_upload,
        "seconds_downloading": torrent.seconds_downloading,
        "seconds_seeding": torrent.seconds_seeding,
        "seed_idle_limit": torrent.seed_idle_limit,
        "size_when_done": torrent.size_when_done,
        "status": torrent.status,
        "torrent_file": torrent.torrent_file,
        "total_size": torrent.total_size,
        # "tracker_stats": torrent.tracker_stats,
        "tracker_stats": extract_fields(torrent.trackers),
        # "trackers": torrent.trackers,
        "trackers": extract_fields(torrent.trackers),
        "upload_limit": torrent.upload_limit,
        "upload_limited": torrent.upload_limited,
        "upload_ratio": torrent.upload_ratio,
        "uploaded_ever": torrent.uploaded_ever,
    }

    return torrent_dict


def get_transmission_controller(
    transmission_settings: TransmissionClientSettings | None = None,
    host: str | None = "127.0.0.1",
    port: t.Union[str, int] | None = 9091,
    username: str | None = None,
    password: str | None = None,
    protocol: str | None = "http",
    path: str | None = "/transmission/rpc",
):
    if transmission_settings is None:
        if any(
            conf is None for conf in [host, port, username, password, protocol, path]
        ):
            raise ValueError(
                "transmission_settings object is None, you must pass all connection values, but at least 1 parameter is None."
            )

    if transmission_settings:
        log.debug(
            "Detected TransmissionClientSettings object, using values from configuration."
        )
        _conf: dict[str, t.Union[str, int]] = {
            "host": transmission_settings.host,
            "port": transmission_settings.port,
            "username": transmission_settings.username,
            "password": transmission_settings.password,
            "path": transmission_settings.path,
            "protocol": transmission_settings.protocol,
        }

    else:
        _conf: dict[str, t.Union[str, int]] = {
            "host": host,
            "port": port,
            "username": username,
            "password": password,
            "path": path,
            "protocol": protocol,
        }

    try:
        _controller = TransmissionRPCController(
            host=_conf["host"],
            port=_conf["port"],
            username=_conf["username"],
            password=_conf["password"],
            path=_conf["path"],
            protocol=_conf["protocol"],
        )

        return _controller
    except Exception as exc:
        msg = f"({type(exc)}) Error initializing TransmissionRPCController. Details: {exc}"
        log.error(msg)

        raise exc


def get_transmission_client(
    transmission_settings: TransmissionClientSettings | None = None,
    host: str | None = "127.0.0.1",
    port: t.Union[str, int] | None = 9091,
    username: str | None = None,
    password: str | None = None,
    protocol: str | None = "http",
    path: str | None = "/transmission/rpc",
):
    """Return a configured transmission_rpc.Client object.

    Accepts a preconfigured _settings object. Uses Dynaconf to load configuration from environment.
    """
    if transmission_settings is None:
        if any(
            conf is None for conf in [host, port, username, password, protocol, path]
        ):
            raise ValueError(
                "transmission_settings object is None, you must pass all connection values, but at least 1 parameter is None."
            )

    if transmission_settings:
        log.debug(
            "Detected TransmissionClientSettings object, using values from configuration."
        )
        _conf: dict[str, t.Union[str, int]] = {
            "host": transmission_settings.host,
            "port": transmission_settings.port,
            "username": transmission_settings.username,
            "password": transmission_settings.password,
            "path": transmission_settings.path,
            "protocol": transmission_settings.protocol,
        }

    else:
        _conf: dict[str, t.Union[str, int]] = {
            "host": host,
            "port": port,
            "username": username,
            "password": password,
            "path": path,
            "protocol": protocol,
        }

    try:
        client = transmission_rpc.Client(**_conf)
    except Exception as exc:
        raise Exception(
            f"Unhandled exception getting Transmission RPC Client. Details: {exc}"
        )

    return client


def get_torrents(client: transmission_rpc.Client) -> list[Torrent]:
    """Get a list of finished torrents from remote."""
    with client as c:
        try:
            torrents = c.get_torrents()
        except Exception as exc:
            raise Exception(f"Unhandled exception getting torrents. Details: {exc}")

    return torrents


def select_random_torrent(torrents: list[Torrent] = []) -> Torrent:
    """Select a random Torrent from a list of Torrent objects.

    Checks length of list, choosees random number between 0..list_len, and
    returns torrent from list[random_number].
    """
    list_len = len(torrents)

    rand = random.randint(0, list_len)

    random_torrent = torrents[rand]

    return random_torrent


def select_finished(torrents: list[Torrent] = []) -> list[Torrent]:
    """Select all finished torrents from a list of Torrent objects."""
    if not torrents:
        raise ValueError("Torrent list cannot be empty")

    _finished: list[Torrent] = []

    for t in torrents:
        if t.is_finished:
            _finished.append(t)

    return _finished


def select_random_for_delete(
    finished: list[Torrent] = [], num: int = 3
) -> list[Torrent]:
    """Select 'num' random torrents for deletion.

    This function is a good middle-man while testing. Pass an int for num, and a list of Torrent objects,
    and the function will roll 'num' random numbers, then return a list of the torrents matching each roll's
    index in the finished list.
    """
    if not finished:
        raise ValueError("Missing input list of finished Torrents")

    if not isinstance(num, int):
        raise TypeError(f"Invalid type for num: {type(num)}. Must be of type int")
    if num < 0:
        raise ValueError(
            f"Invalid number of torrents to select: {num}. Must be a positive integer"
        )

    loop = num
    selections: list[Torrent] = []

    while loop > 0:
        _index = random.randint(0, len(finished))
        _torrent = finished[_index]
        selections.append(_torrent)

        loop -= 1

    return selections


def remove_finished(
    prompt: bool = False,
    finished: list[Torrent] = [],
    client: transmission_rpc.Client = None,
) -> list[Torrent]:
    """Loop over a list of torrents and remove from remote.

    If prompt = True, will prompt user with Y/N question and buffer to a list 'remove.'
    Function then loops over 'reomve' and deletes each torrent.

    If prompt = False, input list 'finished' becomes list 'remove.'

    Returns a list of removed torrents.
    """
    remove: list[Torrent] = []
    removed_success: list[Torrent] = []

    def build_remove_list(
        finished: list[Torrent] = finished,
        remove_list: list[Torrent] = remove,
        prompt=prompt,
    ) -> list[Torrent]:
        """Return a list of torrents to remove.

        This function acts as a check for the prompt value. If a prompt is enabled,
        loop over the list of torrents and offer a Y/N choice for each torrent before
        removing.
        """
        try:
            for t in finished:
                log_torrent = f"[({t.id}) - {t.name} (finished: {t.is_finished})]"

                if prompt:
                    is_valid = None

                    while not is_valid:
                        choice = input(f"Remove torrent {log_torrent}? (Y/N)")

                        match choice:
                            case "y" | "Y":
                                is_valid = True
                                delete = True
                            case "n" | "N":
                                is_valid = True
                                delete = False
                            case _:
                                is_valid = False
                                delete = False
                                print(
                                    ValueError(
                                        f"Invalid choice: '{choice}'. Must be 'Y' or 'N'"
                                    )
                                )

                    if delete:
                        remove_list.append(t)

                else:
                    remove_list = finished

            return remove_list

        except Exception as exc:
            raise Exception(
                f"Unhandled exception building list of Torrents to remove. Details: {exc}"
            )

    remove = build_remove_list()
    log.debug(f"Remove list: {remove}")

    for _t in remove:
        log_torrent = f"[{_t.id} - {_t.name}]"
        log.debug(f"Removing torrent: {log_torrent}")

        with client as c:
            try:
                c.remove_torrent(ids=[_t.id])
                removed_success.append(_t)

            except Exception as exc:
                log.error(f"Error removing torrent {log_torrent}. Details: {exc}")
                pass

    return removed_success
