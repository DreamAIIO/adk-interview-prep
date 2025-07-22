"""
Voice Handler for audio input/output capabilities using Google's Gemini 2.0 Flash Exp.
Handles speech recognition, text-to-speech, and voice-enabled conversations.
"""
import logging
import asyncio
import io
import base64
from typing import Optional, AsyncGenerator, Dict, Any
import tempfile
import os

import speech_recognition as sr
from gtts import gTTS
import pygame
from pydub import AudioSegment
import google.generativeai as genai

from config import GOOGLE_API_KEY, VOICE_MODEL, AUDIO_SAMPLE_RATE, AUDIO_CHANNELS

logger = logging.getLogger(__name__)

class VoiceHandler:
    """Handles voice input and output for the interview assistant."""
    
    def __init__(self):
        """Initialize the voice handler."""
        genai.configure(api_key=GOOGLE_API_KEY)
        self.voice_model = genai.GenerativeModel(VOICE_MODEL)
        
        # Initialize speech recognition
        self.recognizer = sr.Recognizer()
        
        # Initialize pygame mixer for audio playback
        pygame.mixer.init(frequency=AUDIO_SAMPLE_RATE, channels=AUDIO_CHANNELS)
        
        # Voice settings
        self.voice_enabled = True
        self.tts_language = "en"
        self.speech_rate = 150  # words per minute
        
        logger.info("VoiceHandler initialized with Gemini 2.0 Flash Exp")
    
    def transcribe_audio(self, audio_data: bytes) -> Optional[str]:
        """
        Transcribe audio data to text using speech recognition.
        
        Args:
            audio_data: Raw audio bytes
            
        Returns:
            Transcribed text or None if transcription fails
        """
        try:
            # Convert bytes to AudioData
            with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as temp_file:
                temp_file.write(audio_data)
                temp_file_path = temp_file.name
            
            try:
                with sr.AudioFile(temp_file_path) as source:
                    audio = self.recognizer.record(source)
                
                # Use Google Speech Recognition
                text = self.recognizer.recognize_google(audio)
                logger.info(f"Transcribed audio: {text[:50]}...")
                return text
                
            finally:
                # Clean up temp file
                if os.path.exists(temp_file_path):
                    os.unlink(temp_file_path)
                    
        except sr.UnknownValueError:
            logger.warning("Could not understand audio")
            return None
        except sr.RequestError as e:
            logger.error(f"Speech recognition error: {str(e)}")
            return None
        except Exception as e:
            logger.error(f"Unexpected error in transcription: {str(e)}")
            return None
    
    def text_to_speech(self, text: str, language: str = "en") -> Optional[bytes]:
        """
        Convert text to speech audio.
        
        Args:
            text: Text to convert to speech
            language: Language code for TTS
            
        Returns:
            Audio bytes or None if conversion fails
        """
        try:
            if not text.strip():
                return None
            
            # Use gTTS for text-to-speech
            tts = gTTS(text=text, lang=language, slow=False)
            
            # Save to bytes buffer
            audio_buffer = io.BytesIO()
            tts.write_to_fp(audio_buffer)
            audio_buffer.seek(0)
            
            # Convert to proper format using pydub
            audio_segment = AudioSegment.from_mp3(audio_buffer)
            
            # Export as WAV bytes
            wav_buffer = io.BytesIO()
            audio_segment.export(wav_buffer, format="wav")
            wav_buffer.seek(0)
            
            return wav_buffer.getvalue()
            
        except Exception as e:
            logger.error(f"Error in text-to-speech: {str(e)}")
            return None
    
    def play_audio(self, audio_data: bytes) -> bool:
        """
        Play audio data using pygame.
        
        Args:
            audio_data: Audio bytes to play
            
        Returns:
            True if playback successful, False otherwise
        """
        try:
            if not audio_data:
                return False
            
            # Save audio to temporary file
            with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as temp_file:
                temp_file.write(audio_data)
                temp_file_path = temp_file.name
            
            try:
                # Load and play audio
                pygame.mixer.music.load(temp_file_path)
                pygame.mixer.music.play()
                
                # Wait for playback to complete
                while pygame.mixer.music.get_busy():
                    pygame.time.wait(100)
                
                return True
                
            finally:
                # Clean up temp file
                if os.path.exists(temp_file_path):
                    os.unlink(temp_file_path)
                    
        except Exception as e:
            logger.error(f"Error playing audio: {str(e)}")
            return False
    
    async def voice_conversation(
        self, 
        audio_input: bytes, 
        context: str = "",
        system_prompt: str = ""
    ) -> Dict[str, Any]:
        """
        Handle a complete voice conversation cycle using Gemini 2.0 Flash Exp.
        
        Args:
            audio_input: Input audio bytes
            context: Conversation context
            system_prompt: System prompt for the model
            
        Returns:
            Dictionary with transcribed text, response text, and response audio
        """
        try:
            # Step 1: Transcribe input audio
            transcribed_text = self.transcribe_audio(audio_input)
            if not transcribed_text:
                return {
                    "transcribed_text": None,
                    "response_text": "I couldn't understand your audio. Please try again.",
                    "response_audio": None,
                    "success": False
                }
            
            # Step 2: Generate response using Gemini 2.0 Flash Exp
            full_prompt = f"""
            {system_prompt}
            
            Context: {context}
            
            User said: {transcribed_text}
            
            Please provide a helpful, conversational response for interview preparation.
            Keep responses concise but informative.
            """
            
            response = await self._generate_voice_response(full_prompt)
            
            # Step 3: Convert response to speech
            response_audio = self.text_to_speech(response)
            
            return {
                "transcribed_text": transcribed_text,
                "response_text": response,
                "response_audio": response_audio,
                "success": True
            }
            
        except Exception as e:
            logger.error(f"Error in voice conversation: {str(e)}")
            return {
                "transcribed_text": None,
                "response_text": f"Error processing voice input: {str(e)}",
                "response_audio": None,
                "success": False
            }
    
    async def _generate_voice_response(self, prompt: str) -> str:
        """Generate response using Gemini 2.0 Flash Exp optimized for voice."""
        try:
            # Use async generation for better performance
            response = await asyncio.to_thread(
                self.voice_model.generate_content,
                prompt,
                generation_config={
                    "temperature": 0.7,
                    "max_output_tokens": 500,  # Shorter responses for voice
                    "top_p": 0.8,
                    "top_k": 40
                }
            )
            
            return response.text.strip()
            
        except Exception as e:
            logger.error(f"Error generating voice response: {str(e)}")
            return "I'm sorry, I encountered an error generating a response."
    
    def process_audio_stream(self, audio_chunks: AsyncGenerator[bytes, None]) -> AsyncGenerator[Dict[str, Any], None]:
        """
        Process streaming audio for real-time voice interaction.
        
        Args:
            audio_chunks: Async generator of audio chunks
            
        Yields:
            Processing results for each chunk
        """
        # This would be used for real-time streaming audio processing
        # For now, we'll implement a basic version
        async def _process():
            audio_buffer = io.BytesIO()
            
            async for chunk in audio_chunks:
                audio_buffer.write(chunk)
                
                # Process when we have enough audio (e.g., 3 seconds)
                if audio_buffer.tell() > AUDIO_SAMPLE_RATE * 3 * 2:  # 3 seconds of 16-bit audio
                    audio_buffer.seek(0)
                    audio_data = audio_buffer.getvalue()
                    
                    # Process the audio
                    result = await self.voice_conversation(audio_data)
                    yield result
                    
                    # Reset buffer
                    audio_buffer = io.BytesIO()
        
        return _process()
    
    def set_voice_settings(self, language: str = "en", rate: int = 150):
        """
        Update voice settings.
        
        Args:
            language: TTS language code
            rate: Speech rate in words per minute
        """
        self.tts_language = language
        self.speech_rate = rate
        logger.info(f"Voice settings updated: language={language}, rate={rate}")
    
    def toggle_voice(self, enabled: bool):
        """Enable or disable voice functionality."""
        self.voice_enabled = enabled
        logger.info(f"Voice functionality {'enabled' if enabled else 'disabled'}")
    
    def is_voice_available(self) -> bool:
        """Check if voice functionality is available and working."""
        try:
            # Test TTS
            test_audio = self.text_to_speech("test")
            return test_audio is not None and self.voice_enabled
        except Exception:
            return False