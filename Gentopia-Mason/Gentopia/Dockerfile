FROM python:3.10-alpine3.17
RUN apk update
RUN apk add python3-dev py3-pip g++ gcc libgfortran musl-dev openblas-dev

COPY ./ /opt/Gentopia

RUN cd /opt/Gentopia && \
    pip3 install -e .

WORKDIR /opt/Gentopia
