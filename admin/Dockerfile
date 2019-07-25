FROM docker:18.09

RUN apk update && \
    apk upgrade && \
    apk add --no-cache python3 python3-dev build-base

RUN pip3 install --no-cache-dir --upgrade pip && \
    pip3 install --no-cache-dir docker responder

# docker build . -t yusukeiwaki/cloud-pine-admin:latest
# docker run --rm -it -v /var/run/docker.sock:/var/run/docker.sock yusukeiwaki/cloud-pine-admin
