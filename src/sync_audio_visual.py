from utils import get_audio_duration, srt_str_to_sec
import subprocess
import datetime
import srt

def sync_video_audio(VIDEO_CLIPS, output_video_path, input_video_path, video_workspace_dir, output_srt_path):
    sync_video_list = []
    translated_subtitles = []
    current_time = 0.0  # track cumulative timeline in seconds

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

        # === Record updated subtitle timing ===
        if text.strip() != '':
            start_time = current_time
            end_time = current_time + tts_audio_duration
            translated_subtitles.append(
                srt.Subtitle(
                    index=len(translated_subtitles) + 1,
                    start=datetime.timedelta(seconds=start_time),
                    end=datetime.timedelta(seconds=end_time),
                    content=text
                )
            )
        current_time += tts_audio_duration  # advance timeline

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

    # === Save new translated subtitles ===
    with open(output_srt_path, "w", encoding="utf-8") as f:
        f.write(srt.compose(translated_subtitles))
