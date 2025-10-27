# Video Translation MVP (Coqui TTS + Wav2Lip)

This project builds a **Video Translation MVP** that automatically generates synchronized lip movements and translated speech using:
- [Coqui TTS](https://github.com/coqui-ai/TTS) for text-to-speech generation  
- [Wav2Lip](https://github.com/Rudrabha/Wav2Lip) for lip-syncing speech to video  

---

## Prerequisites

Before running, ensure:
- **Software:** Conda, ffmpeg, Python 
- **Operating System:** Ubuntu 20.04 (tested)  
- **CUDA:** 12.1 (tested) or compatible version  
- **Hardware:** NVIDIA GPU with CUDA support, e.g., A100-SXM4-80GB (tested) or similar 

---

## 1. Environment Setup

Run the bootstrap script to install dependencies and create environments:

```bash
bash bootstrap.sh
```

Alternatively, you can follow the instructions in the script to manually perform each step. The script will:
- Installs `ffmpeg` (if not already installed)
- Creates two Conda environments:
  - `coqui-tts` → for speech synthesis
  - `wav2lip` → for video lip-sync
- Installs all necessary Python dependencies

---

## 2. Download Model Checkpoints

You can download the required model checkpoints using the provided script:

```bash
bash download_ckp.sh
```

Alternatively, you can manually download the files. The script will download:
- `s3fd.pth` — face detection model [S3FD](https://www.adrianbulat.com/downloads/python-fan/s3fd-619a316812.pth)
- `Wav2Lip-SD-GAN.pth` — Wav2Lip generator model  [Wav2Lip SD-GAN](https://drive.google.com/uc?id=15G3U08c8xsCkOqQxE38Z2XXDnPcOptNk)

And saved to:
```
src/Wav2Lip/face_detection/detection/sfd/s3fd.pth
src/Wav2Lip/checkpoints/Wav2Lip-SD-GAN.pt
```

---

## 3. Run the Full Pipeline

Run the pipeline script:

```bash
bash run_pipeline.sh
```

This script:
1. Activates the **Coqui TTS** environment  
2. Runs audio translation and video synchronization (`src/run_stage1.py`)  
3. Activates the **Wav2Lip** environment  
4. Runs video lip-sync inference (`src/Wav2Lip/inference.py`)

---

## Customize the Run

You can pass arguments to `run_pipeline.sh` or edit the variables at lines 10–18 of the script. Defaults are provided if no arguments are given:

```bash
SUBTITLE_FILE="${1:-examples/Tanzania-caption.srt}"
VIDEO_FILE="${2:-examples/Tanzania-2.mp4}"
TASK_NAME="${3:-tanzania}"
CANDIDATE_TIME="${4:-5}"
RESULT_FOLDER="${5:-results/${TASK_NAME}}"
```
- SUBTITLE_FILE — path to the input subtitle file (.srt)
- VIDEO_FILE — path to the input video
- TASK_NAME — name for this task; used to organize workspace
- CANDIDATE_TIME — number of candidates TTD to generate per clip
- RESULT_FOLDER — directory to store final outputs

Then run:
```bash
bash run_pipeline.sh
```

The resulting video will be saved at the path defined by RESULT_FOLDER.

---

## Example Output

After running, you will find:
- The updated video file with seamless transitions and synchronization:
```
results/tanzania/final_output_video.mp4
```
- The new audio file generated based on the translated transcription:
```
results/tanzania/output_audio.wav
```

---

## Project Structure

```
├── bootstrap.sh                # Environment setup
├── download_ckp.sh             # Model checkpoint downloader
├── run_pipeline.sh             # Full Coqui TTS → Wav2Lip pipeline
├── src/
│   ├── run_stage1.py           # Audio translation and video synchronization
│   └── Wav2Lip/                # Wav2Lip model
|       └── inference.py        # Lip-sync
└── workspace/                  # Intermediate/final outputs
└── temp/                       # Intermediate files
```

---

## Pipeline Overview


---

## Assumptions and Limitations
- The pipeline assumes a single face is present in the video for lip-syncing.
- GPU with sufficient VRAM is required; otherwise, you must reduce `--resize_factor` for large videos.
- Subtitle and video must be roughly aligned in timing.
- Models are trained on general datasets and may not perfectly match all speech styles or languages.

---

## Credits

- [Wav2Lip](https://github.com/Rudrabha/Wav2Lip)  
- [Coqui TTS](https://github.com/coqui-ai/TTS)

---

## License

MIT License © 2025