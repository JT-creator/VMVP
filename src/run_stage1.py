import srt
import subprocess
import argparse
import os

from utils import get_video_duration_str, get_audio_duration, srt_str_to_sec
from translate_en2de import translate_all
from tts import voice_cloning
from sync_audio_visual import sync_video_audio

# subtitle_file = 'examples/Tanzania-caption.srt'
# video_file = 'examples/Tanzania-2.mp4'
# task_name = 'tanzania'
# candidate_time = 5
# temp_output_video = f'workspace/{task_name}/temp_output_video.mp4'
# temp_output_audio = f'workspace/{task_name}/temp_output_audio.wav'

def parse_args():
    parser = argparse.ArgumentParser(description="Process subtitles and prepare audio/video segments.")
    parser.add_argument("--subtitle_file", type=str, default="examples/Tanzania-caption.srt",
                        help="Path to the subtitle file (.srt)")
    parser.add_argument("--video_file", type=str, default="examples/Tanzania-2.mp4",
                        help="Path to the input video file")
    parser.add_argument("--task_name", type=str, default="tanzania",
                        help="Task or workspace name")
    parser.add_argument("--candidate_time", type=int, default=5,
                        help="Number of candidates TTD to generate per clip")
    parser.add_argument("--temp_output_video", type=str, default=None,
                        help="Temporary output video path")
    parser.add_argument("--temp_output_audio", type=str, default=None,
                        help="Temporary output audio path")
    return parser.parse_args()

args = parse_args()

# === Assign variables ===
subtitle_file = args.subtitle_file
video_file = args.video_file
task_name = args.task_name
candidate_time = args.candidate_time
temp_output_video = args.temp_output_video
temp_output_audio = args.temp_output_audio

workspace_dir = f'workspace/{task_name}'
os.makedirs(workspace_dir, exist_ok=True)


if __name__ == "__main__":
    with open(subtitle_file, "r", encoding="utf-8") as f:
        subtitles = list(srt.parse(f.read()))

    len_video = get_video_duration_str(video_file)

    video_clips = []
    for sub_idx in range(len(subtitles)):
        sub = subtitles[sub_idx]
        # print(sub.start, sub.end, sub.content)
        # print(type(sub.start), type(sub.end), type(sub.content))
        if sub_idx == 0 and sub.start.total_seconds() > 0:
            video_clips.append(["00:00:00.000", str(sub.start), ""])
        if sub_idx > 0 and subtitles[sub_idx - 1].end < sub.start:
            video_clips.append([str(subtitles[sub_idx - 1].end), str(sub.start), ""])
        video_clips.append([str(sub.start), str(sub.end), sub.content])
        if sub_idx == len(subtitles) - 1 and sub.end < len_video:
            video_clips.append([str(sub.end), str(len_video), ""])

    # Translate all texts in video_clips
    text_en_list = [clip[2] for clip in video_clips if clip[2].strip() != '']
    text_de_list = translate_all(text_en_list)
    # append translated texts back to video_clips
    de_idx = 0
    for idx in range(len(video_clips)):
        if video_clips[idx][2].strip() != '':
            video_clips[idx][2] = text_de_list[de_idx]
            de_idx += 1

    # with video_clips[start, end, text], extract audio clips and put them in workspace/{task_name}/audio_clips_en/
    subprocess.run(['mkdir', '-p', f'workspace/{task_name}/audio_clips_en/'])
    for idx, clip in enumerate(video_clips):
        start, end, text = clip
        output_audio_path = f'workspace/{task_name}/audio_clips_en/clip_{idx:03d}.wav'
        cmd = [
            "ffmpeg",
            "-i", video_file,
            "-ss", start,
            "-to", end,
            "-q:a", "0",
            "-map", "a",
            output_audio_path,
            "-y"
        ]
        subprocess.run(cmd)
    # Record into video_clips
    for idx, clip in enumerate(video_clips):
        clip.append(f'workspace/{task_name}/audio_clips_en/clip_{idx:03d}.wav')

    # Now do voice cloning TTS for all clips
    tts_dir = f'workspace/{task_name}/audio_clips_de'
    subprocess.run(['mkdir', '-p', tts_dir])
    spaeker_embed_audio = f'workspace/{task_name}/audio_clips_en/full.wav'
    subprocess.run([
            "ffmpeg",
            "-i", video_file,
            "-q:a", "0",
            "-map", "a",
            spaeker_embed_audio,
            "-y"
        ])
    audio_de_paths = voice_cloning(video_clips, tts_dir, spaeker_embed_audio, candidate_time)
    # Replace audio paths in video_clips with audio_de_paths
    for idx in range(len(video_clips)):
        if video_clips[idx][2].strip() != '':
            video_clips[idx][3] = audio_de_paths[idx]

    # Finally sync audio and video
    video_workspace_dir = f'workspace/{task_name}/video_clips'
    subprocess.run(['mkdir', '-p', video_workspace_dir])
    sync_video_audio(VIDEO_CLIPS=video_clips, 
                    output_video_path=temp_output_video, 
                    input_video_path=video_file, 
                    video_workspace_dir=video_workspace_dir)

    cmd = [
        "ffmpeg",
        "-i", temp_output_video,
        "-q:a", "0",
        "-map", "a",
        temp_output_audio,
        "-y"
    ]
    subprocess.run(cmd)