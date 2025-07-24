# Use NVIDIA CUDA base image with Python
FROM nvidia/cuda:11.7-devel-ubuntu20.04

# Set environment variables
ENV DEBIAN_FRONTEND=noninteractive
ENV PYTHONUNBUFFERED=1
ENV CUDA_HOME=/usr/local/cuda

# Install system dependencies
RUN apt-get update && apt-get install -y \
    python3 \
    python3-pip \
    python3-dev \
    git \
    wget \
    curl \
    ffmpeg \
    libgl1-mesa-glx \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender-dev \
    libgomp1 \
    && rm -rf /var/lib/apt/lists/*

# Create symbolic link for python
RUN ln -s /usr/bin/python3 /usr/bin/python

# Upgrade pip
RUN python -m pip install --upgrade pip

# Set working directory
WORKDIR /app

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install -r requirements.txt

# Install additional optimizations
RUN pip install --no-deps xformers

# Copy application code
COPY handler.py .
COPY config.py .
COPY validation.py .

# Create cache directory for models
RUN mkdir -p /app/model_cache
ENV HF_HOME=/app/model_cache
ENV TRANSFORMERS_CACHE=/app/model_cache
ENV HF_DATASETS_CACHE=/app/model_cache

# Pre-download the model (optional - uncomment to cache model in image)
# RUN python -c "from diffusers import StableVideoDiffusionPipeline; StableVideoDiffusionPipeline.from_pretrained('stabilityai/stable-video-diffusion-img2vid-xt', torch_dtype='float16', variant='fp16')"

# Set the command to run the handler
CMD ["python", "handler.py"]