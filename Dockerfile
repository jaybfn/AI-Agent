# Use an official Python runtime as a parent image
FROM python:3.10-slim
# Allow statements and log messages to immediately appear in knative logs
ENV PYTHONUNBUFFERED True
EXPOSE 8080
# copy local code to the container image.
ENV APP_HOME /app
WORKDIR $APP_HOME
COPY . ./
# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt
# Run aiagent.py when the container launches
CMD streamlit run --server.port 8080 --server.enableCORS false app.py

