FROM python:3.11-slim

COPY ./app /app

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

RUN pip install --upgrade pip pip-tools
RUN pip-compile -o /app/requirements.txt /app/pyproject.toml
RUN pip install -r /app/requirements.txt
RUN pip install git+https://github.com/influxdata/influxdb-client-python.git@master

RUN mkdir /data
RUN mkdir /log

#RUN sh -c 'echo "deb http://apt.postgresql.org/pub/repos/apt $(lsb_release -cs)-pgdg main" > /etc/apt/sources.list.d/pgdg.list'
#RUN apt-get install wget
#RUN /bin/wget --quiet -O - https://www.postgresql.org/media/keys/ACCC4CF8.asc | apt-key add -
#RUN apt-get update
#RUN apt-get -y install postgresql
RUN apt-get clean

CMD ["python", "-u", "/app/main.py"]
