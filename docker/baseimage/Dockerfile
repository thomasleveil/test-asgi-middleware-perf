# syntax=docker/dockerfile:1

ARG PYTHON_VERSION
FROM python:${PYTHON_VERSION:?} as base

LABEL PYTHON_VERSION=${PYTHON_VERSION}

RUN --mount=type=cache,target=/root/.cache \
    python -m pip install -U pip

ARG GUICORN_VERSION=21.2.0
LABEL GUICORN_VERSION=${GUICORN_VERSION:?}
RUN --mount=type=cache,target=/root/.cache \
    pip install gunicorn==${GUICORN_VERSION}


ARG UVICORN_VERSION=0.18.3
LABEL UVICORN_VERSION=${UVICORN_VERSION:?}
RUN --mount=type=cache,target=/root/.cache \
    pip install uvicorn==${UVICORN_VERSION}


WORKDIR /home/root/app

COPY ./entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh
CMD ["/entrypoint.sh"]

ENV NUM_MIDDLEWARES=0

