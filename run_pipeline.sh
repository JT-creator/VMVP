#!/usr/bin/env bash
set -euo pipefail

# === Configurable environment names ===
COQUI_ENV="coqui-tts_0"
WAV2LIP_ENV="wav2lip_0"

# === Paths (edit if needed) ===
VIDEO_PATH="/home/jordanz/projects/tts/VMVP/workspace/tanzania/temp_output_video.mp4"
AUDIO_PATH="/home/jordanz/projects/tts/VMVP/workspace/tanzania/temp_output_audio.wav"
OUTFILE="resultV.mp4"
CHECKPOINT_PATH="src/Wav2Lip/checkpoints/Wav2Lip-SD-GAN.pt"

# === Helper: activate conda env safely ===
activate_env() {
  local env_name="$1"
  if ! conda env list | grep -qE "^${env_name}\s"; then
    echo "Conda environment '${env_name}' not found."
    exit 1
  fi
  echo "Activating environment: $env_name"
  source "$(conda info --base)/etc/profile.d/conda.sh"
  conda activate "$env_name"
}

# === Step 1: Run Coqui TTS preprocessing ===
activate_env "$COQUI_ENV"
echo "Running Coqui TTS step..."
python src/srt_reader.py
conda deactivate
echo "Coqui TTS step complete."

# === Step 2: Run Wav2Lip inference ===
activate_env "$WAV2LIP_ENV"
echo "Running Wav2Lip inference..."
python src/Wav2Lip/inference.py \
  --checkpoint_path "$CHECKPOINT_PATH" \
  --face "$VIDEO_PATH" \
  --audio "$AUDIO_PATH" \
  --outfile "$OUTFILE" \
  --pads 0 30 0 0
conda deactivate
echo "Wav2Lip inference complete."

echo "All done. Output video saved as: $OUTFILE"
