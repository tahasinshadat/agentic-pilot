# JARVIS - Advanced AI Assistant

An advanced voice-activated AI assistant with vision capabilities, inspired by both Iron Man's JARVIS and modern AI technology.

## Features

- 🎤 **Wake Word Detection** - Activate with "Hey Jarvis" or "Hey Sarah"
- 🗣️ **Natural Voice Interaction** - Powered by Gemini Live API and **ChatTTS (open-source, local TTS)**
- 👁️ **Vision Capabilities** - Can see and analyze your screen
- 🛠️ **Powerful Tools** - File operations, app launching, web browsing, code execution
- 🎨 **Beautiful GUI** - Floating window with 3D animated sphere (appears bottom-right)
- ⚡ **Async Architecture** - Fast and responsive
- 🆓 **100% Open Source TTS** - No API costs for text-to-speech!

## Setup

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

**Important Notes:**
- **PyAudio** can be tricky on some systems:
  - **Windows**: Download wheel from [here](https://www.lfd.uci.edu/~gohlke/pythonlibs/#pyaudio)
  - **Mac**: `brew install portaudio && pip install pyaudio`
  - **Linux**: `sudo apt-get install portaudio19-dev && pip install pyaudio`

- **ChatTTS** will download models on first run (~200MB). This is normal!

- **PyTorch** is required for ChatTTS. If you have a GPU:
  ```bash
  pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118
  ```

### 2. Configure API Key

Edit the `.env` file in the root directory:

```env
GEMINI_API_KEY=your_gemini_api_key_here
```

Get your Gemini API key:
- Gemini: [Google AI Studio](https://aistudio.google.com/app/apikey) - **FREE tier available!**

**Note**: No need for ElevenLabs or any other API keys - ChatTTS runs locally!

### 3. Run Jarvis

```bash
python main.py
```

## Usage

### Voice Commands

- **Activate**: Say "Hey Jarvis" (or "Hey Sarah")
- **Ask Questions**: "What's the weather?" (uses Google Search)
- **Screen Help**: "Help me with this LeetCode problem" (takes screenshot + vision)
- **File Operations**: "Create a file called notes.txt"
- **Launch Apps**: "Open Chrome"
- **Browse Web**: "Go to youtube.com"
- **Code Execution**: "Calculate 15 * 23"

### Continuous Mode

- **Enable**: "Hey Jarvis, Listen up" - Jarvis will respond without wake word
- **Disable**: "Hey Jarvis, stop listening" - Back to wake word mode

### GUI

A small floating window appears in the bottom-right corner when Jarvis is active:
- **Blue sphere** - Idle/Listening
- **Pulsing sphere** - Speaking
- Auto-hides when idle

## Project Structure

```
personal-assistant/
├── main.py              # Entry point
├── requirements.txt     # Dependencies
├── .env                 # API keys
├── README.md            # This file
├── CHATTTS_MIGRATION.md # ChatTTS migration guide
├── config/              # Configuration folder
│   ├── config.py        # Technical configuration
│   └── settings.json    # User preferences
├── core/
│   └── jarvis_core.py  # Main AI logic
├── gui/
│   ├── floating_window.py  # Floating GUI
│   └── animation.py        # 3D sphere animation
├── speech/
│   ├── wake_word.py    # Wake word detection
│   └── tts.py          # Text-to-speech
├── vision/
│   ├── screen_capture.py   # Screenshots
│   └── video_feed.py       # Camera/screen feed
├── tools/
│   ├── file_operations.py  # File system
│   ├── app_control.py      # App launching
│   └── web_tools.py        # Web browsing
├── utils/
│   └── logger.py       # Logging
└── ada/                 # Reference project (ADA)
```

## Customization

### Change Wake Word

Edit `config/config.py`:

```python
WAKE_WORD = "sarah"  # Options: "jarvis", "sarah"
```

### Customize ChatTTS

ChatTTS generates natural-sounding speech automatically. You can customize generation in `config/config.py`:

```python
TTS_COMPILE = True  # Enable for faster inference (requires compatible GPU)
```

For advanced customization, edit `speech/tts.py` to modify voice characteristics.

## Troubleshooting

### No Wake Word Detection

- Check microphone permissions in system settings
- Verify microphone is set as default device
- Try increasing `ENERGY_THRESHOLD` in config/config.py

### GUI Not Showing

- Make sure PySide6 is installed: `pip install PySide6`
- Check if window is hidden behind other windows

### API Errors

- Verify Gemini API key in `.env` file
- Check Gemini API quotas (free tier has limits)
- Ensure you have internet connection for Gemini

### ChatTTS Issues

- **First run is slow**: ChatTTS downloads models (~200MB) on first use
- **Voice quality**: ChatTTS generates natural speech but may vary. It's learning-based.
- **GPU acceleration**: Set `TTS_COMPILE = True` in config/config.py if you have a CUDA GPU
- **Memory usage**: ChatTTS needs ~1-2GB RAM. Close other apps if needed.

## Credits

- Inspired by [ADA](https://github.com/example) project
- Built with Google Gemini and **ChatTTS (open-source)**
- Uses faster-whisper for wake word detection
- ChatTTS: [https://github.com/2noise/ChatTTS](https://github.com/2noise/ChatTTS)

## Why ChatTTS?

- ✅ **100% Free** - No API costs
- ✅ **Privacy** - Runs locally, your data stays on your machine
- ✅ **No Rate Limits** - Use as much as you want
- ✅ **Natural Speech** - High-quality, expressive TTS
- ✅ **Open Source** - Community-driven, constantly improving

## License

MIT License