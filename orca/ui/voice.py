"""
Voice interface for Orca OS (offline speech recognition and TTS).
"""

import logging
from typing import Optional, Callable
import asyncio

logger = logging.getLogger(__name__)

try:
    import speech_recognition as sr
    import pyttsx3
    VOICE_AVAILABLE = True
except ImportError:
    VOICE_AVAILABLE = False
    logger.warning("Voice libraries not available. Install: pip install SpeechRecognition pyttsx3")


class VoiceInterface:
    """Offline voice recognition and text-to-speech."""
    
    def __init__(self):
        """Initialize voice interface."""
        self.available = VOICE_AVAILABLE
        self.recognizer = None
        self.tts_engine = None
        
        if self.available:
            try:
                self.recognizer = sr.Recognizer()
                self.tts_engine = pyttsx3.init()
                self._configure_tts()
            except Exception as e:
                logger.error(f"Failed to initialize voice: {e}")
                self.available = False
    
    def _configure_tts(self):
        """Configure text-to-speech engine."""
        if self.tts_engine:
            # Set speech rate
            self.tts_engine.setProperty('rate', 150)
            # Set volume
            self.tts_engine.setProperty('volume', 0.8)
    
    def listen(self, timeout: int = 5) -> Optional[str]:
        """Listen for voice input (offline)."""
        if not self.available or not self.recognizer:
            return None
        
        try:
            with sr.Microphone() as source:
                logger.info("Listening...")
                # Adjust for ambient noise
                self.recognizer.adjust_for_ambient_noise(source, duration=0.5)
                # Listen for audio
                audio = self.recognizer.listen(source, timeout=timeout)
            
            # Use offline recognition (pocketsphinx)
            try:
                text = self.recognizer.recognize_sphinx(audio)
                logger.info(f"Recognized: {text}")
                return text
            except sr.UnknownValueError:
                logger.warning("Could not understand audio")
                return None
            except sr.RequestError as e:
                logger.error(f"Recognition error: {e}")
                return None
                
        except Exception as e:
            logger.error(f"Voice input error: {e}")
            return None
    
    async def listen_async(self, timeout: int = 5) -> Optional[str]:
        """Async version of listen."""
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, self.listen, timeout)
    
    def speak(self, text: str):
        """Convert text to speech."""
        if not self.available or not self.tts_engine:
            logger.warning("TTS not available")
            return
        
        try:
            self.tts_engine.say(text)
            self.tts_engine.runAndWait()
        except Exception as e:
            logger.error(f"TTS error: {e}")
    
    async def speak_async(self, text: str):
        """Async version of speak."""
        loop = asyncio.get_event_loop()
        await loop.run_in_executor(None, self.speak, text)
    
    def set_voice_properties(self, rate: Optional[int] = None, volume: Optional[float] = None):
        """Set TTS voice properties."""
        if not self.tts_engine:
            return
        
        if rate is not None:
            self.tts_engine.setProperty('rate', rate)
        if volume is not None:
            self.tts_engine.setProperty('volume', max(0.0, min(1.0, volume)))

