# Use an official Python runtime as a parent image
FROM python:3.12-slim

# Set the working directory in the container
WORKDIR /app

# Install python dependencies
COPY requirements.txt .

# Install dependencies + gunicorn
RUN pip install --no-cache-dir -r requirements.txt gunicorn

# Copy the current directory contents into the container at /app
COPY . .

# Create necessary directories for persistence
RUN mkdir -p instance uploads

# Expose port 5000
EXPOSE 5000

# Define the command to run the app using Gunicorn
# We use 4 workers for concurrency: for better handling of multiple requests
CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:5000", "app:create_app()"]
