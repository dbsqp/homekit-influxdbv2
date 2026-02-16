ARG ARCH=

# Pull base image
FROM ubuntu:latest

# Labels
LABEL MAINTAINER="https://github.com/dbsqp/"

# Setup external package-sources
RUN apt-get update && apt-get install -y \
    python3 \
    python3-dev \
    python3-setuptools \
    python3-pip \
    python3-virtualenv \
    iputils-ping \
    python3-venv \
    --no-install-recommends && \
    rm -rf /var/lib/apt/lists/* 

# set venv
RUN python3 -m venv docker_env
RUN . docker_env/bin/activate
RUN python3 -m venv --system-site-packages /usr/local

# RUN pip install setuptools
RUN pip3 install pytz influxdb-client requests getmac

# Environment vars
ENV PYTHONIOENCODING=utf-8

# Copy files
ADD homekit2influxdb.py /
ADD get.sh /

# Run
CMD ["/bin/bash","/get.sh"]
