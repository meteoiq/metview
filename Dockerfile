FROM python:3.14-trixie

RUN set -ex \
	&& apt-get update \
	&& apt-get install --yes --no-install-suggests --no-install-recommends \
	cmake \
        bison \
        flex \
        g++ \
        gcc \
        gfortran \
        parallel \
        libcairo2-dev \
        libpango1.0-dev \
        libproj-dev \
        libnetcdf-c++4-dev \
	&& rm -rf /var/lib/apt/lists/*

ENV METVIEWBUNDLE=MetviewBundle-2026.1.0-Source

RUN mkdir -p /src 
RUN mkdir -p /build
WORKDIR /src
RUN wget -O ${METVIEWBUNDLE}.tar.gz https://confluence.ecmwf.int/download/attachments/51731119/${METVIEWBUNDLE}.tar.gz && tar -xzvf ${METVIEWBUNDLE}.tar.gz && rm -rf ${METVIEWBUNDLE}.tar.gz

WORKDIR /build
RUN cmake -DENABLE_UI=OFF -DCMAKE_BUILD_TYPE=Release /src/${METVIEWBUNDLE} && make && make install

RUN pip install metview xarray rioxarray rasterio cfgrib ecmwf-opendata psutil

RUN mkdir -p /examples
COPY examples/* /examples/
