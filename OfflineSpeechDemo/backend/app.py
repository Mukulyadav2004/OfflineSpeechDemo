from flask import Flask, request, jsonify
from flask_cors import CORS
import os
import wave
import json
import logging
from vosk import Model, KaldiRecognizer
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app)

# Configuration
class Config:
    DEBUG = os.getenv('DEBUG', 'False').lower() == 'true'
    HOST = os.getenv('HOST', '0.0.0.0')
    PORT = int(os.getenv('PORT', 5000))
    MAX_CONTENT_LENGTH = int(os.getenv('MAX_CONTENT_LENGTH', 16 * 1024 * 1024))  # 16MB default

app.config['MAX_CONTENT_LENGTH'] = Config.MAX_CONTENT_LENGTH

# Global models cache
models = {}

def load_model(lang='en'):
    """Load and cache Vosk model for specified language"""
    if lang not in models:
        model_path = f"models/{lang}"
        if not os.path.exists(model_path):
            logger.error(f"Model for language '{lang}' not found at {model_path}")
            raise ValueError(f"Model for language '{lang}' not found.")
        
        logger.info(f"Loading model for language: {lang}")
        try:
            models[lang] = Model(model_path)
            logger.info(f"Successfully loaded model for language: {lang}")
        except Exception as e:
            logger.error(f"Failed to load model for language '{lang}': {str(e)}")
            raise
    
    return models[lang]

@app.route("/health", methods=["GET"])
def health_check():
    """Health check endpoint"""
    return jsonify({
        "status": "healthy",
        "service": "offline-speech-demo",
        "available_languages": list(models.keys()) if models else []
    }), 200

@app.route("/", methods=["GET"])
def root():
    """Root endpoint with API information"""
    return jsonify({
        "service": "Offline Speech Recognition API",
        "version": "1.0.0",
        "endpoints": {
            "/health": "Health check",
            "/transcribe": "Speech transcription (POST with audio file)",
            "/models": "List available models",
            "/demo": "Frontend demo page"
        }
    }), 200

@app.route("/demo", methods=["GET"])
def demo():
    """Serve the frontend demo page"""
    try:
        frontend_path = os.path.join(os.path.dirname(__file__), '..', 'frontend', 'index.html')
        with open(frontend_path, 'r') as f:
            return f.read(), 200, {'Content-Type': 'text/html'}
    except FileNotFoundError:
        return jsonify({"error": "Demo page not found"}), 404

@app.route("/models", methods=["GET"])
def list_models():
    """List available language models"""
    try:
        models_dir = "models"
        available_models = []
        if os.path.exists(models_dir):
            available_models = [d for d in os.listdir(models_dir) 
                             if os.path.isdir(os.path.join(models_dir, d))]
        
        return jsonify({
            "available_models": available_models,
            "loaded_models": list(models.keys())
        }), 200
    except Exception as e:
        logger.error(f"Error listing models: {str(e)}")
        return jsonify({"error": "Failed to list models"}), 500

@app.route("/transcribe", methods=["POST"])
def transcribe():
    """Transcribe audio file to text"""
    wf = None
    try:
        # Get language parameter
        lang = request.args.get("lang", "en")
        logger.info(f"Transcription request for language: {lang}")
        
        # Load model
        try:
            model = load_model(lang)
        except ValueError as e:
            logger.error(f"Model loading error: {str(e)}")
            return jsonify({"error": str(e)}), 400
        except Exception as e:
            logger.error(f"Unexpected model loading error: {str(e)}")
            return jsonify({"error": "Failed to load speech recognition model"}), 500

        # Check if audio file is provided
        if "audio" not in request.files:
            logger.warning("No audio file provided in request")
            return jsonify({"error": "No audio file provided"}), 400

        audio_file = request.files["audio"]
        
        # Check if file is selected
        if audio_file.filename == '':
            logger.warning("No audio file selected")
            return jsonify({"error": "No audio file selected"}), 400

        # Validate file size
        if request.content_length and request.content_length > app.config['MAX_CONTENT_LENGTH']:
            logger.warning(f"File too large: {request.content_length} bytes")
            return jsonify({"error": "File too large"}), 413

        # Open and validate audio file
        try:
            wf = wave.open(audio_file, "rb")
        except Exception as e:
            logger.error(f"Failed to open audio file: {str(e)}")
            return jsonify({"error": "Invalid audio file format"}), 400

        # Validate audio format
        if (wf.getnchannels() != 1 or 
            wf.getsampwidth() != 2 or 
            wf.getcomptype() != "NONE"):
            logger.warning("Invalid audio format")
            return jsonify({
                "error": "Audio must be mono WAV PCM format.",
                "details": {
                    "channels": wf.getnchannels(),
                    "sample_width": wf.getsampwidth(),
                    "compression": wf.getcomptype()
                }
            }), 400

        # Initialize recognizer
        try:
            rec = KaldiRecognizer(model, wf.getframerate())
        except Exception as e:
            logger.error(f"Failed to initialize recognizer: {str(e)}")
            return jsonify({"error": "Failed to initialize speech recognizer"}), 500

        # Process audio
        results = []
        total_frames = 0
        
        try:
            while True:
                data = wf.readframes(4000)
                if len(data) == 0:
                    break
                
                total_frames += len(data)
                
                if rec.AcceptWaveform(data):
                    result = json.loads(rec.Result())
                    if result.get("text"):  # Only add non-empty results
                        results.append(result)
            
            # Get final result
            final_result = json.loads(rec.FinalResult())
            if final_result.get("text"):
                results.append(final_result)
                
        except Exception as e:
            logger.error(f"Error during audio processing: {str(e)}")
            return jsonify({"error": "Error processing audio"}), 500

        # Compile transcript
        transcript = " ".join([r.get("text", "") for r in results]).strip()
        
        # Calculate confidence (if available)
        confidences = [r.get("conf", 0) for r in results if "conf" in r]
        avg_confidence = sum(confidences) / len(confidences) if confidences else None

        response = {
            "transcript": transcript,
            "language": lang,
            "segments": len(results),
            "total_frames_processed": total_frames
        }
        
        if avg_confidence is not None:
            response["average_confidence"] = round(avg_confidence, 3)

        logger.info(f"Transcription completed: {len(transcript)} characters")
        return jsonify(response), 200

    except Exception as e:
        logger.error(f"Unexpected error in transcribe endpoint: {str(e)}")
        return jsonify({"error": "Internal server error"}), 500
    
    finally:
        # Ensure wave file is properly closed
        if wf is not None:
            try:
                wf.close()
            except Exception as e:
                logger.error(f"Error closing wave file: {str(e)}")

@app.errorhandler(413)
def request_entity_too_large(error):
    """Handle file too large error"""
    return jsonify({"error": "File too large"}), 413

@app.errorhandler(500)
def internal_server_error(error):
    """Handle internal server errors"""
    logger.error(f"Internal server error: {str(error)}")
    return jsonify({"error": "Internal server error"}), 500

if __name__ == "__main__":
    logger.info(f"Starting server on {Config.HOST}:{Config.PORT}")
    logger.info(f"Debug mode: {Config.DEBUG}")
    app.run(debug=Config.DEBUG, host=Config.HOST, port=Config.PORT)