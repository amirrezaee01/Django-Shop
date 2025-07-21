FROM python:3.10-slim-buster

LABEL maintainer="amirrezayi0101@gmail.com"

ENV PYTHONUNBUFFERED=1

WORKDIR /usr/src/app

# Install dependencies
COPY ./requirements.txt .
RUN pip install --upgrade pip && pip install -r requirements.txt

# Copy project files
COPY ./core .

