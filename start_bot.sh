#!/bin/bash

# Basic idea of this script: run the framework and launch all enabled cogs that
#  require containers. If --build flag is added will also build the framework.

if [[ $* == *--build* ]]; then
    docker compose build
fi

docker compose up -d

ENABLED_COGS=$(jq '.cogs[] | select(.enabled == true) | {name}' configuration.json | cat)
LIST=$(jq '.[]' app/cogs.json)

while IFS= read -r ROOT_DIR; do
    COG_DIRS=$(echo "app/cogs/${ROOT_DIR:1:-1}/" | xargs ls)

    while IFS= read -r COG_DIR; do
        DOCKER_DIR=$(echo "app/cogs/${ROOT_DIR:1:-1}/$COG_DIR/docker")
        SUBSTR="\"name\": \"$COG_DIR\""

        if [[ "$ENABLED_COGS" == *"$SUBSTR"* ]] && [ -d "$DOCKER_DIR" ]; then
            DOCKER_FILE=$(find $DOCKER_DIR -iname "*.override.yml" -o -iname "*.override.yaml")
            docker compose -f $DOCKER_FILE up -d
        fi
    done <<< "$COG_DIRS"
done <<< "$LIST"
