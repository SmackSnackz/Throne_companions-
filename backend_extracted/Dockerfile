# ============================================================
# 🏰 Throne Companions - Standalone Backend Dockerfile for Render
# ============================================================

# Use official lightweight Python image
FROM python:3.11-slim

# Set working directory inside container
WORKDIR /app

# ------------------------------------------------------------
# Install system dependencies
# (build-essential fixes most package build errors)
# ------------------------------------------------------------
RUN apt-get update && apt-get install -y \
    build-essential \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# ------------------------------------------------------------
# Copy requirements first for dependency caching
# ------------------------------------------------------------
COPY requirements.txt .

# ------------------------------------------------------------
# Install Python dependencies
# Includes EmergentIntegrations from the private index
# ------------------------------------------------------------
RUN pip install --no-cache-dir -r requirements.txt && \
    pip install --no-cache-dir emergentintegrations \
    --extra-index-url https://d33sy5i8bnduwe.cloudfront.net/simple/

# ------------------------------------------------------------
# Copy all backend code into container
# ------------------------------------------------------------
COPY . .

# ------------------------------------------------------------
# Expose port (Render automatically maps this)
# ------------------------------------------------------------
EXPOSE 8001

# ------------------------------------------------------------
# Start the FastAPI application with Uvicorn
# ------------------------------------------------------------
CMD ["uvicorn", "server:app", "--host", "0.0.0.0", "--port", "8001"]
