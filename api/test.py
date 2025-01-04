from TTS.api import TTS

model_path = "tts_models/multilingual/multi-dataset/xtts_v2"
tts_model = TTS(model_path)

# Generate speaker embedding
speaker_embedding = tts_model.get_speaker_embedding("./audio.wav")
print("Generated speaker embedding:", speaker_embedding)
