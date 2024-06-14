# syntax = docker/dockerfile:1.0-experimental
FROM python:3.9-slim as ergo_base
ARG comp
ARG qed_dir="."
ARG scripts_dir="."
ENV MANIFEST="config.yaml"
ENV NAMESPACE=nautilus-dynamic-ns.yaml
ENV BASE=/component
ENV ERGO_PROTOCOL="amqp"
ENV ERGO_EXCHANGE="primary"
WORKDIR ${BASE}

# for SSH related things
# see: https://docs.docker.com/develop/develop-images/build_enhancements/
# also make sure to update Docker Engine to have buildkit enabled
RUN apt-get update
RUN apt-get -y --no-install-recommends install openssh-client git curl
RUN  mkdir -p -m 0600 ~/.ssh && ssh-keyscan github.com >> ~/.ssh/known_hosts
RUN cat ~/.ssh/known_hosts

RUN mkdir ${BASE}/config
RUN mkdir ${BASE}/namespaces

# hardcoded for root user
ENV PATH="/root/.local/bin:${PATH}:/root/.poetry/bin" 

# Pin ergo version so builds from versioned Dockerfile are consistent
RUN pip3 install ergo=="0.8.9a0"

# gather scripts for python dependency tools
# These scripts presume ergo as a downstream dependency
COPY ${scripts_dir}/start.sh /start.sh
COPY ${scripts_dir}/build.sh /build.sh