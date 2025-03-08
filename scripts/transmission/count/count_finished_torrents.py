import setup
from project_cli.subcommands import count_torrents, test_transmission_connection

from loguru import logger as log


def main(config_file: str = "configs/default.json"):
    log.info(f"Testing transmission connection")
    try:
        test_transmission_connection(config_file=config_file)
    except Exception as e:
        log.error(f"Failed to test transmission connection. Details: {e}")

    try:
        count_torrents(config_file=config_file, status="finished")
    except Exception as e:
        log.error(f"Failed to count all finished torrents. Details: {e}")


if __name__ == "__main__":
    setup.setup_loguru_logging(log_level="DEBUG", colorize=True)
    log.info("START count all finished torrents")

    main()
