FROM python:3.12.2-slim

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

CMD ["python", "-u", "/app/main.py"]
