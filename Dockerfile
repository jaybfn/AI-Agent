# Use an official Python runtime as a parent image
FROM python:3.10-slim

# Allow statements and log messages to immediately appear in the logs
ENV PYTHONUNBUFFERED True

# Expose port 8080 for the application
EXPOSE 8080

# Set the working directory in the container
ENV APP_HOME /app
WORKDIR $APP_HOME

# Copy the current directory contents into the container at /app
COPY . ./

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Command to run the Streamlit application
CMD streamlit run --server.port 8080 --server.enableCORS false aiagent.py


