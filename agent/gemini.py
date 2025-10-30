"""
Gemini AI Core - Main logic with async architecture.
Uses MCP for tool calling.
"""

import asyncio
from typing import Optional, Callable
from google import genai

from config import Config
from speech.wake_word import WakeWordDetector
from speech.tts import ElevenLabsTTS
from tools import ScreenCapture
from utils.logger import Logger
from mcp import format_tools_for_gemini, init_executor, initialize as mcp_initialize, execute_tool, cleanup as mcp_cleanup


class GeminiCore:
    """
    Main Gemini AI core with async architecture.
    Handles wake word -> listen -> think -> act -> speak flow.
    """

    def __init__(self, gemini_api_key: str, wake_word: str = "jarvis"):
        """
        Initialize Gemini core.

        Args:
            gemini_api_key: Google Gemini API key
            wake_word: "jarvis" or "sarah"
        """
        self.is_running = False
        self.wake_word = wake_word

        # Continuous conversation mode
        self.continuous_mode = False
        self.conversation_history = []

        # Initialize components
        Logger.info("Core", f"Initializing {wake_word.capitalize()}...")

        # Gemini client
        self.client = genai.Client(api_key=gemini_api_key)

        # Wake word detector
        self.wake_detector = WakeWordDetector(wake_word=wake_word)

        # TTS manager (ElevenLabs WebSocket Streaming - exact copy from ada.py)
        self.tts = ElevenLabsTTS(
            api_key=Config.ELEVENLABS_API_KEY,
            voice_id="UgBBYS2sOqTuMpoF3BR0"
        )

        # Screen capture
        self.screen_capture = ScreenCapture()

        # Initialize MCP tool executor
        Logger.info("Core", "Initializing MCP tool executor...")
        init_executor(self.client, self.screen_capture)

        # Gemini configuration with tools
        self.config = self._create_gemini_config()

        # Callbacks for GUI
        self.on_listening = None
        self.on_thinking = None
        self.on_speaking_start = None
        self.on_speaking_end = None
        self.on_idle = None

        Logger.info("Core", f"{wake_word.capitalize()} initialized!")

    def _create_gemini_config(self) -> dict:
        """Create Gemini API configuration with tools (typed config) and keep legacy return keys."""
        from google.genai import types

        # Load comprehensive system prompt from context.txt
        try:
            import os
            context_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'config', 'context.txt')
            with open(context_path, 'r', encoding='utf-8') as f:
                sys_instr = f.read()
        except Exception as e:
            Logger.error("Core", f"Failed to load context.txt: {e}. Using fallback.")
            sys_instr = f"""You are {self.wake_word.capitalize()}, an advanced AI voice assistant with vision and computer control.
Keep responses SHORT (1-3 sentences) for voice. Use tools intelligently. You can see the screen via screenshots."""
       
        # Get MCP tool schemas and build typed Tool
        tool_decls = format_tools_for_gemini()  # list[FunctionDeclaration]
        from google.genai import types
        tools = [types.Tool(function_declarations=tool_decls)]

        # Save a typed config for generate_content
        self._g_config = types.GenerateContentConfig(
            system_instruction=sys_instr,
            tools=tools,
            response_modalities=["TEXT"],
        )

        # Also return legacy dict so existing references to self.config still work
        return {
            "system_instruction": sys_instr,
            "tools": tools,  # keep a compatible object
            "response_modalities": ["TEXT"],
        }


    async def _continuous_listening_loop(self):
        """Continuous listening loop - keeps listening until 'terminate' is heard."""
        while self.continuous_mode and self.is_running:
            try:
                # Show listening state
                if self.on_listening:
                    await self.on_listening()

                # Record and transcribe
                user_text = await self._record_and_transcribe_command()

                if not user_text:
                    Logger.info("Core", "No command detected in continuous mode")
                    await asyncio.sleep(0.5)
                    continue

                # Check for terminate command
                if "terminate" in user_text.lower().strip():
                    Logger.info("Core", "Terminate command detected")
                    self.continuous_mode = False
                    self.conversation_history = []

                    # Speak confirmation and wait for it to finish
                    await self.tts.speak(
                        "Continuous mode deactivated. Goodbye.",
                        on_start=self.on_speaking_start,
                        on_end=self.on_speaking_end
                    )

                    # Small delay to let the speech finish and GUI animation play
                    await asyncio.sleep(0.5)

                    if self.on_idle:
                        await self.on_idle()
                    break

                # Process the interaction with conversation history
                await self._process_interaction(user_text, use_history=True)

                # Small delay before listening again to ensure TTS completes
                await asyncio.sleep(0.3)

            except Exception as e:
                Logger.error("Core", f"Error in continuous loop: {e}")
                import traceback
                traceback.print_exc()
                await asyncio.sleep(1)

    async def _process_interaction(self, user_text: str, use_history: bool = False):
        """Process user command with Gemini (typed contents; no Part.from_* helpers)."""
        from google.genai import types
        import base64

        try:
            if self.on_thinking:
                await self.on_thinking()

            Logger.info("Core", f"Sending to Gemini: {user_text}")

            # ALWAYS capture screen - Jarvis needs to see what you see!
            Logger.info("Core", "Capturing screen for context...")
            screenshot_result = await self.screen_capture.capture_screen()

            # Use conversation history in continuous mode
            if use_history and self.conversation_history:
                contents = list(self.conversation_history)
            else:
                contents = []

            # Add new user message WITH screenshot
            user_parts = [types.Part(text=user_text)]

            # Add screenshot as inline data
            if screenshot_result:
                screenshot_image, _ = screenshot_result

                # Convert PIL Image to bytes
                import io
                image_io = io.BytesIO()
                screenshot_image.save(image_io, format="JPEG", quality=85)
                image_bytes = image_io.getvalue()

                user_parts.append(
                    types.Part(
                        inline_data=types.Blob(
                            mime_type="image/jpeg",
                            data=base64.b64encode(image_bytes).decode('utf-8')
                        )
                    )
                )
                Logger.info("Core", "Screenshot attached to query")

            contents.append(
                types.Content(role="user", parts=user_parts)
            )

            def _call():
                return self.client.models.generate_content(
                    model=Config.MODEL,
                    contents=contents,
                    config=self._g_config,
                )

            # Retry logic for API failures
            max_retries = 3
            retry_delay = 2  # seconds
            response = None

            for attempt in range(max_retries):
                try:
                    response = await asyncio.to_thread(_call)
                    break  # Success!
                except Exception as e:
                    error_msg = str(e)
                    if "503" in error_msg or "overloaded" in error_msg.lower():
                        if attempt < max_retries - 1:
                            Logger.info("Core", f"API overloaded, retrying in {retry_delay}s... (attempt {attempt + 1}/{max_retries})")
                            await asyncio.sleep(retry_delay)
                            retry_delay *= 2  # Exponential backoff
                        else:
                            Logger.error("Core", "API still overloaded after retries")
                            raise
                    else:
                        # Other errors, don't retry
                        raise

            max_iterations = 5
            for _ in range(max_iterations):
                function_calls = []
                if getattr(response, "candidates", None):
                    model_content = response.candidates[0].content
                    if getattr(model_content, "parts", None):
                        for part in model_content.parts:
                            fc = getattr(part, "function_call", None)
                            if fc:
                                function_calls.append(fc)

                if not function_calls:
                    break

                Logger.info("Core", "Gemini requested tool execution")

                # Execute with MCP
                function_responses = await self._handle_tool_calls(function_calls)

                # 1) Append the full model content turn
                contents.append(response.candidates[0].content)

                # 2) Build function_response parts via constructors (no from_function_response)
                fr_parts = []
                for fr in function_responses:
                    fr_obj = types.FunctionResponse(
                        name=fr["name"],
                        response=fr["response"],
                    )
                    fr_parts.append(types.Part(function_response=fr_obj))

                # 3) Add as a new user turn, then continue
                contents.append(types.Content(role="user", parts=fr_parts))

                # Retry logic for tool result processing (same as initial call)
                for attempt in range(max_retries):
                    try:
                        response = await asyncio.to_thread(_call)
                        break  # Success!
                    except Exception as e:
                        error_msg = str(e)
                        if "503" in error_msg or "overloaded" in error_msg.lower():
                            if attempt < max_retries - 1:
                                # Use exponential backoff (2s, 4s, 8s)
                                current_delay = 2 * (2 ** attempt)
                                Logger.info("Core", f"API overloaded during tool processing, retrying in {current_delay}s... (attempt {attempt + 1}/{max_retries})")
                                await asyncio.sleep(current_delay)
                            else:
                                Logger.error("Core", "API still overloaded after retries in tool loop")
                                raise
                        else:
                            # Other errors, don't retry
                            raise

            # Extract/sanitize text
            response_text = getattr(response, "text", "") or ""
            import re
            response_text = re.sub(r"```.*?```", "", response_text, flags=re.DOTALL).strip()

            Logger.info("Core", f"Gemini response: {response_text[:100] if response_text else 'empty'}...")

            # Add assistant's response to conversation history
            if use_history and response.candidates:
                contents.append(response.candidates[0].content)
                # Keep last 10 turns to avoid context length issues
                if len(contents) > 20:
                    contents = contents[-20:]
                self.conversation_history = contents

            if response_text and len(response_text) > 5:
                Logger.info("Core", "Speaking response...")

                # Wrap TTS in try-finally to ensure callbacks always fire
                speech_successful = False
                try:
                    await self.tts.speak(
                        response_text,
                        on_start=self.on_speaking_start,
                        on_end=self.on_speaking_end,
                    )
                    speech_successful = True
                    Logger.info("Core", "Finished speaking")
                except Exception as tts_error:
                    Logger.error("Core", f"TTS error: {tts_error}")
                    # Ensure end callback fires even on error
                    if self.on_speaking_end:
                        await self.on_speaking_end()

                # Check if Jarvis asked a question - if so, continue listening for answer
                # IMPORTANT: Remove "not use_history" condition to enable multi-turn conversations
                if speech_successful and response_text.strip().endswith('?'):
                    Logger.info("Core", "Question detected - continuing listening for answer")

                    try:
                        # Start listening for response
                        if self.on_listening:
                            await self.on_listening()

                        # Record user's answer
                        answer_text = await self._record_and_transcribe_command()

                        if answer_text:
                            Logger.info("Core", f"Got answer: {answer_text}")

                            # Check if user said "no" or wants to end conversation
                            answer_lower = answer_text.lower().strip()
                            decline_keywords = ["no", "nope", "nothing", "that's all", "thats all", "i'm good", "im good", "all good", "no thanks", "no thank you"]

                            if any(keyword in answer_lower for keyword in decline_keywords) and len(answer_lower) < 15:
                                Logger.info("Core", "User declined further assistance, ending conversation")
                                # Acknowledge and end gracefully
                                await self.tts.speak(
                                    "Alright! Let me know if you need anything.",
                                    on_start=self.on_speaking_start,
                                    on_end=self.on_speaking_end
                                )
                                # Clear history and go idle
                                self.conversation_history = []
                                if self.on_idle:
                                    await self.on_idle()
                                return

                            # Process answer with conversation history
                            # Keep context from previous conversation
                            if not self.conversation_history:
                                self.conversation_history = contents
                            await self._process_interaction(answer_text, use_history=True)
                            return  # Don't go idle here, let the recursive call handle it
                        else:
                            Logger.info("Core", "No answer detected, ending conversation")
                            # Clear history and go idle
                            self.conversation_history = []
                            if self.on_idle:
                                await self.on_idle()
                    except Exception as conv_error:
                        Logger.error("Core", f"Conversation error: {conv_error}")
                        import traceback
                        traceback.print_exc()
                        # Clear history and reset on error
                        self.conversation_history = []
                        if self.on_idle:
                            await self.on_idle()
                    return  # Exit early, don't run the idle logic at the end

            else:
                Logger.info("Core", "No speakable response")
                # Ensure callbacks fire even with no speech
                if self.on_speaking_start:
                    await self.on_speaking_start()
                if self.on_speaking_end:
                    await self.on_speaking_end()

            # Only go idle if not in continuous mode and didn't return early
            if not use_history and self.on_idle:
                await self.on_idle()

        except Exception as e:
            Logger.error("Core", f"Interaction error: {e}")
            import traceback
            traceback.print_exc()

            # CRITICAL: Always ensure we go idle on error to prevent stuck state
            try:
                if self.on_speaking_end:
                    await self.on_speaking_end()
            except:
                pass

            try:
                if not use_history and self.on_idle:
                    await self.on_idle()
            except:
                pass



    async def start(self):
        """Start Gemini core loop."""
        self.is_running = True
        Logger.info("Core", "Starting Gemini...")

        try:
            # Initialize MCP (browser, etc.)
            Logger.info("Core", "Initializing MCP...")
            await mcp_initialize()
            Logger.info("Core", "MCP ready!")

            # Start wake word detection
            await self.wake_detector.start_detection(self._on_wake_detected)

        except Exception as e:
            Logger.error("Core", f"Error: {e}")
            import traceback
            traceback.print_exc()
        finally:
            self.stop()

    async def _on_wake_detected(self, command_text: str = None):
        """
        Handle wake word detection.

        Args:
            command_text: Optional command text captured during wake word detection
        """
        Logger.info("Core", f"Wake word detected: {self.wake_word}")

        if self.on_listening:
            await self.on_listening()

        # If command was captured with wake word, use it directly
        if command_text:
            Logger.info("Core", f"Using command from wake word: {command_text}")
            user_text = command_text
        else:
            # Record user's command
            user_text = await self._record_and_transcribe_command()

        if not user_text:
            Logger.info("Core", "No command detected")
            if self.on_idle:
                await self.on_idle()
            return

        # Check for special commands
        user_text_lower = user_text.lower().strip()

        # Check for "listen up" command
        if "listen up" in user_text_lower or "listen" in user_text_lower:
            Logger.info("Core", "Continuous mode ACTIVATED")
            self.continuous_mode = True
            self.conversation_history = []

            # Speak confirmation
            if self.on_speaking_start:
                await self.on_speaking_start()
            await self.tts.speak(
                "I'm listening.",
                on_start=self.on_speaking_start,
                on_end=self.on_speaking_end
            )

            # Start continuous listening loop
            await self._continuous_listening_loop()
            return

        # Check for "terminate" command
        if "terminate" in user_text_lower:
            Logger.info("Core", "Continuous mode DEACTIVATED")
            self.continuous_mode = False
            self.conversation_history = []

            # Speak confirmation
            if self.on_speaking_start:
                await self.on_speaking_start()
            await self.tts.speak(
                "Continuous mode deactivated. Goodbye.",
                on_start=self.on_speaking_start,
                on_end=self.on_speaking_end
            )

            if self.on_idle:
                await self.on_idle()
            return

        # Process the command normally
        await self._process_interaction(user_text)

    async def _record_and_transcribe_command(self) -> str:
        """Record audio after wake word and transcribe it."""
        try:
            import pyaudio
            import wave
            import tempfile
            import struct

            Logger.info("Core", "Recording command...")

            # Audio settings
            FORMAT = pyaudio.paInt16
            CHANNELS = 1
            RATE = 16000
            CHUNK = 1024
            SILENCE_THRESHOLD = 300
            SILENCE_DURATION = 2.0
            MAX_DURATION = 10
            MIN_AUDIO_LENGTH = 0.5

            pya = pyaudio.PyAudio()
            stream = pya.open(
                format=FORMAT,
                channels=CHANNELS,
                rate=RATE,
                input=True,
                frames_per_buffer=CHUNK
            )

            frames = []
            silent_chunks = 0
            max_silent_chunks = int(SILENCE_DURATION * RATE / CHUNK)
            max_chunks = int(MAX_DURATION * RATE / CHUNK)
            min_chunks = int(MIN_AUDIO_LENGTH * RATE / CHUNK)

            # Small delay to let user start speaking
            await asyncio.sleep(0.3)

            # Record until silence or max duration
            for i in range(max_chunks):
                data = await asyncio.to_thread(stream.read, CHUNK, exception_on_overflow=False)
                frames.append(data)

                # Check energy
                pcm = struct.unpack_from("h" * CHUNK, data)
                energy = sum(abs(x) for x in pcm) / CHUNK

                # Only check for silence after minimum recording time
                if i >= min_chunks:
                    if energy < SILENCE_THRESHOLD:
                        silent_chunks += 1
                        if silent_chunks > max_silent_chunks:
                            break
                    else:
                        silent_chunks = 0

            Logger.info("Core", "Recording complete, transcribing...")

            # Save to temp file
            temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.wav')
            temp_path = temp_file.name
            temp_file.close()

            sample_width = pya.get_sample_size(FORMAT)

            stream.stop_stream()
            stream.close()
            pya.terminate()

            with wave.open(temp_path, 'wb') as wf:
                wf.setnchannels(CHANNELS)
                wf.setsampwidth(sample_width)
                wf.setframerate(RATE)
                wf.writeframes(b''.join(frames))

            # Transcribe using Whisper
            segments, _ = await asyncio.to_thread(
                self.wake_detector.model.transcribe,
                temp_path,
                language="en",
                beam_size=1
            )
            text = " ".join([segment.text for segment in segments]).strip()

            # Clean up
            import os
            os.unlink(temp_path)

            # Validate transcription
            if not text or len(text) < 3:
                Logger.info("Core", "Transcription too short or empty")
                return ""

            Logger.info("Core", f"Transcribed: {text}")
            return text

        except Exception as e:
            Logger.error("Core", f"Recording error: {e}")
            return ""

    async def _handle_tool_calls(self, function_calls):
        """Handle function/tool calls from Gemini using MCP."""
        function_responses = []

        for fc in function_calls:
            tool_name = fc.name
            args = dict(fc.args) if hasattr(fc.args, '__iter__') else {}

            Logger.info("Core", f"Tool call: {tool_name}")

            try:
                # Execute tool via MCP
                result = await execute_tool(tool_name, args)
            except Exception as e:
                import traceback
                traceback.print_exc()
                result = {"success": False, "error": str(e)}

            function_responses.append({"name": tool_name, "response": result})

        return function_responses

    def stop(self):
        """Stop Gemini core."""
        self.is_running = False
        self.wake_detector.stop_detection()

        # Cleanup MCP
        try:
            import asyncio
            loop = asyncio.get_event_loop()
            if loop.is_running():
                asyncio.create_task(mcp_cleanup())
            else:
                asyncio.run(mcp_cleanup())
        except Exception as e:
            Logger.error("Core", f"Cleanup error: {e}")

        Logger.info("Core", "Gemini stopped")

    def set_continuous_mode(self, enabled: bool):
        """Enable/disable continuous listening mode."""
        self.wake_detector.set_continuous_mode(enabled)
