#!/bin/bash

pushd reverse_proxy
docker stack rm reverse_proxy
docker stack deploy --compose-file docker-compose.yml reverse_proxy
popd
