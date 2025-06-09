# docker-whatsapp
Send messages via Whatsapp using Chromium running inside a docker container.

## Installation

The image is based on [linuxserver/chromium](https://hub.docker.com/r/linuxserver/chromium).

### docker-compose

```
---
services:
  whatsapp:
    security_opt:
      - seccomp:unconfined
    build:
      context: /path/to/docker-whatsapp
      dockerfile: ./Dockerfile
    environment:
      - PUID=1000
      - PGID=1000
      - TZ=Etc/UTC
    ports:
      - 127.0.0.1:3000:3000 # KasmVNC port
      - 127.0.0.1:5000:5000 # server port
    volumes:
      - whatsapp_volume:/config
    shm_size: "1gb"
    restart: unless-stopped
```

### Parameters

See [linuxserver/chromium](https://hub.docker.com/r/linuxserver/chromium) for all the supported environment variables.

## Usage

### Logging in to Whatsapp using the QR code

Go to http://localhost:3000 to see what's happening inside the docker container. This is also needed to be able to scan the QR code.

Hit the login API.

```
curl -X POST http://localhost:5000/api/login
```
Scan the QR code. The API will return `{"status":"success"}` after successful login.

### Dry run sending a message

```
curl -X POST -H "Content-Type: application/json" -d '{"phone_number": "<phone number>"}' http://localhost:5000/api/dry
_run_message
```

This will check that the text box to send the message is located and is clickable. Some pop ups might appear which should be cancelled by you so that they never appear again.

This API can also be used as a healthcheck.

### Send a message

```
curl -X POST -H "Content-Type: application/json" -d '{"phone_number": "<phone number>", "message": "Hi"}' http://localhost:5000/api
/message
```

The this will send a message to the specified phone number.