FROM python:3.10-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    software-properties-common \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Install Playwright browsers
RUN playwright install chromium

# Copy application code
COPY huizenzoeker/ /app/huizenzoeker/
COPY main.py /app/

# Create directories for templates, static files, and data
RUN mkdir -p /app/templates /app/static /app/data

# Set environment variables
ENV PYTHONUNBUFFERED=1

# Expose port for web interface
EXPOSE 5000

# Run the application
CMD ["python", "main.py"]
