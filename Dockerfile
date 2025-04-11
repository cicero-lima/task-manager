# Use an official Python runtime as a parent image
FROM python:3.9-slim

# Set the working directory in the container
WORKDIR /app

# Copy the current directory contents into the container at /app
COPY . /app

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Expose the port that Flask will run on
EXPOSE 80

# Set the entry point for Gunicorn with a custom timeout of 60 seconds
CMD ["gunicorn", "--bind", "0.0.0.0:80", "--timeout", "60", "app:app"]