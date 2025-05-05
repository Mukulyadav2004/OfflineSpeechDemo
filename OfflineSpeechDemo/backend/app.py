from flask import Flask, request, jsonify
from flask_cors import CORS  # <-- Add this import
import os
import wave
import json
from vosk import Model, KaldiRecognizer

app = Flask(__name__)
CORS(app)  # <-- Add this line to enable CORS
models = {}

def load_model(lang='en'):
    if lang not in models:
        model_path = f"models/{lang}"
        if not os.path.exists(model_path):
            raise ValueError(f"Model for language '{lang}' not found.")
        models[lang] = Model(model_path)
    return models[lang]

@app.route("/transcribe", methods=["POST"])
def transcribe():
    lang = request.args.get("lang", "en")
    model = load_model(lang)

    if "audio" not in request.files:
        return jsonify({"error": "No audio file provided"}), 400

    audio_file = request.files["audio"]
    wf = wave.open(audio_file, "rb")
    if wf.getnchannels() != 1 or wf.getsampwidth() != 2 or wf.getcomptype() != "NONE":
        return jsonify({"error": "Audio must be mono WAV PCM format."}), 400

    rec = KaldiRecognizer(model, wf.getframerate())
    results = []
    while True:
        data = wf.readframes(4000)
        if len(data) == 0:
            break
        if rec.AcceptWaveform(data):
            results.append(json.loads(rec.Result()))
    results.append(json.loads(rec.FinalResult()))

    transcript = " ".join([r.get("text", "") for r in results])
    return jsonify({"transcript": transcript})

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)