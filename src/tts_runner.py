from TTS.api import TTS

# Initialize model
tts = TTS("tts_models/multilingual/multi-dataset/xtts_v2", progress_bar=False, gpu=True)

# Generate sample output
tts.tts_to_file(
    text="Tansania, Heimat einiger der atemberaubendsten Wildtiere der Erde.",
    file_path="output_de.wav",
    speaker_wav="workspace/speech1.wav",  # <-- Replace with your reference speaker .wav file
    language="de"
)
