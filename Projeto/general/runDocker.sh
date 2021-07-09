#!/bin/sh

docker build --tag projecto_final . && docker run -d --name $1 projecto_final
