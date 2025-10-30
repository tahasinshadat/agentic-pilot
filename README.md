# JARVIS - Advanced AI Assistant

An advanced voice-activated AI assistant with vision and autopilot capabilities, combining the best of conversational AI with powerful computer control. Inspired by Iron Man's JARVIS and enhanced with Open-Interface's autonomous UI automation.

## Features

### Core Capabilities
- **Wake Word Detection** - Activate with "Hey Jarvis" or "Hey Sarah"
- **Natural Voice Interaction** - Powered by Gemini 2.0 Flash and **ElevenLabs TTS**
- **Vision Capabilities** - Can see and analyze your screen in real-time
- **Autopilot Mode** - Autonomous computer control with PyAutoGUI (inspired by Open-Interface)
- **50+ Specialized Tools** - File operations, app launching, web browsing, code execution, screen interaction
- **Beautiful GUI** - Floating window with 3D animated sphere (appears bottom-right)
- **Async Architecture** - Fast, responsive, and non-blocking

### What Makes JARVIS Unique
- **Voice + Vision + Autopilot**: Combines conversational AI with autonomous UI control
- **Context-Aware**: Loads comprehensive system prompts from \`config/context.txt\` for intelligent behavior
- **Multi-Turn Conversations**: Maintains context across multiple interactions
- **Recursive Autopilot**: Uses screenshot feedback loops for precise task execution
- **Tool-Based Architecture**: Modular, extensible tool system (MCP-inspired)

## Setup

### 1. Install Dependencies

\`\`\`bash
pip install -r requirements.txt
\`\`\`

**Important Notes:**
- **PyAudio** can be tricky on some systems:
  - **Windows**: Download wheel from [here](https://www.lfd.uci.edu/~gohlke/pythonlibs/#pyaudio)
  - **Mac**: \`brew install portaudio && pip install pyaudio\`
  - **Linux**: \`sudo apt-get install portaudio19-dev && pip install pyaudio\`

- **Playwright** (for browser automation):
  \`\`\`bash
  playwright install chromium
  \`\`\`

### 2. Configure API Keys

Edit the \`.env\` file in the root directory:

\`\`\`env
GEMINI_API_KEY=your_gemini_api_key_here
ELEVENLABS_API_KEY=your_elevenlabs_api_key_here
\`\`\`

Get your API keys:
- **Gemini**: [Google AI Studio](https://aistudio.google.com/app/apikey) - **FREE tier available!**
- **ElevenLabs**: [ElevenLabs](https://elevenlabs.io/) - For TTS (has free tier)

### 3. Run JARVIS

\`\`\`bash
python main.py
\`\`\`

## Usage

### Voice Commands

#### Basic Commands
- **Activate**: Say "Hey Jarvis" (or "Hey Sarah")
- **Ask Questions**: "What's the weather?" (uses Google Search)
- **Screen Help**: "Help me with this LeetCode problem" (takes screenshot + vision)
- **File Operations**: "Create a file called notes.txt with my shopping list"
- **Launch Apps**: "Open Chrome"
- **Browse Web**: "Go to youtube.com" or "Search for Python tutorials"

#### Advanced Commands (Autopilot)
- **Complex UI Tasks**: "Fill out this form on screen"
- **Multi-Step Workflows**: "Open Notepad and create a shopping list"
- **Navigation**: "Navigate to settings and enable dark mode"

The autopilot automatically:
1. Captures screenshots to see current state
2. Plans keyboard/mouse actions
3. Executes them with PyAutoGUI
4. Verifies completion with new screenshots
5. Repeats until task is done

### Continuous Mode

- **Enable**: "Hey Jarvis, Listen up" - JARVIS will respond without wake word
- **Disable**: Say "terminate" or "that's all"

### GUI

A small floating window appears in the bottom-right corner:
- **Blue sphere** - Idle/Listening
- **Yellow sphere** - Thinking
- **Pulsing sphere** - Speaking
- Auto-hides after 2 seconds of idle

## Architecture

### Recent Improvements (Integration with Open-Interface)

#### What's New
1. **Autopilot Mode**: Full PyAutoGUI-based computer control for complex UI tasks
2. **Context System**: Comprehensive system prompt in \`config/context.txt\` (90+ lines)
3. **Security Fixes**: Removed all \`shell=True\` usage from subprocess calls
4. **Better Architecture**: Enhanced tool organization and execution flow
5. **Improved Documentation**: Clearer README with architecture diagrams

#### What Was Preserved
- All 50+ existing tools (no functionality lost)
- Voice input/output with wake word detection
- Floating GUI with 3D sphere animation
- Multi-turn conversations
- Screen capture and vision capabilities
- Browser automation with Playwright
- Continuous listening mode

### Project Structure

\`\`\`
agentic-pilot/
├── main.py                      # Entry point
├── .env                         # API keys
│
├── config/
│   ├── config.py               # Technical configuration
│   ├── context.txt             # Comprehensive system prompt
│   └── settings.json           # User preferences
│
├── agent/
│   └── gemini.py               # Core AI logic
│
├── mcp/                        # Model Context Protocol
│   ├── tool_schemas.py         # 50+ tool definitions
│   └── tool_execution.py       # Tool dispatcher
│
├── tools/                      # 50+ Tool Implementations
│   ├── autopilot.py            # PyAutoGUI autopilot
│   ├── click_on_screen.py      # AI-powered clicking
│   ├── smart_open.py           # Updated security concerns (no access to program & system files)
│   └── ... (50+ more tools)
│
├── speech/
│   ├── wake_word.py            # Wake word detection
│   └── tts.py                  # Text-to-speech
│
└── gui/
    ├── floating_window.py      # Floating window
    └── animation.py            # 3D sphere
\`\`\`

### Key Components

1. **GeminiCore** - Main orchestrator with context.txt loading
2. **Autopilot** - PyAutoGUI-based UI automation (NEW)
3. **Tool System** - 50+ modular tools
4. **Context System** - Comprehensive prompts (NEW)

## Customization

### Change Wake Word

Edit \`config/config.py\`:
\`\`\`python
WAKE_WORD = "sarah"  # Options: "jarvis", "sarah"
\`\`\`

### Customize System Prompt

Edit \`config/context.txt\` to modify JARVIS's behavior and tool usage patterns.

### Add New Tools

1. Create \`tools/my_tool.py\`
2. Add to \`tools/__init__.py\`
3. Add schema to \`mcp/tool_schemas.py\`
4. Add handler to \`mcp/tool_execution.py\`

## Troubleshooting

### No Wake Word Detection
- Check microphone permissions
- Verify default microphone device
- Try speaking louder/closer

### Autopilot Not Working
- Ensure PyAutoGUI is installed
- Check console for errors
- Verify screenshots are being captured

### API Errors
- Verify API keys in \`.env\`
- Check Gemini API quotas
- Ensure internet connection

## Credits
- **Powered by**: Gemini 2.0 Flash, ElevenLabs, faster-whisper, PyAutoGUI, Playwright


---
**Built with combining conversational AI with autonomous computer control**
