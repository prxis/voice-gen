import os
from flask import Flask, request, render_template, send_file, send_from_directory, jsonify
from TTS.api import TTS  # Only import TTS
from pydub import AudioSegment
import torch

# Force CPU usage
device = "cpu"
torch.set_default_device(device)



app = Flask(__name__)
UPLOAD_FOLDER = "static/audio"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

AUDIO_DIRECTORY = os.path.join(app.root_path, 'static', 'preview')

# Specify the model path manually
model_path = "tts_models/multilingual/multi-dataset/xtts_v2"  # Replace with your desired model ID
tts_model = TTS(model_path)

# Function to generate TTS audio
def generate_voice(text, output_file, speaker):
    #speaker = "Ana Florence"
    tts_model.tts_to_file(text=text, speaker=speaker, language="en", file_path=output_file)

# Function to lower the pitch
def lower_pitch(input_file, output_file, semitones=-3):
    audio = AudioSegment.from_file(input_file)
    deeper_audio = audio._spawn(audio.raw_data, overrides={
        "frame_rate": int(audio.frame_rate )
    }).set_frame_rate(audio.frame_rate) #* (2 ** (semitones / 12))
    deeper_audio.export(output_file, format="wav")

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        text = request.form["text"]
        speaker = request.form["selected_speaker"]
        tts_file = os.path.join(UPLOAD_FOLDER, "tts_output.wav")
        deep_voice_file = os.path.join(UPLOAD_FOLDER, f"{speaker}.wav")
        
        # Generate TTS and lower pitch
        generate_voice(text, tts_file, speaker)
        lower_pitch(tts_file, deep_voice_file)
        
        return render_template("index.html", download_link=f"{speaker}.wav")
        
    
    return render_template("index.html", download_link=None)

@app.route("/download/<filename>")
def download(filename):
    file_path = os.path.join(UPLOAD_FOLDER, filename)
    return send_file(file_path, as_attachment=True)


@app.route('/audio')
def home():
    # Render the main preview page
    return render_template('preview.html')

@app.route('/audio-files')
def list_audio_files():
    """
    Endpoint to list all .wav files in the AUDIO_DIRECTORY.
    """
    if not os.path.exists(AUDIO_DIRECTORY):
        return jsonify({"error": "Audio directory not found"}), 404

    # Get all .wav files in the directory
    files = [f for f in os.listdir(AUDIO_DIRECTORY) if f.endswith('.wav')]
    return jsonify({"files": files})

@app.route('/about')
def about():
    return render_template('about.html')


if __name__ == "__main__":
    app.run(port=8081)
