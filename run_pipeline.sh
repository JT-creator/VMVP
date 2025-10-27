#!/usr/bin/env bash
set -euo pipefail

# === Configurable environment names ===
COQUI_ENV="coqui-tts_0"
WAV2LIP_ENV="wav2lip_0"

# === Paths (edit if needed) ===
CHECKPOINT_PATH="src/Wav2Lip/checkpoints/Wav2Lip-SD-GAN.pt"

SUBTITLE_FILE="${1:-examples/Tanzania-caption.srt}"
VIDEO_FILE="${2:-examples/Tanzania-2.mp4}"
TASK_NAME="${3:-tanzania}"
CANDIDATE_TIME="${4:-5}"
RESULT_FOLDER="${5:-results/${TASK_NAME}}"

WORKSPACE_DIR="workspace/${TASK_NAME}"
OUTFILE="${WORKSPACE_DIR}/final_output_video.mp4"
TEMP_OUTPUT_VIDEO="${WORKSPACE_DIR}/stage1_output_video.mp4"
TEMP_OUTPUT_AUDIO="${WORKSPACE_DIR}/output_audio.wav"

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
python src/run_stage1.py \
  --subtitle_file "$SUBTITLE_FILE" \
  --video_file "$VIDEO_FILE" \
  --task_name "$TASK_NAME" \
  --candidate_time "$CANDIDATE_TIME" \
  --temp_output_video "$TEMP_OUTPUT_VIDEO" \
  --temp_output_audio "$TEMP_OUTPUT_AUDIO"
conda deactivate
echo "Coqui TTS step complete."

# === Step 2: Run Wav2Lip inference ===
activate_env "$WAV2LIP_ENV"
echo "Running Wav2Lip inference..."
python src/Wav2Lip/inference.py \
  --checkpoint_path "$CHECKPOINT_PATH" \
  --face "$TEMP_OUTPUT_VIDEO" \
  --audio "$TEMP_OUTPUT_AUDIO" \
  --outfile "$OUTFILE" \
  --pads 0 30 0 0
conda deactivate
echo "Wav2Lip inference complete."

mkdir -p "$RESULT_FOLDER"
cp "$OUTFILE" "$RESULT_FOLDER/"
cp "$TEMP_OUTPUT_AUDIO" "$RESULT_FOLDER/"

echo "All done. Output video saved as: $RESULT_FOLDER"
