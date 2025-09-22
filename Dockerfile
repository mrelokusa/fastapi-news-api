# Use an official Python runtime as a parent image
FROM python:3.11-slim

# Set the working directory in the container
WORKDIR /app

# Copy the requirements file into the container at /app
COPY ./requirements.txt /app/requirements.txt

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir --upgrade -r /app/requirements.txt

# Copy the rest of your app's source code from your host to your image filesystem.
COPY . /app

# The command to run your application
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8080"]
