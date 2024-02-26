# AI Agent App - Docker Setup Guide

This repository contains the Docker setup for the AI Agent App. To run the app, follow the steps below:

## Prerequisites

- Docker installed on your local machine
- .env file with the required environment variables

## Creating a .env file

Create a .env file in the same directory as the Dockerfile and docker-compose.yml file. Add the following environment variables to the .env file:

```
OPENAI_API_KEY=<your_openai_api_key>
PINECONE_API_KEY=<your_pinecone_api_key>
```

Replace `<your_openai_api_key>` and `<your_pinecone_api_key>` with your actual API keys.

## Building the Docker Image

1. Make sure you have the `build.sh` script in the same directory as the Dockerfile and docker-compose.yml file.
2. Make the script executable:

```bash
chmod +x build.sh
```

3. Run the `build.sh` script:

```bash
./build.sh
```

This will build the Docker image using the Dockerfile and the environment variables from the .env file.

## Running the Docker Container

1. Run the following command to start the Docker container:

```bash
docker-compose up -d
```

2. Access the Streamlit app by navigating to `http://localhost:8081` in your web browser.

## Stopping the Docker Container

To stop the Docker container, run the following command:

```bash
docker-compose down
```

That's it! You have successfully set up and run the AI Agent App using Docker. Make sure to protect the .env file and never commit it to version control systems.