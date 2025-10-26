import srt
import subprocess
import json
from datetime import timedelta

from transformers import MarianMTModel, MarianTokenizer
from TTS.api import TTS

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

def translate_all(text_list):
    tokenizer = MarianTokenizer.from_pretrained("Helsinki-NLP/opus-mt-en-de")
    model = MarianMTModel.from_pretrained("Helsinki-NLP/opus-mt-en-de")

    def translate_one(text):
        inputs = tokenizer(text, return_tensors="pt", padding=True)
        translated = model.generate(**inputs)
        return tokenizer.decode(translated[0], skip_special_tokens=True)

    return [translate_one(text) for text in text_list]

subtitle_file = 'examples/Tanzania-caption.srt'
video_file = 'examples/Tanzania-2.mp4'
task_name = 'tanzania'
candidate_time = None

def voice_cloning(video_clips, output_tts_dir, spaeker_embed_audio, candidate_time=1):
    tts = TTS("tts_models/multilingual/multi-dataset/xtts_v2", progress_bar=False, gpu=True)

    #speaker_embedding = tts.get_speaker_embedding(spaeker_embed_audio)
    audio_de_paths = [] 
    for idx, clip in enumerate(video_clips):
        start, end, text, audio_path = clip
        if text.strip() == '':
            continue
        
        target_duration = get_audio_duration(audio_path)
        candidate_paths = []
        for i in range(candidate_time):
            candidate_file = f"{output_tts_dir}/clip_{idx:03d}_candidate{i}.wav"
            tts.tts_to_file(
                text=text,
                file_path=candidate_file,
                speaker_wav=[audio_path, spaeker_embed_audio],
                language="de"
            )
            candidate_paths.append(candidate_file)

        # Select candidate with median duration
        durations = [(p, get_audio_duration(p)) for p in candidate_paths]
        durations.sort(key=lambda x: x[1])
        median_idx = (len(durations) - 1) // 2  # lower median for even counts
        best_path = durations[median_idx][0]
        # Remove other candidates
        for cpath in candidate_paths:
            if cpath != best_path:
                subprocess.run(['rm', cpath])
        audio_de_paths.append(best_path)

    return audio_de_paths

def sync_video_audio(VIDEO_CLIPS, output_video_path, input_video_path, video_workspace_dir):
    sync_video_list = []

    for idx, clip in enumerate(VIDEO_CLIPS):
        start, end, text, audio_path = clip
        
        original_video_clip = f'{video_workspace_dir}/original_clip_{idx:03d}.mp4'
        sync_video_clip = f'{video_workspace_dir}/synced_clip_{idx:03d}.mp4'
        clip_with_audio = f'{video_workspace_dir}/clip_with_audio_{idx:03d}.mp4'

        subprocess.run([
            "ffmpeg", "-y",
            "-i", input_video_path,
            "-ss", str(start),
            "-to", str(end),
            original_video_clip
        ], check=True)
        
        original_duration = srt_str_to_sec(end) - srt_str_to_sec(start)
        tts_audio_duration = get_audio_duration(audio_path)
        speed_factor = tts_audio_duration / original_duration if original_duration > 0 else 1.0

        # setpts=PTS/FACTOR speeds up or slows down video
        ffmpeg_cmd = [
            "ffmpeg",
            "-y",  # overwrite output
            "-i", original_video_clip,
            "-filter:v", f"setpts={speed_factor}*PTS",
            "-an", # no audio
            sync_video_clip
        ]
        subprocess.run(ffmpeg_cmd, check=True)


        # Merge stretched video with German audio
        subprocess.run([
            "ffmpeg", "-y",
            "-i", sync_video_clip,
            "-i", audio_path,
            "-c:v", "copy",
            "-c:a", "aac",
            "-strict", "experimental",
            clip_with_audio
        ], check=True)

        sync_video_list.append(clip_with_audio)

    # Concatenate all synced video clips
    concat_file = f"{video_workspace_dir}/concat_list.txt"
    with open(concat_file, "w") as f:
        for clip_file in sync_video_list:
            f.write(f"file '{clip_file[-len('clip_with_audio_000.mp4'):]}'\n")

    subprocess.run([
        "ffmpeg",
        "-y",
        "-f", "concat",
        "-safe", "0",
        "-i", concat_file,
        "-c", "copy",
        output_video_path
    ], check=True)



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
audio_de_paths = voice_cloning(video_clips, tts_dir, spaeker_embed_audio)
# Replace audio paths in video_clips with audio_de_paths
for idx in range(len(video_clips)):
    if video_clips[idx][2].strip() != '':
        video_clips[idx][3] = audio_de_paths[idx]

print(video_clips)
video_workspace_dir = f'workspace/{task_name}/video_clips'
subprocess.run(['mkdir', '-p', video_workspace_dir])
temp_output_video = f'workspace/{task_name}/temp_output_video.mp4'
sync_video_audio(VIDEO_CLIPS=video_clips, 
                 output_video_path=temp_output_video, 
                 input_video_path=video_file, 
                 video_workspace_dir=video_workspace_dir)