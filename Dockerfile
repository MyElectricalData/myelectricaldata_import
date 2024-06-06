FROM python:3.12.3-slim

ARG TARGETPLATFORM
ENV TARGETPLATFORM=$TARGETPLATFORM

ENV LANG fr_FR.UTF-8
ENV LC_ALL fr_FR.UTF-8
ENV TZ=Europe/Paris

RUN apt-get update && \
    apt-get install -y \
    locales  \
    git  \
    g++  \
    gcc  \
    libpq-dev \
    curl
    RUN sed -i -e 's/# fr_FR.UTF-8 UTF-8/fr_FR.UTF-8 UTF-8/' /etc/locale.gen
RUN dpkg-reconfigure --frontend=noninteractive locales
RUN rm -rf /var/lib/apt/lists/*

RUN pip install --upgrade pip pip-tools setuptools

RUN apt update
RUN apt install -y curl git build-essential
RUN apt install -y libc6-armhf-cross libc6-dev-armhf-cross gcc-arm-linux-gnueabihf
RUN apt install -y libdbus-1-dev libdbus-1-dev:armhf


# INSTALL RUST FOR ARMv7 and orjson lib
RUN if [ "$TARGETPLATFORM" = "linux/arm/v7" ]; then \
        curl -k -o rust-install.tar.gz https://static.rust-lang.org/dist/rust-1.78.0-armv7-unknown-linux-gnueabihf.tar.xz && \
        tar -xvf rust-install.tar.gz && \
        chmod +x rust-1.78.0-armv7-unknown-linux-gnueabihf/install.sh && \
        ./rust-1.78.0-armv7-unknown-linux-gnueabihf/install.sh; \
    fi

COPY ./src /app

RUN pip install -r /app/requirements.txt

# REMOVE RUST
RUN /usr/local/lib/rustlib/uninstall.sh

RUN mkdir /data
RUN mkdir /log

RUN apt-get clean

ARG BUILD_DATE
ARG BUILD_REF
ARG BUILD_VERSION
LABEL \
    maintainer="m4dm4rtig4n (https://github.com/alexbelgium)" \
    org.opencontainers.image.title="MyElectricalData official client" \
    org.opencontainers.image.description="Client to import data from MyElectricalData gateway." \
    org.opencontainers.image.authors="m4dm4rtig4n (https://github.com/m4dm4rtig4n)" \
    org.opencontainers.image.licenses="Apache License 2.0" \
    org.opencontainers.image.url="https://github.com/m4dm4rtig4n" \
    org.opencontainers.image.source="https://github.com/MyElectricalData/myelectricaldata_import" \
    org.opencontainers.image.documentation="https://github.com/MyElectricalData/myelectricaldata_import/blob/main/README.md" \
    org.opencontainers.image.created=${BUILD_DATE} \
    org.opencontainers.image.revision=${BUILD_REF} \
    org.opencontainers.image.version=${BUILD_VERSION}

CMD ["python", "-u", "/app/main.py"]
