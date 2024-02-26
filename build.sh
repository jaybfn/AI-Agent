#!/bin/bash

# Read the environment variables from the .env file
eval $(cat .env | grep -v '#' | xargs)

# Build the Docker image using docker-compose
docker-compose build --build-arg OPENAI_API_KEY="$OPENAI_API_KEY" --build-arg PINECONE_API_KEY="$PINECONE_API_KEY"