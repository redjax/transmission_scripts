ARG UV_BASE=${UV_IMAGE_VER:-0.5.9}
ARG PYTHON_BASE=${PYTHON_IMG_VER:-3.12-slim}

FROM ghcr.io/astral-sh/uv:${UV_BASE} AS uv
FROM python:${PYTHON_BASE} AS base

RUN apt-get update -y \
    && apt-get install -y --no-install-recommends \
    build-essential \
    iputils-ping \
    libmemcached-dev \
    zlib1g-dev \
    curl \
    ca-certificates \
    software-properties-common \
    apt-transport-https \
    sudo \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean

RUN mkdir -p /project /var/log/transmission_scripts

FROM base AS stage

WORKDIR /project

COPY --from=base /project /project

COPY pyproject.toml uv.lock README.md ./

## Copy monorepo domains
COPY applications/ applications/
COPY packages/ packages/
COPY scripts/ scripts/
COPY src/ src/

FROM stage AS build

COPY --from=stage /project /project
COPY --from=uv /uv /usr/bin/uv

WORKDIR /project

## Build project in container
RUN uv sync --all-extras \
    && uv build

FROM build AS celery_beat

COPY --from=build /project /project
COPY --from=base /var/log/transmission_scripts /var/log/transmission_scripts
COPY --from=uv /uv /usr/bin/uv

WORKDIR /project

CMD ["uv", "run", "scripts/transmission/count/count_all_torrents.py"]
