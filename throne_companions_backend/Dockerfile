# Throne Companions Backend - Standalone Dockerfile
FROM python:3.11-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy and install Python dependencies
COPY requirements.txt ./
RUN pip install --extra-index-url https://d33sy5i8bnduwe.cloudfront.net/simple/ --no-cache-dir -r requirements.txt

# Copy backend code
COPY . .

# Expose port
EXPOSE 8001

# Set environment variables
ENV PYTHONPATH=/app
ENV PORT=8001

# Start command
CMD ["python", "server.py"]
