#!/usr/bin/env python3
"""
Simple test script for the Offline Speech Recognition API
"""

import requests
import json
import os
import wave
import tempfile
import struct

def create_test_audio():
    """Create a simple test WAV file with sine wave"""
    sample_rate = 16000
    duration = 2  # seconds
    frequency = 440  # Hz (A4 note)
    
    # Generate sine wave data
    samples = []
    for i in range(int(sample_rate * duration)):
        t = i / sample_rate
        sample = int(32767 * 0.5 * (1 + 0.5 * (t % 1)))  # Quieter sine wave
        samples.append(struct.pack('<h', sample))
    
    # Create temporary WAV file
    temp_file = tempfile.NamedTemporaryFile(suffix='.wav', delete=False)
    
    with wave.open(temp_file.name, 'wb') as wf:
        wf.setnchannels(1)  # Mono
        wf.setsampwidth(2)  # 16-bit
        wf.setframerate(sample_rate)
        wf.writeframes(b''.join(samples))
    
    return temp_file.name

def test_api_endpoints():
    """Test all API endpoints"""
    base_url = "http://localhost:5000"
    
    print("🧪 Testing Offline Speech Recognition API")
    print("=" * 50)
    
    # Test health endpoint
    print("\n1. Testing /health endpoint...")
    try:
        response = requests.get(f"{base_url}/health")
        print(f"   Status: {response.status_code}")
        print(f"   Response: {response.json()}")
    except requests.exceptions.RequestException as e:
        print(f"   ❌ Error: {e}")
        return False
    
    # Test root endpoint
    print("\n2. Testing / endpoint...")
    try:
        response = requests.get(f"{base_url}/")
        print(f"   Status: {response.status_code}")
        print(f"   Response: {response.json()}")
    except requests.exceptions.RequestException as e:
        print(f"   ❌ Error: {e}")
    
    # Test models endpoint
    print("\n3. Testing /models endpoint...")
    try:
        response = requests.get(f"{base_url}/models")
        print(f"   Status: {response.status_code}")
        models_data = response.json()
        print(f"   Available models: {models_data.get('available_models', [])}")
        print(f"   Loaded models: {models_data.get('loaded_models', [])}")
    except requests.exceptions.RequestException as e:
        print(f"   ❌ Error: {e}")
    
    # Test transcription with invalid input
    print("\n4. Testing /transcribe endpoint (no file)...")
    try:
        response = requests.post(f"{base_url}/transcribe")
        print(f"   Status: {response.status_code}")
        print(f"   Response: {response.json()}")
    except requests.exceptions.RequestException as e:
        print(f"   ❌ Error: {e}")
    
    # Test transcription with test audio
    print("\n5. Testing /transcribe endpoint (with test audio)...")
    test_audio_path = None
    try:
        test_audio_path = create_test_audio()
        print(f"   Created test audio: {test_audio_path}")
        
        with open(test_audio_path, 'rb') as audio_file:
            files = {'audio': audio_file}
            response = requests.post(f"{base_url}/transcribe?lang=en", files=files)
            print(f"   Status: {response.status_code}")
            result = response.json()
            print(f"   Transcript: '{result.get('transcript', '')}'")
            
            if 'segments' in result:
                print(f"   Segments: {result['segments']}")
            if 'average_confidence' in result:
                print(f"   Confidence: {result['average_confidence']:.3f}")
                
    except requests.exceptions.RequestException as e:
        print(f"   ❌ Error: {e}")
    except Exception as e:
        print(f"   ❌ Unexpected error: {e}")
    finally:
        # Clean up test file
        if test_audio_path and os.path.exists(test_audio_path):
            os.unlink(test_audio_path)
            print(f"   Cleaned up test audio file")
    
    print("\n" + "=" * 50)
    print("✅ API testing completed!")
    print("\n💡 To test with real audio:")
    print("   1. Record a WAV file (mono, 16-bit PCM)")
    print("   2. Use curl:")
    print(f"      curl -X POST -F 'audio=@your_file.wav' {base_url}/transcribe?lang=en")
    print("   3. Or visit the demo page:")
    print(f"      {base_url}/demo")

if __name__ == "__main__":
    test_api_endpoints()