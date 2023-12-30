# syntax=docker/dockerfile:1

ARG PYTHON_VERSION
FROM python:${PYTHON_VERSION:?} as base

LABEL PYTHON_VERSION=${PYTHON_VERSION}


RUN --mount=type=cache,target=/root/.cache \
    python -m pip install -U pip

RUN --mount=type=cache,target=/var/cache/apt \
        apt-get update && apt-get install -y \
            curl \
            wrk

ARG GUICORN_VERSION=21.2.0
LABEL GUICORN_VERSION=${GUICORN_VERSION:?}
RUN --mount=type=cache,target=/root/.cache \
    pip install gunicorn==${GUICORN_VERSION}


ARG UVICORN_VERSION=0.18.3
LABEL UVICORN_VERSION=${UVICORN_VERSION:?}
RUN --mount=type=cache,target=/root/.cache \
    pip install uvicorn==${UVICORN_VERSION}


WORKDIR /home/root/app
COPY server.py server.py

COPY ./entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh
CMD ["/entrypoint.sh"]


FROM base
ARG STARLETTE_VERSION
LABEL STARLETTE_VERSION=${STARLETTE_VERSION:?}
RUN echo "installing starlette ${STARLETTE_VERSION}"
RUN --mount=type=cache,target=/root/.cache \
    pip install starlette==${STARLETTE_VERSION}


