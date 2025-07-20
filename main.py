import whisper
import pyaudio
import threading
import queue
import numpy as np
import time
import argparse
import io
import soundfile as sf

class RealTimeTranscriber:
    def __init__(self, model_name="medium", chunk_duration=3, overlap=0.5):
        """
        Initialize real-time transcriber
        
        Args:
            model_name (str): Whisper model to use
            chunk_duration (float): Duration of each audio chunk in seconds
            overlap (float): Overlap between chunks in seconds
        """
        self.model_name = model_name
        self.chunk_duration = chunk_duration
        self.overlap = overlap
        self.sample_rate = 16000
        self.chunk_size = int(self.sample_rate * self.chunk_duration)
        self.overlap_size = int(self.sample_rate * self.overlap)
        
        # Audio recording parameters
        self.format = pyaudio.paInt16
        self.channels = 1
        self.frames_per_buffer = 1024
        
        # Threading
        self.audio_queue = queue.Queue()
        self.is_recording = False
        self.is_transcribing = False
        
        # Load Whisper model
        print(f"Loading Whisper model: {model_name}")
        self.model = whisper.load_model(model_name)
        print("Model loaded successfully!")
        
        # Audio buffer for overlap
        self.audio_buffer = np.array([])
        
        # Initialize PyAudio
        self.audio = pyaudio.PyAudio()
        
    def start_recording(self):
        """Start recording audio from microphone"""
        self.is_recording = True
        try:
            # Open microphone stream
            self.stream = self.audio.open(
                format=self.format,
                channels=self.channels,
                rate=self.sample_rate,
                input=True,
                frames_per_buffer=self.frames_per_buffer,
                stream_callback=self._audio_callback
            )
        except OSError as e:
            print(f"[OSError] Could not open microphone: {e}")
            list_microphones()
            raise
        print(f"🎤 Recording started... (chunk duration: {self.chunk_duration}s)")
        print("💡 Speak into your microphone. Press Ctrl+C to stop.")
        # Start transcription thread
        self.transcription_thread = threading.Thread(target=self._transcription_worker)
        self.transcription_thread.daemon = True
        self.transcription_thread.start()
        self.stream.start_stream()
        
    def _audio_callback(self, in_data, frame_count, time_info, status):
        """Callback function for audio stream"""
        if self.is_recording:
            # Convert bytes to numpy array
            audio_data = np.frombuffer(in_data, dtype=np.int16).astype(np.float32) / 32768.0
            self.audio_queue.put(audio_data)
        return (None, pyaudio.paContinue)
    
    def _transcription_worker(self):
        """Worker thread for transcription"""
        self.is_transcribing = True
        
        while self.is_transcribing:
            try:
                # Collect audio data for chunk_duration
                audio_chunk = []
                start_time = time.time()
                
                while time.time() - start_time < self.chunk_duration:
                    try:
                        data = self.audio_queue.get(timeout=0.1)
                        audio_chunk.extend(data)
                    except queue.Empty:
                        continue
                
                if audio_chunk:
                    audio_chunk = np.array(audio_chunk)
                    
                    # Add overlap from previous chunk
                    if len(self.audio_buffer) > 0:
                        audio_chunk = np.concatenate([self.audio_buffer, audio_chunk])
                    
                    # Store overlap for next chunk
                    if len(audio_chunk) > self.overlap_size:
                        self.audio_buffer = audio_chunk[-self.overlap_size:]
                    
                    # Transcribe the chunk
                    self._transcribe_chunk(audio_chunk)
                    
            except Exception as e:
                print(f"Error in transcription worker: {e}")
                
    def _transcribe_chunk(self, audio_data):
        """Transcribe a chunk of audio data using in-memory processing"""
        try:
            # Skip if audio is too short or too quiet
            if len(audio_data) < self.sample_rate * 0.5:  # Less than 0.5 seconds
                return
                
            # Check if audio has enough volume
            if np.abs(audio_data).mean() < 0.001:  # Very quiet
                return
            
            # Transcribe directly using numpy array
            result = self.model.transcribe(audio_data, fp16=False)
            
            # Print transcription if not empty
            text = result['text'].strip()
            if text and len(text) > 1:  # Ignore very short transcriptions
                timestamp = time.strftime("%H:%M:%S")
                print(f"[{timestamp}] {text}")
                    
        except Exception as e:
            print(f"Error transcribing chunk: {e}")
    
    def stop_recording(self):
        """Stop recording and transcription"""
        print("\n🛑 Stopping recording...")
        self.is_recording = False
        self.is_transcribing = False
        
        if hasattr(self, 'stream'):
            self.stream.stop_stream()
            self.stream.close()
        
        self.audio.terminate()
        print("✅ Recording stopped.")
    
    def __del__(self):
        """Cleanup"""
        if hasattr(self, 'audio'):
            self.audio.terminate()

def list_microphones():
    """List available microphones"""
    audio = pyaudio.PyAudio()
    print("Available microphones:")
    print("-" * 40)
    
    for i in range(audio.get_device_count()):
        device_info = audio.get_device_info_by_index(i)
        if device_info['maxInputChannels'] > 0:
            print(f"{i}: {device_info['name']}")
    
    audio.terminate()

def main():
    """Main function"""
    parser = argparse.ArgumentParser(description='Real-time Speech-to-Text using Whisper')
    parser.add_argument('--model', '-m', default='medium',
                       help='Whisper model to use (tiny, base, small, medium, large, etc.)')
    parser.add_argument('--chunk', '-c', type=float, default=3.0,
                       help='Audio chunk duration in seconds (default: 3.0)')
    parser.add_argument('--overlap', '-o', type=float, default=0.5,
                       help='Overlap between chunks in seconds (default: 0.5)')
    parser.add_argument('--list-mics', action='store_true',
                       help='List available microphones')
    
    args = parser.parse_args()
    
    if args.list_mics:
        list_microphones()
        return
    
    # Available models
    available_models = [
        'tiny.en', 'tiny', 'base.en', 'base', 'small.en', 'small', 
        'medium.en', 'medium', 'large-v1', 'large-v2', 'large-v3', 
        'large', 'large-v3-turbo', 'turbo'
    ]
    
    if args.model not in available_models:
        print(f"Error: Model '{args.model}' not found.")
        print(f"Available models: {', '.join(available_models)}")
        return
    
    # Create transcriber
    transcriber = RealTimeTranscriber(
        model_name=args.model,
        chunk_duration=args.chunk,
        overlap=args.overlap
    )
    
    try:
        # Start recording
        transcriber.start_recording()
        
        # Keep running until user stops
        while True:
            time.sleep(1)
            
    except KeyboardInterrupt:
        transcriber.stop_recording()
    except Exception as e:
        print(f"Error: {e}")
        transcriber.stop_recording()

if __name__ == "__main__":
    import sys
    if '--list-mics' in sys.argv:
        list_microphones()
    else:
        main()