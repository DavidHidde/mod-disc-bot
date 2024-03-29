#!/bin/bash

# Basic idea of this script: stop the framework and all enabled cogs that require containers

ENABLED_COGS=$(jq '.cogs[] | select(.enabled == true) | {name}' configuration.json | cat)
LIST=$(jq '.[]' cogs.json)

while IFS= read -r ROOT_DIR; do
    COG_DIRS=$(echo "cogs/${ROOT_DIR:1:-1}/" | xargs ls)

    while IFS= read -r COG_DIR; do
        DOCKER_DIR=$(echo "cogs/${ROOT_DIR:1:-1}/$COG_DIR/docker")
        SUBSTR="\"name\": \"$COG_DIR\""

        if [[ "$ENABLED_COGS" == *"$SUBSTR"* ]] && [ -d "$DOCKER_DIR" ]; then
            DOCKER_FILE=$(find $DOCKER_DIR -iname "docker-compose.yml" -o -iname "docker-compose.yaml")
            docker compose -f $DOCKER_FILE down
        fi
    done <<< "$COG_DIRS"
done <<< "$LIST"

docker compose down
