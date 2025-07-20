import requests
import os
from dotenv import load_dotenv
load_dotenv()
# Removed gTTS, pygame, tempfile, os as _os imports

# Set your API key
GROQ_API_KEY = os.getenv('GROQ_API_KEY')
GROQ_API_URL = 'https://api.groq.com/openai/v1/chat/completions'

HEADERS = {
    'Authorization': f'Bearer {GROQ_API_KEY}',
    'Content-Type': 'application/json',
}

def chat_with_groq(message, conversation=None):
    if conversation is None:
        conversation = []
    conversation.append({"role": "user", "content": message})
    data = {
        "model": "llama-3.1-8b-instant",
        "messages": conversation,
        "max_tokens": 512,
        "temperature": 0.7
    }
    try:
        response = requests.post(GROQ_API_URL, headers=HEADERS, json=data)
        response.raise_for_status()
        result = response.json()
        reply = result['choices'][0]['message']['content']
        conversation.append({"role": "assistant", "content": reply})
        return reply, conversation
    except requests.exceptions.HTTPError as e:
        print(f"Error communicating with Groq API: {e}")
        if e.response is not None:
            print(f"Response content: {e.response.text}")
        return None, conversation
    except Exception as e:
        print(f"Unexpected error: {e}")
        return None, conversation

def main():
    print("Welcome to the Groq Text Chatbot! Type 'exit' or 'quit' to stop.")
    if GROQ_API_KEY == 'YOUR_GROQ_API_KEY':
        print("[!] Please set your Groq API key in the script or as an environment variable.")
        return
    conversation = []
    try:
        while True:
            user_input = input("You: ")
            if not user_input.strip():
                continue
            if user_input.lower() in ('exit', 'quit'):
                print("Goodbye!")
                break
            reply, conversation = chat_with_groq(user_input, conversation)
            if reply:
                print(f"Groq: {reply}")
    except KeyboardInterrupt:
        print("\n[!] Exiting gracefully. Goodbye!")

if __name__ == "__main__":
    main() 