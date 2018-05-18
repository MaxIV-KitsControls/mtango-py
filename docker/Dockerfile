############################################################
# Dockerfile to build a deployment container for mtango-py
# Based on Ubuntu and miniconda
############################################################

# To build an image, e.g.:
# $ docker build . -t docker.maxiv.lu.se/mtango-py
#
# To run it, e.g.:
# $ docker run -d -p 8000:8000 -e TANGO_HOST=w-v-kitslab-csdb-0:10000 --name=mtango-py docker.maxiv.lu.se/mtango-py

FROM continuumio/miniconda3
COPY mtango-py.conda /tmp/mtango-py.conda

RUN apt-get update && \
    apt-get -y install build-essential && \
    conda env create --name mtango-py python=3.5 --file=/tmp/mtango-py.conda && \
    git clone https://github.com/MaxIV-KitsControls/mtango-py.git

WORKDIR mtango-py
RUN git checkout -b develop

CMD  /bin/bash -c "source activate mtango-py &&gunicorn main:app --bind 0.0.0.0:8000 --worker-class sanic.worker.GunicornWorker"