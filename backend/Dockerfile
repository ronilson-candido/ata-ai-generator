FROM python:3.10-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    ffmpeg \
    libavcodec-dev \
    libavformat-dev \
    libavutil-dev \
    libswscale-dev \
    libavfilter-dev \
    libavdevice-dev \
    pkg-config \
    git \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copy all requirements first
COPY requirements.txt ./
COPY backend/requirements.txt ./backend_requirements.txt

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt
RUN pip install --no-cache-dir -r backend_requirements.txt

# Copy application code
COPY . .

# Expose port
EXPOSE 8000

# Run FastAPI
CMD ["uvicorn", "backend.main:app", "--host", "0.0.0.0", "--port", "8000"]
