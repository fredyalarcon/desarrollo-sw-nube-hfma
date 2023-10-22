# syntax=docker/dockerfile:1

FROM python:3.8-slim-buster

WORKDIR /usr/src/worker

COPY . .

RUN pip3 install --upgrade pip

RUN pip3 install -r requirements.txt

RUN apt-get -y update

RUN apt-get -y upgrade

RUN apt-get install -y ffmpeg

CMD [ "python3", "-m" , "flask", "run", "--host=0.0.0.0"]