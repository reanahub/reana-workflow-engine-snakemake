# This file is part of REANA.
# Copyright (C) 2021, 2022, 2023, 2024 CERN.
#
# REANA is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

# Use Ubuntu LTS base image
FROM docker.io/library/ubuntu:24.04

# Recognise target architecture
ARG TARGETARCH

# Use default answers in installation commands
ENV DEBIAN_FRONTEND=noninteractive

# Allow pip to install packages in the system site-packages dir
ENV PIP_BREAK_SYSTEM_PACKAGES=true

# Prepare list of Python dependencies
COPY requirements.txt /code/

# Install all system and Python dependencies in one go
# hadolint ignore=DL3008,DL3009,DL3013,DL4006
RUN apt-get update -y && \
    apt-get install -y --no-install-recommends \
        cmake \
        curl \
        g++ \
        gcc \
        git \
        gnupg2 \
        graphviz \
        graphviz-dev \
        imagemagick \
        krb5-config \
        krb5-user \
        libauthen-krb5-simple-perl \
        libkrb5-dev \
        libssl-dev \
        make \
        pkg-config \
        python3.12-dev \
        python3-pip \
        python3.12 \
        uuid-dev \
        vim-tiny && \
    # Install xrootd
    if echo "$TARGETARCH" | grep -q "amd64"; then \
      (if curl -o /dev/null -Isw '%{http_code}' https://storage-ci.web.cern.ch/storage-ci/debian/xrootd/dists/focal/Release | grep -q 200; then \
        echo "deb [arch=amd64] http://storage-ci.web.cern.ch/storage-ci/debian/xrootd/ focal release" | tee -a /etc/apt/sources.list.d/xrootd.list; \
      elif curl -o /dev/null -Isw '%{http_code}' https://storage-ci.web.cern.ch/storage-ci/old_debian/xrootd/dists/focal/Release | grep -q 200; then \
        echo "deb [arch=amd64] http://storage-ci.web.cern.ch/storage-ci/old_debian/xrootd/ focal release" | tee -a /etc/apt/sources.list.d/xrootd.list; \
      else \
        echo "[ERROR] Cannot find XRootD package repository location. Exiting."; exit 1; \
      fi && \
      curl -sL http://storage-ci.web.cern.ch/storage-ci/storageci.key | apt-key add - && \
      apt-get update -y && \
      apt-get install -y --no-install-recommends \
          libxrootd-client-dev \
          xrootd-client) \
    fi && \
    pip install --no-cache-dir --upgrade 'setuptools<81' && \
    pip install --no-cache-dir -r /code/requirements.txt && \
    apt-get remove -y \
        cmake \
        g++ \
        gcc \
        git \
        graphviz-dev \
        libssl-dev \
        make \
        pkg-config \
        python3.12-dev \
        uuid-dev && \
    apt-get autoremove -y && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Copy cluster component source code
WORKDIR /code
COPY . /code

# Add magick wrapper command to simulate ImageMagick v7 that is necessary by Snakemake
# to produce thumbnails in generated reports. The wrapper simply passes conversion
# requests to ImageMagick v6 available on Ubuntu 24.04.
COPY scripts/magick-wrapper.sh /usr/local/bin/magick
RUN chmod +x /usr/local/bin/magick

# Are we debugging?
ARG DEBUG=0
# hadolint ignore=DL3013
RUN if [ "${DEBUG}" -gt 0 ]; then pip install --no-cache-dir -e ".[debug]"; else pip install --no-cache-dir .; fi;

# Are we building with locally-checked-out shared modules?
# hadolint ignore=DL3008,DL3013
RUN apt-get update -y && \
    apt-get install -y --no-install-recommends \
        cmake \
        g++ \
        gcc \
        git \
        libssl-dev \
        make \
        python3.12-dev \
        uuid-dev && \
    if test -e modules/reana-commons; then \
      if [ "${DEBUG}" -gt 0 ]; then \
        pip install --no-cache-dir -e "modules/reana-commons[snakemake,snakemake-xrootd]" --upgrade; \
      else \
        pip install --no-cache-dir "modules/reana-commons[snakemake,snakemake-xrootd]" --upgrade; \
      fi \
    fi && \
    apt-get remove -y \
        cmake \
        g++ \
        gcc \
        git \
        libssl-dev \
        make \
        python3.12-dev \
        uuid-dev && \
    apt-get autoremove -y && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Check for any broken Python dependencies
RUN pip check

# Set useful environment variables
ENV TERM=xterm \
    PYTHONPATH=/workdir

# Create and set cache directory to be used by Snakemake
RUN mkdir -p /.cache/snakemake && chmod ug+rwx /.cache/snakemake
ENV XDG_CACHE_HOME=/.cache

# Set image labels
LABEL org.opencontainers.image.authors="team@reanahub.io"
LABEL org.opencontainers.image.created="2026-01-06"
LABEL org.opencontainers.image.description="REANA reproducible analysis platform - Snakemake workflow engine component"
LABEL org.opencontainers.image.documentation="https://reana-workflow-engine-snakemake.readthedocs.io/"
LABEL org.opencontainers.image.licenses="MIT"
LABEL org.opencontainers.image.source="https://github.com/reanahub/reana-workflow-engine-snakemake"
LABEL org.opencontainers.image.title="reana-workflow-engine-snakemake"
LABEL org.opencontainers.image.url="https://github.com/reanahub/reana-workflow-engine-snakemake"
LABEL org.opencontainers.image.vendor="reanahub"
# x-release-please-start-version
LABEL org.opencontainers.image.version="0.9.5"
# x-release-please-end
