# syntax=docker/dockerfile:1

FROM ubuntu:22.04
LABEL org.opencontainers.image.source=https://github.com/meteoiq/metview

ENV METVIEWBUNDLE=MetviewBundle-2026.1.0-Source
ENV LIBAEC_VERSION=1.0.6
ARG PARALLELISM=1

RUN apt-get update \
	&& DEBIAN_FRONTEND=noninteractive TZ=Etc/UTC apt-get install --yes --no-install-suggests --no-install-recommends \
        bison \
        build-essential \
	    cmake \
        curl \
        file \
        flex \
        gfortran \
        git \
        libbz2-dev \
        libcairo2-dev \
        libeigen3-dev \
        libgdbm-dev \
        liblapack-dev \
        liblz4-dev \
        libncurses-dev \
        libnetcdf-dev \
        libnetcdf-c++4-dev \
        libpango1.0-dev \
        libproj-dev \
        libsnappy-dev \
        libtirpc-dev \
        libtirpc3 \
        make \
        parallel \
        python3-full \
        python3-pip \
        python-is-python3 \
        rpcsvc-proto \
	&& rm -rf /var/lib/apt/lists/*

RUN curl -L -o /libaec-${LIBAEC_VERSION}.tar.gz https://github.com/MathisRosenhauer/libaec/releases/download/v${LIBAEC_VERSION}/libaec-${LIBAEC_VERSION}.tar.gz && \
    tar -xzf /libaec-${LIBAEC_VERSION}.tar.gz && \
    mkdir /build_libaec

WORKDIR /build_libaec
RUN cmake -DCMAKE_INSTALL_PREFIX=/usr/local ../libaec-${LIBAEC_VERSION} && \
  make install
WORKDIR /

RUN mkdir -p /src
RUN mkdir -p /build
WORKDIR /src
RUN curl -L -o ${METVIEWBUNDLE}.tar.gz https://confluence.ecmwf.int/download/attachments/51731119/${METVIEWBUNDLE}.tar.gz && tar -xzf ${METVIEWBUNDLE}.tar.gz && rm -rf ${METVIEWBUNDLE}.tar.gz

WORKDIR /build
RUN export RPC_PATH="$(find / -name libtirpc.so.3 -exec dirname {} \;)" && \
    cmake -DENABLE_UI=OFF -DENABLE_EXPOSE_SUBPACKAGES=ON -DCMAKE_BUILD_TYPE=Release /src/${METVIEWBUNDLE} &&  \
    make -j$PARALLELISM &&  \
    make install && \
    rm -r /build

RUN pip install metview xarray rioxarray rasterio cfgrib ecmwf-opendata psutil

RUN mkdir -p /examples
COPY examples/* /examples/
