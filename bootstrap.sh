#!/bin/bash
# bootstrap.sh
# This script sets up the environment for Coqui TTS and Wav2Lip

set -e  # Exit immediately if a command exits with a non-zero status

# Configuration: environment names
COQUI_ENV="coqui-tts_0"
WAV2LIP_ENV="wav2lip_0"

# System dependencies
if ! command -v ffmpeg &> /dev/null
then
    echo "ffmpeg not found, installing..."
    sudo apt-get update
    sudo apt-get install -y ffmpeg
else
    echo "ffmpeg is already installed, skipping..."
fi

# Initialize conda for shell scripts
eval "$(conda shell.bash hook)"

# -------------------------------
# Coqui TTS environment
echo "Creating and setting up conda environment: $COQUI_ENV"
conda create -n $COQUI_ENV python=3.10 -y
conda activate $COQUI_ENV

echo "Installing PyTorch (CUDA 12.1) and TTS dependencies..."
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121
pip install TTS
pip install srt

# Force specific versions
pip install "transformers==4.37.2" --force-reinstall
pip install "numpy==1.22.0" --force-reinstall
pip install "scipy==1.11.4" "soundfile<0.13" --force-reinstall
pip install sentencepiece

conda deactivate

# -------------------------------
# Wav2Lip environment
echo "Creating and setting up conda environment: $WAV2LIP_ENV"
conda create -n $WAV2LIP_ENV python=3.8 -y
conda activate $WAV2LIP_ENV

echo "Installing Wav2Lip requirements..."
pip install -r src/Wav2Lip/requirements.txt

echo "Installing PyTorch (CUDA 11.8) for Wav2Lip..."
pip install torch==2.0.1+cu118 torchvision==0.15.2+cu118 torchaudio==2.0.2 --index-url https://download.pytorch.org/whl/cu118

conda deactivate

echo "Bootstrap complete! Both environments are ready."
