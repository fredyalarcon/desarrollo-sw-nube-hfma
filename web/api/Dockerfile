# syntax=docker/dockerfile:1

FROM python:3.8-slim-buster

WORKDIR /usr/src/web/api

COPY . .

RUN pip3 install --upgrade pip

RUN pip3 install -r requirements.txt

CMD [ "python3", "-m" , "flask", "run", "-p", "8080", "--host=0.0.0.0"]