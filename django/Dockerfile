# Use a standard, lightweight Python Debian image
FROM python:3.11-slim

ENV DEBIAN_FRONTEND=noninteractive

# 1. Install system dependencies for GeoDjango and OpenCV
RUN apt-get update && apt-get install -y \
    binutils \
    libproj-dev \
    gdal-bin \
    libgdal-dev \
    python3-gdal \
    libgl1 \
    libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

RUN pip install --no-cache-dir torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 4. Copy the rest of the Django project
COPY . .

# Expose the default Django port and Tello UDP ports
EXPOSE 8000
EXPOSE 8889/udp
EXPOSE 8890/udp
EXPOSE 11111/udp

CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]