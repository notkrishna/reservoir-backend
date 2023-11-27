# Use an official Python runtime as the base image
FROM python:3.9-slim

# Set environment variables for Python and Docker
ENV PYTHONUNBUFFERED 1
ENV PYTHONDONTWRITEBYTECODE 1

# Install system dependencies
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        build-essential \
        libpq-dev \
&& rm -rf /var/lib/apt/lists/*

# Create and set the working directory
WORKDIR /app

# Copy the requirements file and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the Django project code into the Docker image
COPY . .

# Expose the necessary port(s) for your Django application
EXPOSE 8000

# Set the entrypoint command to start the Django application
# CMD ["python", "manage.py", "shell"]

CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
