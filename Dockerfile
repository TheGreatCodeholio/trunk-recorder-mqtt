FROM ubuntu:24.04 AS builder

# Install docker for passing the socket to allow for intercontainer exec
RUN apt-get update && \
  apt-get -y upgrade &&\
  export DEBIAN_FRONTEND=noninteractive && \
  apt-get install --no-install-recommends -y \
    build-essential \
    ca-certificates \
    cmake \
    curl \
    git \
    gnuradio-dev \
    gr-osmosdr \
    libosmosdr-dev \
    libairspy-dev \
    libairspyhf-dev \
    libbladerf-dev \
    libboost-all-dev \
    libcurl4-openssl-dev \
    libfreesrp-dev \
    libgmp-dev \
    libhackrf-dev \
    libmirisdr-dev \
    liborc-0.4-dev \
    libpaho-mqtt-dev  \
    libpaho-mqttpp-dev \
    libpthread-stubs0-dev \
    librtlsdr-dev \
    libsndfile1-dev \
    libsoapysdr-dev \
    libssl-dev \
    libuhd-dev \
    libusb-dev \
    libusb-1.0-0-dev \
    libxtrx-dev \
    pkg-config \
    wget \
    python3-six \
    openssh-client \
    ffmpeg

WORKDIR /src

RUN git clone https://github.com/robotastic/trunk-recorder.git  \
    && cd trunk-recorder  \
    && mkdir build

RUN cd trunk-recorder/user_plugins && git clone https://github.com/taclane/trunk-recorder-mqtt-status.git

WORKDIR /src/trunk-recorder/build

RUN cmake .. && make -j$(nproc) && make DESTDIR=/newroot install

#Stage 2 build
FROM ubuntu:24.04
RUN apt-get update && apt-get -y upgrade && apt-get install --no-install-recommends -y ca-certificates gr-funcube gr-iqbal curl wget libboost-log1.83.0 \
    libboost-chrono1.83.0t64 libgnuradio-digital3.10.9t64 libgnuradio-analog3.10.9t64 libgnuradio-filter3.10.9t64 libgnuradio-network3.10.9t64  \
    libpaho-mqtt-dev libpaho-mqttpp-dev \
    libgnuradio-uhd3.10.9t64 libgnuradio-osmosdr0.2.0t64 libsoapysdr0.8 soapysdr0.8-module-all libairspyhf1 libfreesrp0 librtlsdr2 libxtrx0 sox fdkaac docker.io && \
    rm -rf /var/lib/apt/lists/* && \
    rm -rf /usr/share/{doc,man,info} && rm -rf /usr/local/share/{doc,man,info}

COPY --from=builder /newroot /

# Fix the error message level for SmartNet
RUN mkdir -p /etc/gnuradio/conf.d/ && echo 'log_level = info' >> /etc/gnuradio/conf.d/gnuradio-runtime.conf && ldconfig
WORKDIR /app

# GNURadio requires a place to store some files, can only be set via $HOME env var.
ENV HOME=/tmp

#USER nobody
CMD ["trunk-recorder", "--config=/app/config.json"]
