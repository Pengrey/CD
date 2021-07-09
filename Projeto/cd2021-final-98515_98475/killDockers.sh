#!/bin/bash
i=${1:-5}

if [[ -n $(docker ps -a -q) ]];then
 docker stop $(docker ps -a -q)
 docker rm $(docker ps -a -q)
fi

#docker run --name server diogogomes/cd2021:latest &

for (( ; i>0; i-- ));do
 DOCKERNAME="Worker"$if
 setsid --fork gnome-terminal -- bash -c "docker build --tag projecto_final . && docker run --name $DOCKERNAME projecto_final; read" 2>/dev/null
done
