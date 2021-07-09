FROM python:3.8-slim-buster

WORKDIR /

COPY cracker.py cracker.py
COPY utils.py utils.py
COPY slave.py slave.py


CMD ["python3", "-u", "slave.py"]
