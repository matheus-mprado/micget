FROM python:3.11-slim

# Install system dependencies for audio, GUI, and system tray
RUN apt-get update && apt-get install -y \
    libasound-dev \
    portaudio19-dev \
    libx11-dev \
    libxext-dev \
    libxinerama-dev \
    libxi-dev \
    libxrandr-dev \
    libxcursor-dev \
    libxtst-dev \
    libpulse-dev \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy the application code
COPY main.py .

# Install Python dependencies
RUN pip install --no-cache-dir \
    speechrecognition \
    pystray \
    Pillow \
    psutil

# Set environment variables for display
ENV DISPLAY=:0

# Command to run the application
CMD ["python", "main.py"]