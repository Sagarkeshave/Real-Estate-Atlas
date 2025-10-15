# # Use lightweight Python base image
# FROM python:3.12-slim

# # Set working directory
# WORKDIR /app

# # Copy all project files
# COPY . /app

# # Install dependencies
# RUN pip install --no-cache-dir -r requirements.txt

# # Expose the port Hugging Face expects
# EXPOSE 7860

# # Run the Flask app
# CMD ["python", "app.py"]

# Dockerfile
# Use a slim Python image
FROM python:3.11-slim

# Set the working directory
WORKDIR /app

# Install system dependencies needed for the embedding model (if any, though often not needed for all-mpnet-base-v2)
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements file and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application files
COPY . .

# Expose the port (must match the port in app.py)
EXPOSE 5051

# Define the command to run the application
# We use the Gunicorn WSGI server for production instead of Flask's built-in server.
# Gunicorn is more robust for deployment.
# We map the host and port to 0.0.0.0:5051 as configured in your app.py
CMD ["gunicorn", "--bind", "0.0.0.0:5051", "app:app"]