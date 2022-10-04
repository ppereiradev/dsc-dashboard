#Download base image ubuntu 20.04
FROM python:3.10.0-bullseye
LABEL maintainer="paulopereira.dev"

ARG DEBIAN_FRONTEND=noninteractive
ARG UID

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

RUN useradd -u $UID -m user

COPY ./dsc_dashboard /home/user/app
COPY ./requirements.txt /home/user/requirements.txt


RUN python -m venv /home/user/venv && \
    mkdir -p /home/user/vol/web/media && \
    mkdir -p /home/user/vol/web/static && \
    apt-get install default-libmysqlclient-dev && \
    chown -R user:user /home/user
    
USER user

ENV PATH="/home/user/venv/bin:$PATH"

# install dependencies and commands
RUN pip install --upgrade pip && \
    pip install -r /home/user/requirements.txt

WORKDIR /home/user/app