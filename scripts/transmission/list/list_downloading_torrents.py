import setup
from project_cli.subcommands import list_torrents, test_transmission_connection

from loguru import logger as log


def main(config_file: str = "configs/default.json"):
    log.info(f"Testing transmission connection")
    try:
        test_transmission_connection(config_file=config_file)
    except Exception as e:
        log.error(f"Failed to test transmission connection. Details: {e}")

    try:
        torrents = list_torrents(config_file=config_file, status="downloading")
        log.info(
            f"Got {len(torrents)} downloading torrent(s) from host:\n{[t.name for t in torrents]}"
        )
    except Exception as e:
        log.error(f"Failed to get downloading torrent(s) from host. Details: {e}")
        return []


if __name__ == "__main__":
    setup.setup_loguru_logging(log_level="DEBUG", colorize=True)
    log.info("START count all torrents")

    main()
