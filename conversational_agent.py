import threading
import time
import queue

# Import Groq chat function
def chat_with_groq(message, conversation=None):
    import groq_chatbot
    return groq_chatbot.chat_with_groq(message, conversation)

# Import Deepgram TTS function
def text_to_speech(text, output_file='output.wav', play_audio=True):
    import deepgram_tts
    # Truncate text to 1000 chars for TTS
    if len(text) > 1000:
        print("[TTS] Response too long, truncating for speech synthesis.")
        text = text[:1000] + '...'
    return deepgram_tts.text_to_speech(text, output_file, play_audio)

# Import Whisper STT class and mic listing
from main import RealTimeTranscriber, list_microphones

# Conversation memory
conversation = []

def select_microphone():
    print("\nAvailable microphones:")
    list_microphones()
    try:
        device_index = int(input("Enter the device index of the microphone to use (or press Enter for default): ") or -1)
    except ValueError:
        device_index = -1
    return device_index

# Voice-to-Voice mode
def voice_to_voice():
    print("[Start] Voice-to-Voice Mode. Speak to the AI. Say 'exit' or press Ctrl+C to stop.")
    user_queue = queue.Queue()
    recording_flag = threading.Event()
    session_active = True
    device_index = select_microphone()

    def on_transcription(text):
        if text and len(text.strip()) > 1:
            print(f"[Transcribed] {text.strip()}")
            user_queue.put(text.strip())
            print("[Ready for next input]")

    def recording_indicator():
        while not recording_flag.is_set():
            print("[Recording...]", end='\r')
            time.sleep(0.5)
        print(" " * 20, end='\r')  # Clear the line

    try:
        while session_active:
            print("[Start speaking]")
            recording_flag.clear()
            indicator_thread = threading.Thread(target=recording_indicator)
            indicator_thread.start()
            # Re-initialize transcriber for each turn to avoid stream issues
            transcriber = RealTimeTranscriber(model_name="tiny", chunk_duration=3, overlap=0.5)
            # Set device index if specified
            if device_index != -1:
                transcriber.device_index = device_index
            # Patch the _transcribe_chunk method to push text to queue
            def patched_transcribe_chunk(audio_data):
                try:
                    result = transcriber.model.transcribe(audio_data, fp16=False)
                    text = result['text'].strip()
                    if text and len(text) > 1:
                        timestamp = time.strftime("%H:%M:%S")
                        print(f"[You {timestamp}] {text}")
                        on_transcription(text)
                except Exception as e:
                    print(f"Error transcribing chunk: {e}")
            transcriber._transcribe_chunk = patched_transcribe_chunk
            try:
                transcriber.start_recording()
                user_text = user_queue.get()  # Wait for transcription
                recording_flag.set()
                transcriber.stop_recording()
                indicator_thread.join()
                if user_text.lower() in ("exit", "quit"):
                    session_active = False
                    break
                reply, _ = chat_with_groq(user_text, conversation)
                if reply:
                    print(f"[AI] {reply}")
                    text_to_speech(reply)
            except (OSError, KeyboardInterrupt) as e:
                recording_flag.set()
                indicator_thread.join()
                if isinstance(e, KeyboardInterrupt):
                    print("[!] Voice-to-Voice session ended.")
                    break
                else:
                    print(f"[!] Error: {e}")
                    print("[!] Exiting voice-to-voice mode due to error.")
                    break
    except KeyboardInterrupt:
        recording_flag.set()
        print("[!] Voice-to-Voice session ended.")

# Text-to-Voice mode
def text_to_voice():
    print("[Text-to-Voice Mode] Type your message. Type 'exit' to quit.")
    while True:
        user_input = input("You: ")
        if user_input.lower() in ("exit", "quit"): break
        start_groq = time.time()
        reply, _ = chat_with_groq(user_input, conversation)
        end_groq = time.time()
        if reply:
            print(f"[AI] {reply}")
            start_tts = time.time()
            text_to_speech(reply)
            end_tts = time.time()
            print(f"[Timing] Groq response: {end_groq - start_groq:.2f}s, TTS synthesis: {end_tts - start_tts:.2f}s")

# Main menu
if __name__ == "__main__":
    print("Conversational AI Agent\n======================")
    print("1. Voice-to-Voice Conversation (speak to the AI)")
    print("2. Text-to-Voice Mode (type and hear responses)")
    mode = input("Select mode (1 or 2): ").strip()
    if mode == "1":
        voice_to_voice()
    elif mode == "2":
        text_to_voice()
    else:
        print("Invalid selection. Exiting.") 