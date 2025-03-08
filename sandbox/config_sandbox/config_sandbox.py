from __future__ import annotations

import json

from loguru import logger as log
import setup

TRANSMISSION_CONFIG_FILE: str = "configs/ultraseedbox.json"


if __name__ == "__main__":
    setup.setup_loguru_logging(log_level="DEBUG", colorize=True)
    log.info("START config sandbox")

    log.info(f"Reading configuration from '{TRANSMISSION_CONFIG_FILE}'")
    with open(TRANSMISSION_CONFIG_FILE, "r") as f:
        transmission_config = json.load(f)

    log.info(f"Loaded config: {transmission_config}")
