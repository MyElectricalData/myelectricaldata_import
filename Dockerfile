FROM python:3.9.7-slim

COPY ./app /app

RUN apt-get update && \
    apt-get install -y locales && \
    sed -i -e 's/# fr_FR.UTF-8 UTF-8/fr_FR.UTF-8 UTF-8/' /etc/locale.gen && \
    dpkg-reconfigure --frontend=noninteractive locales && \
    rm -rf /var/lib/apt/lists/*

ENV LANG fr_FR.UTF-8
ENV LC_ALL fr_FR.UTF-8

RUN mkdir -p /data
RUN pip install -r /app/requirement.txt

CMD ["python", "-u", "/app/main.py"]