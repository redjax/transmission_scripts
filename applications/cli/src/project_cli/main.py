import sys
import typing as t

from .subcommands import transmission_app

from cyclopts import App, Group, Parameter
from loguru import logger as log

__all__ = ["app"]

app = App(
    name="transmission_scripts",
    help="CLI for controlling a remote Transmission client.",
)

app.meta.group_parameters = Group("Session Parameters", sort_key=0)

MOUNT_SUB_CLIS: list = [transmission_app]

for sub_cli in MOUNT_SUB_CLIS:
    app.command(sub_cli)


@app.meta.default
def cli_launcher(
    *tokens: t.Annotated[str, Parameter(show=False, allow_leading_hyphen=True)],
    debug: t.Annotated[
        bool, Parameter("--debug", show_default=True, help="Enable debug logging.")
    ] = False,
    log_file: (
        t.Annotated[
            str,
            Parameter(
                "--log-file",
                show_default=True,
                help="Path to a file where logs will be saved. Default is None.",
            ),
        ]
        | None
    ) = None,
):
    """CLI entrypoint.

    Params:
        debug (bool): If `True`, enables debug logging.
    """
    # log.remove(0)

    if debug:
        log.add(
            sys.stderr,
            format="<blue>{time:YYYY-MM-DD HH:mm:ss}</blue> | <yellow>[{level}]</yellow> | <cyan>{name}.{function}:{line}</cyan> |> {message}",
            level="DEBUG",
            colorize=True,
        )

        log.debug("CLI debugging enabled.")
    else:
        log.add(
            sys.stderr,
            format="<blue>{time:YYYY-MM-DD HH:mm:ss}</blue> <yellow>[{level}]</yellow> : {message}",
            level="INFO",
            colorize=True,
        )

    if log_file:
        log.add(
            log_file,
            format="{time:YYYY-MM-DD HH:mm:ss} | {level} | {name}.{function}:{line} |> {message}",
            level="DEBUG",
            rotation="15MB",
        )

    app(tokens)


if __name__ == "__main__":
    app.meta()
