from __future__ import annotations

import json

from loguru import logger as log
import setup
import transmission_lib

TRANSMISSION_CONFIG_FILE: str = "configs/default.json"


def load_config(config_file: str) -> dict:
    log.debug(f"Reading configuration from '{config_file}'")
    with open(config_file, "r") as f:
        config = json.load(f)

    return config


def main(config_file: str):
    config: dict = load_config(config_file)

    transmission_settings = transmission_lib.TransmissionClientSettings(**config)
    log.debug(f"Loaded Transmission settings: {transmission_settings}")

    transmission_controller: transmission_lib.TransmissionRPCController = (
        transmission_lib.get_transmission_controller(
            transmission_settings=transmission_settings
        )
    )

    log.info(f"Connecting to Transmission on host '{transmission_settings.host}'")
    connect_success = transmission_controller.test_connection()
    log.info(f"Successful connection: {connect_success}")


if __name__ == "__main__":
    setup.setup_loguru_logging(log_level="DEBUG", colorize=True)
    log.info("START config sandbox")

    main(config_file=TRANSMISSION_CONFIG_FILE)
