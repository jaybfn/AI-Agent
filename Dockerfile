# Use an official Python runtime as a parent image
FROM python:3.10-slim

# Allow statements and log messages to immediately appear in the logs
ENV PYTHONUNBUFFERED True

# Copy the requirements.txt file and install the Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the entire current directory into the container at /app
COPY . /app

VOLUME /app/

# Expose the port that your Streamlit app is listening on
EXPOSE 8501

# Command to run the Streamlit application
CMD streamlit run --server.port 8501 --server.enableCORS false app.py


