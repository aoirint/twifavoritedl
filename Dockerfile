FROM python:3.11

ENV PYTHONUNBUFFERED=1

RUN apt-get update && \
    apt-get install -y \
        gosu && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

RUN useradd -o -u 1000 -U -m user

ADD ./requirements.txt /tmp/requirements.txt
RUN gosu user pip3 install --no-cache-dir -r /tmp/requirements.txt

ADD ./twifavoritedl /opt/twifavoritedl

WORKDIR /opt/twifavoritedl
ENTRYPOINT [ "gosu", "user", "python3", "main.py" ]
