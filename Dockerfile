FROM python:3.11-slim

COPY ./app /app

RUN apt-get install -y \
  dos2unix \
  libpq-dev \
  libmariadb-dev-compat \
  libmariadb-dev \
  gcc \
  && apt-get clean

RUN apt-get update && \
    apt-get install -y \
    locales  \
    git  \
    g++  \
    gcc  \
    libpq-dev  \
    && sed -i -e 's/# fr_FR.UTF-8 UTF-8/fr_FR.UTF-8 UTF-8/' /etc/locale.gen  \
    && apt-get clean
RUN dpkg-reconfigure --frontend=noninteractive locales && \
RUN rm -rf /var/lib/apt/lists/*

ENV LANG fr_FR.UTF-8
ENV LC_ALL fr_FR.UTF-8
ENV TZ=Europe/Paris

RUN pip install --upgrade pip
RUN pip install -r /app/requirements.txt
RUN pip install git+https://github.com/influxdata/influxdb-client-python.git@master

RUN mkdir /data
RUN mkdir /log

CMD ["python", "-u", "/app/main.py"]
