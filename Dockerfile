# Use the official Python slim image for a smaller footprint
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Set environment variables to prevent Python from writing .pyc files
# and to ensure stdout/stderr are unbuffered
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    STREAMLIT_SERVER_PORT=8501 \
    STREAMLIT_SERVER_ADDRESS=0.0.0.0

# Install system dependencies (needed for cryptography/compiling)
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        gcc \
        libffi-dev \
        libssl-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements file first to leverage Docker cache
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code
COPY . .

# Tun Tests
RUN python -m unittest discover -s ./tests -p "test_*.py"

# Expose the standard Streamlit port
EXPOSE 8501

# Run the application
CMD ["streamlit", "run", "main.py", "--server.port=8501", "--server.address=0.0.0.0"]
