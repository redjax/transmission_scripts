import setup

from loguru import logger as log

if __name__ == "__main__":
    setup.setup_loguru_logging(log_level="DEBUG", colorize=True)
    log.info("START config sandbox")
