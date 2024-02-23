# Use an official Python runtime as a parent image
FROM python:3.10-slim

# Set the working directory in the container
WORKDIR /app

EXPOSE 8080
# Copy the current directory contents into the container at /usr/src/app
COPY . .

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copy the entire current directory into the container at /app
COPY . /app

VOLUME /app/

# Make port 8501 available to the world outside this container
EXPOSE 8501

# Run aiagent.py when the container launches
CMD streamlit run --server.port 8080 --server.enableCORS false app.py

