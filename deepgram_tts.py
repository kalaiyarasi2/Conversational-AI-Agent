import requests
import soundfile as sf
import numpy as np
import pyaudio
import io
import os
from dotenv import load_dotenv
load_dotenv()

# Deepgram API key
DEEPGRAM_API_KEY = os.getenv('DEEPGRAM_API_KEY')
DEEPGRAM_TTS_URL = 'https://api.deepgram.com/v1/speak'

HEADERS = {
    'Authorization': f'Token {DEEPGRAM_API_KEY}',
    'Content-Type': 'application/json',
    'Accept': 'audio/wav',
}

def text_to_speech(text, output_file='output.wav', play_audio=True):
    data = {
        'text': text
    }
    response = requests.post(DEEPGRAM_TTS_URL, headers=HEADERS, json=data)
    if response.status_code != 200:
        print(f"Error: {response.status_code} - {response.text}")
        return
    audio_bytes = response.content
    # Save to file
    with open(output_file, 'wb') as f:
        f.write(audio_bytes)
    print(f"Audio saved to {output_file}")
    # Play audio if requested
    if play_audio:
        play_wav_file(output_file)

def play_wav_file(filename):
    data, samplerate = sf.read(filename, dtype='int16')
    p = pyaudio.PyAudio()
    stream = p.open(format=pyaudio.paInt16,
                    channels=1,
                    rate=samplerate,
                    output=True)
    stream.write(data.tobytes())
    stream.stop_stream()
    stream.close()
    p.terminate()

def main():
    text = input("Enter text to synthesize: ")
    text_to_speech(text)

if __name__ == "__main__":
    main() 