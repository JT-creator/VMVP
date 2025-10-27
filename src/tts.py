from TTS.api import TTS
from utils import get_audio_duration
import subprocess

def voice_cloning(VIDEO_CLIPS, output_tts_dir, spaeker_embed_audio, candidate_time=1):
    tts = TTS("tts_models/multilingual/multi-dataset/xtts_v2", progress_bar=False, gpu=True)

    #speaker_embedding = tts.get_speaker_embedding(spaeker_embed_audio)
    audio_de_paths = [] 
    for idx, clip in enumerate(VIDEO_CLIPS):
        start, end, text, audio_path = clip
        if text.strip() == '':
            audio_de_paths.append(audio_path)
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