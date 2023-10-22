# syntax=docker/dockerfile:1

FROM python:3.8-slim-buster

WORKDIR /usr/src/web

COPY . .

RUN pip3 install --upgrade pip

RUN pip3 install -r requirements.txt

CMD [ "gunicorn", "-w", "-b", "4" "0.0.0.0:5000", "'api:create_app()'"]