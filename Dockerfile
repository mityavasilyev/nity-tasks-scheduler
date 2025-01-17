FROM --platform=linux/amd64 python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first to leverage Docker cache
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

EXPOSE 80
EXPOSE 50051

# Use an argument to specify the main file at build time
ARG MAIN_FILE=main.py

# Use the argument in the CMD
CMD ["python", "${MAIN_FILE}"]