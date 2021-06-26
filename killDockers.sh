#!/bin/sh


DOCKER_UP=$(docker ps -q)
if [[ ${#DOCKER_UP[@]} -gt 1 ]]; then
  docker kill $(docker ps -q)
fi

DOCKER_TORM=$(docker ps -a -q)
if [[ ${#DOCKER_TORM} -gt 1 ]]; then
  docker rm $(docker ps -a -q)
fi
