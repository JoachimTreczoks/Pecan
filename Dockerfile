FROM ubuntu:24.04

# Setup basic environment
RUN apt-get update
RUN apt-get install -y software-properties-common

# Install git
RUN apt-get install -y git
RUN git --version

# Install python
RUN apt-get update
RUN apt-get install -y python3 python3-dev python3-pip graphviz
# Since this is a docker environment, there is no real danger of actually breaking the system install by using pip for installing packages
RUN pip3 install --break-system-packages pytest
RUN rm -rf /var/lib/apt/lists/*

ENV PYTHONIOENCODING utf-8

# Install misc
RUN apt-get update
RUN apt-get install -y sudo vim wget curl

# Install spot. Run this here so that if we make changes to the stuff below, we don't have to rebuild spot
RUN curl -sSL https://raw.githubusercontent.com/JoachimTreczoks/Pecan/master/scripts/install-spot.sh | bash

WORKDIR /home/pecan

RUN git clone --recursive "https://github.com/JoachimTreczoks/Pecan/" "JoachimTreczoks/Pecan"
RUN git clone --recursive "https://github.com/ReedOei/SturmianWords" "JoachimTreczoks/Pecan/SturmianWords"

WORKDIR /home/pecan/JoachimTreczoks/Pecan

RUN pip3 install --break-system-packages -r requirements.txt
# Install my custom version of PySimpleAutomata
RUN ( cd PySimpleAutomata; pip3 install --break-system-packages . )
RUN pytest --verbose test

