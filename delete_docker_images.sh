#!/usr/bin/env bash
IMAGES=$(docker image list --format '{{.Repository}}:{{.Tag}}' --filter 'reference=test-asgi-perf:*')
if [[ -z $IMAGES ]]; then
  echo "no docker image to delete"
else
  docker image rm $IMAGES
fi
