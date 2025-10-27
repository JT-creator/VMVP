import subprocess
import json
from datetime import timedelta

def get_video_duration_str(path):
    result = subprocess.run(
        [
            "ffprobe", "-v", "error",
            "-show_entries", "format=duration",
            "-of", "json", path
        ],
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True
    )
    info = json.loads(result.stdout)
    seconds = float(info["format"]["duration"])
    return timedelta(seconds=seconds)

def get_audio_duration(path):
    """Return duration (seconds) using ffprobe."""
    result = subprocess.run(
        ["ffprobe", "-v", "error", "-show_entries", "format=duration",
        "-of", "default=noprint_wrappers=1:nokey=1", path],
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True
    )
    try:
        return float(result.stdout.strip())
    except:
        return 0.0

def srt_str_to_sec(time_str):
    """Convert time string like '0:00:04.436000' to seconds"""
    parts = time_str.split(":")
    h = int(parts[0])
    m = int(parts[1])
    s = float(parts[2])
    return h * 3600 + m * 60 + s