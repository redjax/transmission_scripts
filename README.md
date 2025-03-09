# Transmission Scripts

Scripts for controlling Transmission remotes.

## Requirements

- [Astral `uv`](https://docs.astral.sh/uv)

## Setup

- Copy [`configs/example.config.json`](./configs/example.config.json) to `default.json`
  - Edit this file with your remote Transmission connection details.
  - You can add additional JSON config files, and if you [use the project CLI](#project-cli), you can pass them with `-c path/to/your/custom-config.json`.
- Run [one of the scripts](#scripts), the [project CLI](#project-cli), or the [Docker container](#docker)
  - The first time you run one of these commands, `uv` will automatically install all of your dependencies.
  - You can also manually install the project using `uv sync --all-extras` (include `--dev` to install dev dependencies)

## Usage

### Scripts

Run one of the scripts in [`scripts/transmission/`](./scripts/transmission/). These are Python scripts mean to be run with `uv`. You can run these scripts by prefixing them with `uv run`. For example, to run the scripts that counts all torrents on the remote:

```shell
uv run ./scripts/transmission/count/count_all_torents.py
```

### Project CLI

The project includes [a CLI app built with [`cyclopts`](https://cyclopts.readthedocs.io/)](./applications/cli/), with an entrypoint in the project root at [`./cli.py`](./cli.py).

Run this script with `--help` to see all options (i.e. `uv run cli.py --help`).

All Transmission operations are in the `transmission` subcommand, which you can call like `uv run cli.py transmission --help`. You can also pass a custom config JSON file with `-c path/to/custom_config.json`. The CLI app will look for a `default.json` file in the [`configs/` path](./configs/).

Some examples:

- Count all paused torrents:
  - `uv run cli.py transmission count --status stopped`
- Count all finished torrents, using a custom config named `remote1.json`:
  - `uv run cli.py transmission count -c remote1.json --status finished`
- List all seeding torrents:
  - `uv run cli.py transmission list --status seeding`
- List all torrents on remote3, debug the connection:
  - `uv run cli.py transmission list -c configs/remote3.json --debug`

### Docker

The [included Dockerfile](./containers/dockerfiles/Dockerfile) builds the project in a Docker container and allows for custom entrypoints. This is just like [running a script](#scripts) or the [project CLI](#project-cli), except the execution happens inside Docker (meaning you don't need to install anything, even `uv`, if you already have Docker installed).

Before running the container, you have to build it. You can use the [included build script](./scripts/docker/build_container.sh) to build the container to an image named `transmission-scripts`. Then, you can either use [one of the pre-made run scripts](./scripts/docker/run_scripts/), or execute a custom command.

For example, to run the [script that removes finished torrents](./scripts/docker/run_scripts/run_rm_finished_torrents.sh), run the command: `./scripts/docker/run_scripts/run_rm_finished_torrents.sh`.

To run a custom Python command, i.e. to call the project CLI in the container with a custom configuration:

```shell
docker run --rm \
    --name transmission-scripts \
    -v "./configs:/project/configs:ro" \
    transmission-scripts_customexec \
    uv run cli.py transmission count -c configs/custom-remote.json --status finished
```
