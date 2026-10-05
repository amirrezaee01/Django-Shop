FROM python:3.12-slim

ENV PYTHONUNBUFFERED=1

WORKDIR /usr/src/app

# Install dependencies
COPY ./requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy project files
COPY ./core .

