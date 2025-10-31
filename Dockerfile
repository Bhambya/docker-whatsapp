FROM linuxserver/chromium:latest

# Install git and python dependencies
RUN echo "**** install packages ****" && \
    apt-get update && \
    apt-get install -y --no-install-recommends \
    python3 \
    python3-pip \
    python3.13-venv \
    chromium-driver \
    xclip && \
    echo "**** cleanup ****" && \
    apt-get autoclean && \
    rm -rf \
    /config/.cache \
    /var/lib/apt/lists/* \
    /var/tmp/* \
    /tmp/*

COPY ./server /server

WORKDIR /server
RUN python3 -m venv /server/.venv
RUN /server/.venv/bin/python3 -m pip install -r requirements.txt

COPY root /
