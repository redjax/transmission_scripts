from __future__ import annotations

from contextlib import AbstractContextManager
import logging
from pathlib import Path
import typing as t

from transmission_rpc.client import Client
from transmission_rpc.torrent import Torrent

log = logging.getLogger(__name__)

__all__ = ["TransmissionRPCController"]


class TransmissionRPCController(AbstractContextManager):
    def __init__(
        self,
        host: str | None = None,
        port: int = None,
        username: str = None,
        password: str = None,
        path: str = None,
        protocol: str = None,
        timeout: int | float | tuple[int | float, int | float] | None = None,
    ) -> None:
        self.host: str | None = host
        self.port: int | None = port
        self.username: str | None = username
        self.password: str | None = password
        self.path: str | None = path
        self.protocol: str | None = protocol
        self.timeout: int | float | tuple[int | float, int | float] | None = timeout

        self.client: Client | None = None

        self.logger: logging.Logger = log.getChild("TransmissionRPCController")

    def __enter__(self) -> "TransmissionRPCController":
        self.client = self._create_client()

        return self

    def __exit__(self, exc_type, exc_value, traceback) -> None:
        if traceback:
            pass

        if exc_type is not None:
            msg = f"Unhandled exception in TransmissionRPCController: {exc_value}"
            self.logger.error(msg)

    def _create_client(self) -> Client:
        """Create and return a configured transmission_rpc.Client object."""
        _conf: dict[str, t.Union[str, int]] = {
            "host": self.host,
            "port": self.port,
            "username": self.username,
            "password": self.password,
            "path": self.path,
            "protocol": self.protocol,
        }

        # Remove keys with None values to avoid passing them to Client
        _conf = {k: v for k, v in _conf.items() if v is not None}

        try:
            client = Client(**_conf)
        except Exception as exc:
            raise Exception(
                f"Unhandled exception getting Transmission RPC Client. Details: {exc}"
            )

        return client

    def _move_or_copy(
        self,
        ids: int | str | list[int] | list[str] = None,
        dest: str | Path = None,
        move: bool = False,
    ) -> bool:
        try:
            self.client.move_torrent_data(
                ids=ids, location=dest, timeout=self.timeout, move=move
            )

            return True
        except Exception as exc:
            msg = Exception(
                f"Unhandled exception {'moving' if move else 'copying'} torrent data to dest '{dest}'. Details: {exc}"
            )
            self.logger.error(msg)

            raise exc

    def test_connection(self) -> bool:
        try:
            with self as conn:
                log.debug("Successfully connected to Transmission RPC server")
                return True

        except Exception as exc:
            msg = Exception(
                f"Unhandled exception testing connection to Transmission RPC server. Details: {exc}"
            )
            self.logger.error(msg)

            return False

    def get_client(self) -> Client:
        """Return the Transmission RPC client."""
        if self.client is None:
            self.client = self._create_client()

        return self.client

    def get_all_torrents(self) -> list[Torrent]:
        if self.client is None:
            self.client = self._create_client()

        try:
            _torrents: list[Torrent] = self.client.get_torrents()

            return _torrents
        except Exception as exc:
            msg = Exception(f"Unhandled exception getting all torrents. Details: {exc}")
            self.logger.error(msg)

            raise exc

    def count_torrents(self, status: str = "all") -> int:
        if self.client is None:
            self.client = self._create_client()

        try:
            _torrents: list[Torrent] = self.client.get_torrents()
        except Exception as exc:
            msg = Exception(f"Unhandled exception getting all torrents. Details: {exc}")
            self.logger.error(msg)

            raise exc

        if status == "all":
            return len(_torrents)
        else:
            match status.lower():
                case "check pending":
                    pending_torrents = [
                        t for t in _torrents if t.status == "check pending"
                    ]
                    return len(pending_torrents)
                case "checking":
                    checking_torrents = [t for t in _torrents if t.status == "checking"]
                    return len(checking_torrents)
                case "downloading":
                    downloading_torrents = [
                        t for t in _torrents if t.status == "downloading"
                    ]
                    return len(downloading_torrents)
                case "download pending":
                    download_pending_torrents = [
                        t for t in _torrents if t.status == "download pending"
                    ]
                    return len(download_pending_torrents)
                case "seeding":
                    seeding_torrents = [t for t in _torrents if t.status == "seeding"]
                    return len(seeding_torrents)
                case "seed pending":
                    seed_pending_torrents = [
                        t for t in _torrents if t.status == "seed pending"
                    ]
                    return len(seed_pending_torrents)
                case "stopped":
                    stopped_torrents = [t for t in _torrents if t.status == "stopped"]
                    return len(stopped_torrents)
                case "finished" | "completed":
                    finished_torrents = [t for t in _torrents if t.done_date]
                    return len(finished_torrents)
                case _:
                    raise ValueError(f"Invalid state: {status}")

    def get_multiple_torrents(self, ids: list[str | int] = None) -> list[Torrent]:

        try:
            _torrents: list[Torrent] = self.client.get_torrents(
                ids=ids, timeout=self.timeout
            )

            return _torrents
        except Exception as exc:
            msg = Exception(f"Unhandled exception getting all torrents. Details: {exc}")
            self.logger.error(msg)

            raise exc

    def get_single_torrent(self, torrent_id: str | int = None):
        try:
            _torrent: Torrent = self.client.get_torrent(
                torrent_id=torrent_id, timeout=self.timeout
            )

            return _torrent
        except Exception as exc:
            msg = Exception(
                f"Unhandled exception getting torrent by ID '{torrent_id}'. Details: {exc}"
            )
            self.logger.error(msg)

            raise exc

    def move_torrent_data(
        self, ids: int | str | list[int] | list[str] = None, dest: str | Path = None
    ) -> bool:

        try:
            self._move_or_copy(ids=ids, dest=dest, move=True)
            return True
        except Exception as exc:
            log.error(f"({type(exc)}) Error moving torrent data. Details: {exc}")
            return False

        # try:
        #     self.client.move_torrent_data(
        #         ids=ids, location=dest, timeout=self.timeout, move=True
        #     )

        #     return True
        # except Exception as exc:
        #     msg = Exception(
        #         f"Unhandled exception moving torrent data to dest '{dest}'. Details: {exc}"
        #     )
        #     print(f"[ERROR] {msg}")

        #     raise exc

    def copy_torrent_data(
        self, ids: int | str | list[int] | list[str] = None, dest: str | Path = None
    ) -> bool:
        try:
            self._move_or_copy(ids=ids, dest=dest, move=False)
            return True
        except Exception as exc:
            log.error(f"({type(exc)}) Error copying torrent data. Details: {exc}")
            return False
        # try:
        #     self.client.move_torrent_data(
        #         ids=ids, location=dest, timeout=self.timeout, move=False
        #     )

        #     return True
        # except Exception as exc:
        #     msg = Exception(
        #         f"Unhandled exception moving torrent data to dest '{dest}'. Details: {exc}"
        #     )
        #     print(f"[ERROR] {msg}")

        #     raise exc

    def get_free_space(self, remote_path: str = "/") -> int | None:
        try:
            free_space: int | None = self.client.free_space(path=remote_path)

            return free_space
        except Exception as exc:
            msg = Exception(
                f"Unhandled exception getting free space at transmission remote. Details: {exc}"
            )
            log.error(msg)

            raise exc

    def get_recently_active(self) -> t.Tuple[t.List[Torrent] | t.List[int]]:
        recently_active: t.Tuple[t.List[Torrent] | t.List[int]] = (
            self.client.get_recently_active_torrents()
        )

        return recently_active

    def start_torrent(self, torrent: Torrent):
        try:
            self.client.start_torrent(torrent.id)
        except Exception as exc:
            msg = (
                f"({type(exc)}) Error starting torrent '{torrent.name}'. Details: {exc}"
            )
            log.error(msg)

            raise exc

    def start_torrent_by_id(self, torrent_id: int):
        try:
            self.client.start_torrent(torrent_id)
        except Exception as exc:
            msg = f"({type(exc)}) Error starting torrent '{torrent_id}'. Details: {exc}"
            log.error(msg)

            raise exc

    def stop_torrent(self, torrent: Torrent):
        try:
            self.client.stop_torrent(torrent.id)
        except Exception as exc:
            msg = (
                f"({type(exc)}) Error stopping torrent '{torrent.name}'. Details: {exc}"
            )
            log.error(msg)

            raise exc

    def stop_torrent_by_id(self, torrent_id: int):
        try:
            self.client.stop_torrent(torrent_id)
        except Exception as exc:
            msg = f"({type(exc)}) Error stopping torrent '{torrent_id}'. Details: {exc}"
            log.error(msg)

            raise exc

    def delete_torrent(self, torrent: Torrent, remove_files: bool = False) -> bool:
        """Delete a torrent by passing the Torrent object."""
        try:
            # Assuming 'torrent.id' is the unique identifier for the torrent
            torrent_id = torrent.id
            return self.delete_torrent_by_id(torrent_id, remove_files)
        except Exception as exc:
            msg = (
                f"({type(exc)}) Error deleting torrent '{torrent.name}'. Details: {exc}"
            )
            self.logger.error(msg)
            raise exc

    def delete_torrent_by_id(
        self,
        torrent_id: int | str | list[t.Union[str, int]],
        remove_files: bool = False,
    ) -> bool:
        """Delete a torrent by passing the torrent ID."""
        if not isinstance(torrent_id, list):
            torrent_id = [torrent_id]

        try:
            self.logger.info(f"Deleting torrent with ID '{torrent_id}'")

            # Assuming `self.client.remove_torrent()` is the method to delete torrents
            # If 'remove_files' is True, pass that flag to remove the data
            result = self.client.remove_torrent(torrent_id, delete_data=remove_files)

            if result:
                self.logger.info(f"Successfully deleted torrent with ID '{torrent_id}'")
                return True
            else:
                self.logger.error(f"Failed to delete torrent with ID '{torrent_id}'")
                return False
        except Exception as exc:
            msg = f"({type(exc)}) Error deleting torrent with ID '{torrent_id}'. Details: {exc}"
            self.logger.error(msg)
            raise exc
