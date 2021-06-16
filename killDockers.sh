#!/bin/sh

docker stop $(awk '/Up/{printf $1"  \n"}'  <<< $(docker ps -a))
docker rm   $(awk '/Exited/{printf $1"  \n"}'  <<< $(docker ps -a ))
