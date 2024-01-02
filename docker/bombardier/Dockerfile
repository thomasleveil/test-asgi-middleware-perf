FROM alpine:3
ARG BOMBARDIER_VERSION=v1.2.6
LABEL BOMBARDIER_VERSION=${BOMBARDIER_VERSION:?}
RUN apk add curl && \
    curl -sSL https://github.com/codesenberg/bombardier/releases/download/${BOMBARDIER_VERSION:?}/bombardier-linux-amd64 -o /bombardier && \
    chmod +x /bombardier
