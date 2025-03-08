import setup
from project_cli.subcommands import (
    count_torrents,
    test_transmission_connection,
    delete_torrents,
)

from loguru import logger as log


def main(config_file: str = "configs/default.json"):
    log.info(f"Testing transmission connection")
    try:
        test_transmission_connection(config_file=config_file)
    except Exception as e:
        log.error(f"Failed to test transmission connection. Details: {e}")

    try:
        deleted_torrents = delete_torrents(config_file=config_file, status="finished")
    except Exception as e:
        log.error(f"Failed to delete finished torrents. Details: {e}")

    if len(deleted_torrents) == 0:
        log.info("No torrents were deleted")
    else:
        log.info(f"Deleted {len(deleted_torrents)} finished torrent(s)")


if __name__ == "__main__":

    setup.setup_loguru_logging(log_level="DEBUG", colorize=True)
    log.info("START delete finished torrents")

    main()
