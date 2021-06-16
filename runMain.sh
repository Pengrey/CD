#!/bin/bash

PORT=${1:-8000}

if [[ -v $2 ]];then
  echo "Did Not Enter Here"
  PASSWORDSIZE=$2
  python3 server/main.py -s $PASSWORDSIZE -p $PORT

else
  python3 main.py -p $PORT
fi
