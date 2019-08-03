#!/bin/bash

pushd admin
docker stack rm admin
docker stack deploy --compose-file docker-compose.yml admin
popd

./restart_reverse_proxy.sh
