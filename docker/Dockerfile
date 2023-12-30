# syntax=docker/dockerfile:1
ARG BASEIMAGE
FROM ${BASEIMAGE:?}

ARG ASGI_MODULE
ARG ASGI_VERSION
LABEL ${ASGI_MODULE:?}_VERSION=${ASGI_VERSION:?}

COPY ./${ASGI_MODULE:?}_server.py server.py

RUN --mount=type=cache,target=/root/.cache \
    pip install ${ASGI_MODULE:?}==${ASGI_VERSION:?} \
