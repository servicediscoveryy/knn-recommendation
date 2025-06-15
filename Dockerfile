# Use official Python image
FROM python:3.11-slim

# Set working directory in container
WORKDIR /app

# Copy your code
COPY . /app

# Install dependencies
RUN pip install --no-cache-dir flask pymongo apyori

# Expose port your Flask app will run on
EXPOSE 5000

# Run your app
CMD ["python", "main.py"]
