# Base image with PyTorch, CUDA, and cuDNN
FROM pytorch/pytorch:1.10.0-cuda11.3-cudnn8-runtime

# Install dependencies
RUN apt-get update && apt-get install -y \
    git \
    libgl1-mesa-glx \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
RUN pip install -U openmim
RUN mim install "mmcv-full>=1.3.0,<1.4.0"
RUN mim install mmengine

# Clone MMDetection repository
RUN git clone https://github.com/open-mmlab/mmdetection.git /mmdetection

# Set working directory
WORKDIR /mmdetection

# Install MMDetection
RUN pip install -v -e .