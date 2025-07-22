"""
Audio Processing Handler for Voice Streaming
Handles WebM to PCM conversion for ADK voice streaming.
"""
import tempfile
import subprocess
import os
import logging
from typing import Optional

logger = logging.getLogger(__name__)

class AudioProcessor:
    """Audio processor for WebM to PCM conversion."""
    
    def __init__(self):
        self.input_sample_rate = 16000
        self.output_sample_rate = 24000
        logger.info(f"Audio processor initialized: {self.input_sample_rate}Hz recording, {self.output_sample_rate}Hz playback")
        
    def convert_webm_to_pcm(self, webm_data: bytes) -> bytes:
        """
        Convert WebM audio data to PCM format for ADK.
        
        Args:
            webm_data: Raw WebM audio bytes
            
        Returns:
            PCM audio bytes, or empty bytes if conversion fails
        """
        if len(webm_data) < 100:  # Too small to be valid audio
            logger.warning(f"WebM data too small: {len(webm_data)} bytes")
            return b""
        
        logger.info(f"Converting WebM audio: {len(webm_data)} bytes")
        
        webm_path = None
        pcm_path = None
        
        try:
            # Create temporary files
            with tempfile.NamedTemporaryFile(suffix=".webm", delete=False) as webm_file:
                webm_file.write(webm_data)
                webm_file.flush()
                webm_path = webm_file.name
            
            with tempfile.NamedTemporaryFile(suffix=".pcm", delete=False) as pcm_file:
                pcm_path = pcm_file.name
            
            # FFmpeg command to convert WebM to PCM
            cmd = [
                'ffmpeg', '-y',                          # Overwrite output files
                '-i', webm_path,                         # Input WebM file
                '-f', 's16le',                          # Output format: signed 16-bit little-endian
                '-ar', str(self.input_sample_rate),     # Sample rate: 16000 Hz
                '-ac', '1',                             # Audio channels: 1 (mono)
                '-loglevel', 'error',                   # Reduce verbose output
                pcm_path                                # Output PCM file
            ]
            
            # Run FFmpeg conversion
            result = subprocess.run(
                cmd, 
                capture_output=True, 
                text=True, 
                timeout=10  # 10 second timeout
            )
            
            if result.returncode != 0:
                logger.error(f"FFmpeg conversion failed: {result.stderr}")
                return b""
            
            # Read the converted PCM data
            if os.path.exists(pcm_path) and os.path.getsize(pcm_path) > 0:
                with open(pcm_path, 'rb') as f:
                    pcm_data = f.read()
                logger.info(f"Successfully converted WebM to PCM: {len(webm_data)} → {len(pcm_data)} bytes")
                return pcm_data
            else:
                logger.error("PCM output file is empty or doesn't exist")
                return b""
                
        except subprocess.TimeoutExpired:
            logger.error("FFmpeg conversion timed out")
            return b""
        except FileNotFoundError:
            logger.error("FFmpeg not found. Please install FFmpeg: https://ffmpeg.org/download.html")
            return b""
        except Exception as e:
            logger.error(f"Audio conversion error: {e}")
            return b""
        finally:
            # Cleanup temporary files
            try:
                if webm_path and os.path.exists(webm_path):
                    os.unlink(webm_path)
                if pcm_path and os.path.exists(pcm_path):
                    os.unlink(pcm_path)
            except Exception as e:
                logger.warning(f"Failed to cleanup temp files: {e}")
    
    def validate_audio_data(self, audio_data: bytes, mime_type: str) -> bool:
        """
        Validate audio data before processing.
        
        Args:
            audio_data: Raw audio bytes
            mime_type: MIME type of the audio
            
        Returns:
            True if audio data appears valid
        """
        if not audio_data or len(audio_data) < 100:
            return False
            
        if not mime_type or not mime_type.startswith('audio/'):
            return False
            
        # Basic WebM header validation
        if mime_type.startswith('audio/webm'):
            # WebM files should start with EBML header
            if len(audio_data) >= 4:
                # Check for EBML signature (0x1A45DFA3)
                header = audio_data[:4]
                if header == b'\x1a\x45\xdf\xa3':
                    return True
                    
        # For other audio types, just check minimum size
        return len(audio_data) >= 100
    
    def get_audio_info(self, audio_data: bytes, mime_type: str) -> dict:
        """
        Get information about audio data.
        
        Args:
            audio_data: Raw audio bytes
            mime_type: MIME type of the audio
            
        Returns:
            Dictionary with audio information
        """
        return {
            "size_bytes": len(audio_data),
            "mime_type": mime_type,
            "valid": self.validate_audio_data(audio_data, mime_type),
            "estimated_duration_ms": len(audio_data) / 16 if mime_type.startswith('audio/webm') else None
        }