FROM python:3.12.3-slim

RUN apt-get update && \
    apt-get install -y \
    locales  \
    git  \
    g++  \
    gcc  \
    libpq-dev
RUN sed -i -e 's/# fr_FR.UTF-8 UTF-8/fr_FR.UTF-8 UTF-8/' /etc/locale.gen
RUN dpkg-reconfigure --frontend=noninteractive locales
RUN rm -rf /var/lib/apt/lists/*

ENV LANG fr_FR.UTF-8
ENV LC_ALL fr_FR.UTF-8
ENV TZ=Europe/Paris

RUN pip install --upgrade pip pip-tools setuptools

COPY ./src /app

RUN pip install -r /app/requirements.txt

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
