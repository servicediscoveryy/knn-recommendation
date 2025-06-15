# Use official Python image
FROM python:3.10-slim

# Install required system packages for MongoDB SRV resolution
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    libnss3 \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy files
COPY . /app

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Expose port
EXPOSE 5000

# Run the app
CMD ["python", "app.py"]
