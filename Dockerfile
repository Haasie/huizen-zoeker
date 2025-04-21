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

# Create directories
RUN mkdir -p /app/templates /app/static/css /app/static/js /app/data

# Copy Python files
COPY *.py ./

# Copy HTML templates
COPY *.html /app/templates/

# Copy static files
COPY *.js /app/static/js/
COPY *.css /app/static/css/

# Copy other files
COPY *.txt ./
COPY *.md ./

# Set environment variables
ENV PYTHONUNBUFFERED=1

# Expose port for web interface
EXPOSE 5000

# Run the application
CMD ["python", "main.py"]
