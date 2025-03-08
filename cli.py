from __future__ import annotations

from cyclopts import App
from loguru import logger as log
from project_cli import app as cli_app
import setup


def start_cli(app: App):
    try:
        app.meta()
    except Exception as exc:
        msg = f"({type(exc)}) error"
        log.error(msg)

        raise exc


if __name__ == "__main__":
    setup.setup_loguru_logging(log_level="ERROR", log_fmt="basic", colorize=True)
    start_cli(app=cli_app)
