
### 🎙️ Real-Time Conversational AI Agent (Voice & Text)

A Python-based AI assistant that supports **real-time voice-to-voice** and **text-to-voice** conversation using advanced AI models. This project integrates **Whisper (STT)**, **Groq LLM (Chat)**, and **Deepgram (TTS)** for a natural, interactive human-computer experience.

---

## 🚀 Features

✅ Dual-mode interaction:
- **Mode 1:** Speak to the AI and hear back (Voice-to-Voice)
- **Mode 2:** Type your input and hear the response (Text-to-Voice)

✅ Fast and real-time performance:
- ⏱️ STT latency: ~2 sec
- ⚡ Groq LLM response: ~1.5 sec
- 🔊 TTS synthesis: ~1 sec

✅ Modular design:
- Separate modules for STT, chat, and TTS
- Easy to extend and secure with `.env`

✅ CLI-based for fast prototyping (Web/GUI-ready)

---

## 🧠 Tech Stack

- **Language:** Python 3.9+
- **STT:** [OpenAI Whisper](https://github.com/openai/whisper)
- **Chat Model:** [Groq API](https://groq.com/)
- **TTS:** [Deepgram API](https://www.deepgram.com/)
- **Audio:** `pyaudio`, `numpy`, `queue`, `threading`
- **Security:** `python-dotenv` for API key handling

---

## 📁 Project Structure

```

conversational-ai-agent/
├── conversational\_agent.py       # Main interface script
├── groq\_chatbot.py               # Handles Groq API calls
├── deepgram\_tts.py               # Deepgram TTS wrapper
├── main.py                       # Whisper STT and mic handling
├── .env                          # API keys (not uploaded)
├── .env.example                  # Template for env vars
├── requirements.txt              # Install dependencies
└── README.md                     # You're here!

```

---

## 🔐 Environment Variables

Create a `.env` file:
```

GROQ\_API\_KEY=your\_groq\_key\_here
DEEPGRAM\_API\_KEY=your\_deepgram\_key\_here

````

Make sure `.env` is in `.gitignore`.

---

## 📦 Installation

1. Clone the repo:
```bash
git clone https://github.com/kalaiyarasi2/conversational-ai-agent.git
cd conversational-ai-agent
````

2. Create a virtual environment (recommended):

```bash
python -m venv venv
source venv/bin/activate   # or venv\Scripts\activate on Windows
```

3. Install dependencies:

```bash
pip install -r requirements.txt
```

4. Add your API keys to `.env`.

---

## 🧪 Run the Project

```bash
python conversational_agent.py
```

Then select:

* `1` for Voice-to-Voice
* `2` for Text-to-Voice

---

## 📊 Impact & Metrics

* 🎙️ Real-time speech chunk processing every **3 seconds**
* 🧠 LLM replies in under **1.5 seconds**
* 🔊 TTS voice response latency under **1 second**
* 🧾 Supports **1000+ character AI responses**
* 🧪 Successfully tested with **multiple microphones**

---

## 📌 Future Enhancements

* [ ] Web-based UI using Streamlit
* [ ] Speaker Identification / Diarization
* [ ] Context memory & summarization
* [ ] Raspberry Pi or edge device integration

---

## 👩‍💻 Author

**Kalaiyarasi G**
[GitHub Profile](https://github.com/kalaiyarasi2) | [Naukri](https://naukri.com) | [LinkedIn](https://linkedin.com/in/kalaiyarasi2)

---

## 📸 Demo (Optional)

Add demo video/screenshot to `assets/` and link them here:

![demo](assets/convo-demo.gif)

---

## 📃 License

This project is open-source and free to use under the [MIT License](LICENSE).

---

```

---

Would you like me to also:
- Generate `requirements.txt` from your code?
- Give the full code for `groq_chatbot.py` or `deepgram_tts.py`?
- Create a README badge header?

Let me know, and I’ll finalize everything for upload!
```
