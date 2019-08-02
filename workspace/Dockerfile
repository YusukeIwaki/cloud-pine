FROM debian:buster

ARG USERNAME=cloud-pine

ENV DEBIAN_FRONTEND noninteractive
RUN apt-get update && apt-get -y --no-install-recommends install \
        build-essential \
        ca-certificates \
        curl \
        git \
        locales \
        openssh-client \
        nano \
        nodejs \
        python \
        sudo \
        wget \
        && rm -rf /var/cache/apt/archives/* /var/lib/apt/lists/*

RUN sed -i -e 's/# \(en_US\.UTF-8 .*\)/\1/' /etc/locale.gen
RUN locale-gen
ENV LANG en_US.UTF-8
ENV LANGUAGE en_US:en
ENV LC_ALL en_US.UTF-8

RUN useradd -m -s /bin/bash $USERNAME
RUN echo $USERNAME "ALL=(ALL:ALL) NOPASSWD: ALL" > /etc/sudoers.d/$USERNAME

RUN mkdir -p /c9 /usr/src/app && chown $USERNAME:$USERNAME /c9 /usr/src/app

RUN curl -L https://www.npmjs.com/install.sh | sh
RUN npm install -g c9

ENV ENTRYKIT_VERSION 0.4.0
RUN wget https://github.com/progrium/entrykit/releases/download/v${ENTRYKIT_VERSION}/entrykit_${ENTRYKIT_VERSION}_Linux_x86_64.tgz \
  && tar -xvzf entrykit_${ENTRYKIT_VERSION}_Linux_x86_64.tgz \
  && rm entrykit_${ENTRYKIT_VERSION}_Linux_x86_64.tgz \
  && mv entrykit /bin/entrykit \
  && chmod +x /bin/entrykit \
  && entrykit --symlink

USER $USERNAME
RUN git clone https://github.com/c9/core.git /c9/sdk --depth 1
RUN cd /c9/sdk/ && ./scripts/install-sdk.sh
RUN sed -i -e 's/"dark"/"flat-light"/' /c9/sdk/configs/ide/default.js

USER root
# SOME ADDITIONAL INSTALL HERE...
USER $USERNAME

ENV PORT=8080
EXPOSE 8080

ENV C9_USER=$USERNAME
WORKDIR /usr/src/app
EXPOSE 8888

ENTRYPOINT [ "prehook", "sudo apt-get update", "--" ]

CMD node /c9/sdk/server.js -w /usr/src/app --port 8888 --listen 0.0.0.0 --auth :
