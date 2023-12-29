# syntax=docker/dockerfile:1

ARG PYTHON_VERSION
FROM python:${PYTHON_VERSION:?} as base

LABEL PYTHON_VERSION=${PYTHON_VERSION}


RUN --mount=type=cache,target=/root/.cache \
    python -m pip install -U pip

RUN --mount=type=cache,target=/var/cache/apt \
        apt-get update && apt-get install -y \
            curl \
            siege


ARG UVICORN_VERSION=0.18.3
LABEL UVICORN_VERSION=${UVICORN_VERSION:?}
RUN --mount=type=cache,target=/root/.cache \
    pip install uvicorn==${UVICORN_VERSION}


WORKDIR /home/root/app
COPY server.py server.py

COPY ./entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh
ENTRYPOINT ["/entrypoint.sh"]


FROM base
ARG SANIC_VERSION
LABEL SANIC_VERSION=${SANIC_VERSION:?}
RUN echo "installing sanic ${SANIC_VERSION}"
RUN --mount=type=cache,target=/root/.cache \
    pip install sanic==${SANIC_VERSION}


