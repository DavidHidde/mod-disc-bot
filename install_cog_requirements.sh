#!/bin/bash

LIST=$(jq '.[]' cogs.json)
while IFS= read -r ROOT_DIR; do
    COG_DIRS=$(echo "cogs/${ROOT_DIR:1:-1}/" | xargs ls)
    while IFS= read -r COG_DIR; do
        REQUIREMENTS_FILE=$(echo "cogs/${ROOT_DIR:1:-1}/$COG_DIR/requirements.txt")
        if [ -f "$REQUIREMENTS_FILE" ]; then
            pip install -r $REQUIREMENTS_FILE
        fi
    done <<< "$COG_DIRS"
done <<< "$LIST"
