# Use an official Python runtime as a parent image
FROM python:3.10.8-slim as builder

# Create a non-root user and set the working directory
RUN useradd -m -s /bin/bash user1
WORKDIR /app

# Set the environment variables for the API keys as build arguments
ARG OPENAI_API_KEY
ARG PINECONE_API_KEY
ENV OPENAI_API_KEY=$OPENAI_API_KEY
ENV PINECONE_API_KEY=$PINECONE_API_KEY

# Copy the requirements.txt file and install the Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the app code into a volume
COPY . /app

# Expose the port that your Streamlit app is listening on
EXPOSE 8081

# Command to run the Streamlit application
CMD ["streamlit", "run", "streamlitapp.py", "--server.port", "8081"]

# Use a different stage for the final image
FROM python:3.10.8-slim

# Create a non-root user and set the working directory
RUN useradd -m -s /bin/bash user1
WORKDIR /app

# Copy the app code into a volume from the builder stage
COPY --from=builder /app /app

RUN pip install --no-cache-dir -r requirements.txt
# Expose the port that your Streamlit app is listening on
EXPOSE 8081

# Command to run the Streamlit application
CMD ["streamlit", "run", "streamlitapp.py", "--server.port", "8081"]