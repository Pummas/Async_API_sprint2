FROM python:3.8-slim-buster

WORKDIR /tests

COPY ./tests/functional/requirements.txt ./
RUN pip3 install --upgrade pip
RUN pip3 install -r requirements.txt

COPY ./tests .

