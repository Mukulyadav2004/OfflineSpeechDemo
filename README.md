# OfflineSpeechDemo

This project demonstrates an **offline ASR system** using [Vosk](https://alphacephei.com/vosk/) with a Python Flask backend and web frontend.

![Offline Speech Recognition Demo](https://github.com/user-attachments/assets/5bca9c84-bf2f-41f6-a5bf-eaa465305d4d)

## 🚀 Features

- **Offline speech-to-text** using Vosk AI models
- **Multilingual support** (English, Hindi, and more)
- **REST API** with comprehensive endpoints
- **Web interface** for easy testing and demonstration
- **Dockerized** backend with health checks
- **Production-ready** with proper error handling and logging
- **Confidence scores** and detailed transcription metadata
- **File upload validation** and security measures

## 🛠 Setup Instructions

### Quick Start with Docker

1. **Clone the repository:**
```bash
git clone https://github.com/Mukulyadav2004/OfflineSpeechDemo.git
cd OfflineSpeechDemo
```

2. **Download Vosk models** (required):
```bash
# English model (small)
cd OfflineSpeechDemo/backend/models
wget https://alphacephei.com/vosk/models/vosk-model-small-en-us-0.15.zip
unzip vosk-model-small-en-us-0.15.zip
mv vosk-model-small-en-us-0.15 en

# Hindi model (optional)
wget https://alphacephei.com/vosk/models/vosk-model-small-hi-0.22.zip
unzip vosk-model-small-hi-0.22.zip
mv vosk-model-small-hi-0.22 hin
```

3. **Start with Docker:**
```bash
docker-compose up --build
```

4. **Access the application:**
   - **Web Demo**: http://localhost:5000/demo
   - **API Documentation**: http://localhost:5000/
   - **Health Check**: http://localhost:5000/health

### Manual Setup

1. **Install Python dependencies:**
```bash
cd OfflineSpeechDemo/backend
pip install -r requirements.txt
```

2. **Configure environment** (optional):
```bash
cp .env.example .env
# Edit .env with your preferences
```

3. **Start the server:**
```bash
python app.py
```

## 📖 API Documentation

### Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/` | GET | API information and available endpoints |
| `/health` | GET | Health check and system status |
| `/models` | GET | List available and loaded language models |
| `/transcribe` | POST | Transcribe audio file to text |
| `/demo` | GET | Web interface for testing |

### Transcription API

**POST** `/transcribe?lang=en`

**Parameters:**
- `lang` (query): Language code (en, hin, etc.) - default: en

**Request:**
- Content-Type: `multipart/form-data`
- Body: Audio file with key `audio`
- Supported format: WAV, mono, 16-bit PCM

**Response:**
```json
{
  "transcript": "Hello world",
  "language": "en",
  "segments": 2,
  "total_frames_processed": 32000,
  "average_confidence": 0.924
}
```

**Example with curl:**
```bash
curl -X POST -F 'audio=@recording.wav' \
  http://localhost:5000/transcribe?lang=en
```

## 🧪 Testing

Run the comprehensive test suite:
```bash
cd OfflineSpeechDemo/backend
python test_api.py
```

## 🔧 Configuration

Environment variables can be set in `.env` file:

```env
DEBUG=False
HOST=0.0.0.0
PORT=5000
MAX_CONTENT_LENGTH=16777216  # 16MB
LOG_LEVEL=INFO
```

## 📝 Audio Requirements

For best results, ensure your audio files meet these requirements:
- **Format**: WAV
- **Channels**: Mono (1 channel)
- **Sample Rate**: 16kHz recommended
- **Bit Depth**: 16-bit PCM
- **Quality**: Clear speech, minimal background noise

## 🐳 Docker Deployment

The included `docker-compose.yml` provides a production-ready setup:

- Health checks with automatic restart
- Security hardening (non-root user)
- Volume mounting for models
- Environment configuration

## 🔒 Security Features

- Input validation and sanitization
- File size limits (16MB default)
- Error handling without information leakage
- Non-root Docker container
- CORS protection

## 🚀 Production Deployment

For production use:

1. Set `DEBUG=False` in environment
2. Use a production WSGI server (e.g., Gunicorn):
   ```bash
   pip install gunicorn
   gunicorn -w 4 -b 0.0.0.0:5000 app:app
   ```
3. Add reverse proxy (nginx) for SSL termination
4. Configure proper logging and monitoring
5. Set up backup for model files

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your improvements
4. Add tests if applicable
5. Submit a pull request

## 📄 License

This project is open source and available under the [MIT License](LICENSE).

## 🙏 Acknowledgments

- [Vosk](https://alphacephei.com/vosk/) for the excellent offline speech recognition
- [Flask](https://flask.palletsprojects.com/) for the web framework
- Contributors and the open source community
