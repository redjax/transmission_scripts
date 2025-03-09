#!/bin/bash

IMAGE_NAME="transmission-scripts"
DOCKERFILE_PATH="./containers/dockerfiles/Dockerfile"

echo "Building Dockerfile at path '$DOCKERFILE_PATH' with name '$IMAGE_NAME'"

docker build -t $IMAGE_NAME -f $DOCKERFILE_PATH .
if [ $? -eq 0 ]; then
    echo "Successfully built Dockerfile at path '$DOCKERFILE_PATH' with name '$IMAGE_NAME'"

    # echo "Run the container with a custom script:"
    # echo "docker run --rm "

    exit 0
else
    echo "Failed to build Dockerfile at path '$DOCKERFILE_PATH' with name '$IMAGE_NAME'"

    exit 1
fi
