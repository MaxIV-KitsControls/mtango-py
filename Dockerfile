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

RUN apt-get update
RUN apt-get -y install build-essential
ADD environment.yml /tmp/environment.yml
RUN conda env create --name mtango-py python=3.5 --file=/tmp/environment.yml
RUN git clone https://github.com/MaxIV-KitsControls/mtango-py.git

WORKDIR mtango-py
RUN git checkout -b develop

# run the web service
EXPOSE 8000
CMD  /bin/bash -c "source activate mtango-py && python main.py"
