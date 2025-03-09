#!/bin/bash

IMAGE_NAME="transmission-scripts"
CONTAINER_NAME="transmission-scripts_count-torrents"

echo "Running Docker container '$IMAGE_NAME' with name '$CONTAINER_NAME'"

docker run --rm \
    --name $CONTAINER_NAME \
    -v "./configs:/project/configs:ro" \
    $IMAGE_NAME \
    uv run scripts/transmission/count/count_all_torrents.py
    

if [ $? -eq 0 ]; then
    echo "Executed successfully"
    exit 0
else
    echo "Failed execution"
    exit 1
fi