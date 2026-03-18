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

# 3. Install the rest of your specific project dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 4. Copy the rest of the Django project
COPY . .

# Expose the default Django port
EXPOSE 8000

# Run the development server
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000", "--noreload"]