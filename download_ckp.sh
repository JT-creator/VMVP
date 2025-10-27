#!/bin/bash
# download_checkpoints.sh
# This script downloads necessary checkpoints for Wav2Lip

set -e  # Exit if any command fails

# Create directories if they don't exist
mkdir -p src/Wav2Lip/face_detection/detection/sfd
mkdir -p src/Wav2Lip/checkpoints
mkdir -p temp

# Download S3FD face detection model
if [ ! -f src/Wav2Lip/face_detection/detection/sfd/s3fd.pth ]; then
    echo "Downloading S3FD face detection model..."
    wget "https://www.adrianbulat.com/downloads/python-fan/s3fd-619a316812.pth" -O src/Wav2Lip/face_detection/detection/sfd/s3fd.pth
else
    echo "S3FD model already exists, skipping..."
fi

# Download Wav2Lip SD-GAN checkpoint from Google Drive
# Using gdown to handle Google Drive links
if ! command -v gdown &> /dev/null
then
    echo "gdown not found, installing..."
    pip install gdown
fi

if [ ! -f src/Wav2Lip/checkpoints/Wav2Lip-SD-GAN.pt ]; then
    echo "Downloading Wav2Lip SD-GAN checkpoint..."
    gdown "https://drive.google.com/uc?id=15G3U08c8xsCkOqQxE38Z2XXDnPcOptNk" -O src/Wav2Lip/checkpoints/Wav2Lip-SD-GAN.pt
else
    echo "Wav2Lip checkpoint already exists, skipping..."
fi

echo "All checkpoints downloaded successfully!"
