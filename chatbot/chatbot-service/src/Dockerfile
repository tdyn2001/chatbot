# syntax=docker/dockerfile:1

FROM python:3.8-slim-buster

WORKDIR /python-docker

COPY requirements.txt requirements.txt
COPY data data
COPY model model
RUN pip3 install -r requirements.txt

COPY . .

CMD [ "python3", "chatbot.py"]