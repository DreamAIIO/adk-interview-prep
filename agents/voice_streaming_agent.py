"""
Voice Streaming Agent using ADK Live API - FIXED VERSION.
Provides professional voice streaming capabilities with proper session management.
"""
import logging
import asyncio
import uuid
from typing import Dict, Any, Optional, AsyncGenerator
from datetime import datetime

from google.adk.agents import LlmAgent
from google.adk.runners import InMemoryRunner
from google.adk.sessions.in_memory_session_service import InMemorySessionService
from google.adk.agents import LiveRequestQueue
from google.adk.agents.run_config import RunConfig
from google.genai.types import Content, Part, Blob
from google.genai import types as genai_types

from config import VOICE_MODEL, API_CONFIG

logger = logging.getLogger(__name__)

class VoiceStreamingAgent:
    """
    Professional voice streaming agent using ADK Live API.
    Handles bidirectional audio streaming with proper session management.
    """
    
    def __init__(self, job_info: Dict[str, Any]):
        """Initialize voice streaming agent with job context."""
        self.job_info = job_info
        self.industry = job_info.get("industry", "technology")
        self.job_title = job_info.get("title", "position")
        
        # Voice streaming state
        self.active_sessions: Dict[str, Dict[str, Any]] = {}
        self.session_service = InMemorySessionService()
        
        # Initialize voice agent
        self.voice_agent = self._create_voice_agent()
        
        # Voice configuration
        self.voice_config = self._create_voice_config()
        
        logger.info(f"Voice streaming agent initialized for {self.industry}")
    
    def _create_voice_agent(self) -> LlmAgent:
        """Create the ADK voice agent with proper configuration."""
        voice_instruction = f"""
        You are a professional interview preparation voice assistant for a {self.job_title} 
        role in the {self.industry} industry.
        
        Your capabilities:
        1. Listen to candidate's spoken answers during practice
        2. Provide real-time voice feedback and guidance
        3. Help with STAR method structuring through voice
        4. Offer immediate suggestions and encouragement
        
        Job context:
        - Position: {self.job_title}
        - Industry: {self.industry}
        - Skills: {', '.join(self.job_info.get('skills', [])[:5])}
        - Technologies: {', '.join(self.job_info.get('technologies', [])[:5])}
        
        Voice interaction guidelines:
        - Speak clearly and at a professional pace
        - Provide constructive, encouraging feedback
        - Ask clarifying questions when needed
        - Help structure responses using STAR method
        - Be supportive and confidence-building
        
        Always maintain a professional, supportive tone while providing valuable guidance.
        """
        
        return LlmAgent(
            name="voice_interview_coach",
            model=VOICE_MODEL,
            description="Professional voice interview preparation coach",
            instruction=voice_instruction
        )
    
    def _create_voice_config(self) -> genai_types.SpeechConfig:
        """Create voice configuration for ADK Live API."""
        voice_config = genai_types.VoiceConfig(
            prebuilt_voice_config=genai_types.PrebuiltVoiceConfigDict(
                voice_name='Aoede'  # Professional, clear voice
            )
        )
        
        return genai_types.SpeechConfig(voice_config=voice_config)
    
    async def create_voice_session(
        self, 
        user_id: str,
        context: Dict[str, Any] = None
    ) -> str:
        """
        Create a new voice streaming session.
        
        Args:
            user_id: Unique identifier for the user
            context: Additional context for the session
            
        Returns:
            session_id: Unique session identifier
        """
        try:
            session_id = f"voice_{uuid.uuid4().hex[:8]}"
            
            # Create ADK session
            session = await self.session_service.create_session(
                app_name="voice_interview_coach",
                user_id=user_id,
                session_id=session_id
            )
            
            # Create runner for this session
            runner = InMemoryRunner(
                app_name="voice_interview_coach",
                agent=self.voice_agent
            )
            
            # Configure for voice streaming - FIXED
            run_config = RunConfig(
                response_modalities=["AUDIO", "TEXT"],
                speech_config=self.voice_config
            )
            
            # Create live request queue
            live_request_queue = LiveRequestQueue()
            
            # Start live streaming
            live_events = runner.run_live(
                session=session,
                live_request_queue=live_request_queue,
                run_config=run_config
            )
            
            # Store session data
            self.active_sessions[session_id] = {
                "session": session,
                "runner": runner,
                "live_request_queue": live_request_queue,
                "live_events": live_events,
                "user_id": user_id,
                "context": context or {},
                "created_at": datetime.now(),
                "is_active": True
            }
            
            logger.info(f"Created voice session {session_id} for user {user_id}")
            return session_id
            
        except Exception as e:
            logger.error(f"Error creating voice session: {str(e)}")
            raise
    
    async def send_audio_to_session(
        self, 
        session_id: str, 
        audio_data: bytes, 
        mime_type: str = "audio/pcm"
    ) -> bool:
        """
        Send audio data to an active voice session.
        
        Args:
            session_id: Session identifier
            audio_data: Raw audio bytes
            mime_type: Audio format (default: audio/pcm)
            
        Returns:
            bool: Success status
        """
        try:
            if session_id not in self.active_sessions:
                logger.error(f"Session {session_id} not found")
                return False
            
            session_data = self.active_sessions[session_id]
            live_request_queue = session_data["live_request_queue"]
            
            if not session_data["is_active"]:
                logger.error(f"Session {session_id} is not active")
                return False
            
            # Skip silence to reduce processing load
            if self._is_silence(audio_data):
                logger.debug("Skipping silent audio chunk")
                return True
            
            # Create audio blob with proper mime type for ADK
            audio_blob = Blob(data=audio_data, mime_type="audio/pcm")
            
            # Send directly to ADK - FIXED: Remove LiveRequest wrapper
            live_request_queue.send_realtime(audio_blob)
            
            logger.debug(f"Sent {len(audio_data)} bytes of audio to session {session_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error sending audio to session {session_id}: {str(e)}")
            return False
    
    def _is_silence(self, audio_data: bytes, threshold: float = 0.01) -> bool:
        """
        Quick silence detection to avoid processing silent audio.
        
        Args:
            audio_data: PCM audio data
            threshold: Silence threshold
            
        Returns:
            bool: True if audio is mostly silent
        """
        try:
            if not audio_data or len(audio_data) < 100:
                return True
            
            # Convert bytes to 16-bit integers for analysis
            import struct
            samples = struct.unpack(f'{len(audio_data)//2}h', audio_data)
            
            # Calculate RMS
            rms = (sum(s*s for s in samples) / len(samples)) ** 0.5
            normalized_rms = rms / 32767.0  # Normalize to 0-1 range
            
            return normalized_rms < threshold
            
        except Exception:
            return False  # If we can't analyze, don't skip
    
    async def send_text_to_session(
        self, 
        session_id: str, 
        text: str
    ) -> bool:
        """
        Send text message to an active voice session.
        
        Args:
            session_id: Session identifier
            text: Text message to send
            
        Returns:
            bool: Success status
        """
        try:
            if session_id not in self.active_sessions:
                logger.error(f"Session {session_id} not found")
                return False
            
            session_data = self.active_sessions[session_id]
            live_request_queue = session_data["live_request_queue"]
            
            if not session_data["is_active"]:
                logger.error(f"Session {session_id} is not active")
                return False
            
            # Create content and send to ADK
            content = Content(role="user", parts=[Part(text=text)])
            live_request_queue.send_content(content=content)
            
            logger.debug(f"Sent text to session {session_id}: {text[:50]}...")
            return True
            
        except Exception as e:
            logger.error(f"Error sending text to session {session_id}: {str(e)}")
            return False
    
    async def get_session_events(
        self, 
        session_id: str
    ) -> Optional[AsyncGenerator]:
        """
        Get live events stream for a session.
        
        Args:
            session_id: Session identifier
            
        Returns:
            AsyncGenerator: Stream of live events or None if session not found
        """
        if session_id not in self.active_sessions:
            logger.error(f"Session {session_id} not found")
            return None
        
        session_data = self.active_sessions[session_id]
        
        if not session_data["is_active"]:
            logger.error(f"Session {session_id} is not active")
            return None
        
        return session_data["live_events"]
    
    async def close_session(self, session_id: str) -> bool:
        """
        Close an active voice session.
        
        Args:
            session_id: Session identifier
            
        Returns:
            bool: Success status
        """
        try:
            if session_id not in self.active_sessions:
                logger.warning(f"Session {session_id} not found for closing")
                return False
            
            session_data = self.active_sessions[session_id]
            
            # Close live request queue
            if session_data.get("live_request_queue"):
                session_data["live_request_queue"].close()
            
            # Mark as inactive
            session_data["is_active"] = False
            
            # Remove from active sessions
            del self.active_sessions[session_id]
            
            logger.info(f"Closed voice session {session_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error closing session {session_id}: {str(e)}")
            return False
    
    def get_session_status(self, session_id: str) -> Dict[str, Any]:
        """
        Get status information for a session.
        
        Args:
            session_id: Session identifier
            
        Returns:
            Dict containing session status information
        """
        if session_id not in self.active_sessions:
            return {
                "exists": False,
                "is_active": False,
                "error": "Session not found"
            }
        
        session_data = self.active_sessions[session_id]
        
        return {
            "exists": True,
            "is_active": session_data["is_active"],
            "user_id": session_data["user_id"],
            "created_at": session_data["created_at"].isoformat(),
            "context": session_data["context"]
        }
    
    def get_active_sessions_count(self) -> int:
        """Get count of currently active sessions."""
        return len([s for s in self.active_sessions.values() if s["is_active"]])
    
    async def cleanup_inactive_sessions(self, max_age_hours: int = 24) -> int:
        """
        Clean up inactive or old sessions.
        
        Args:
            max_age_hours: Maximum age for sessions in hours
            
        Returns:
            int: Number of sessions cleaned up
        """
        from datetime import timedelta
        
        cleanup_count = 0
        current_time = datetime.now()
        cutoff_time = current_time - timedelta(hours=max_age_hours)
        
        sessions_to_remove = []
        
        for session_id, session_data in self.active_sessions.items():
            # Remove if inactive or too old
            if (not session_data["is_active"] or 
                session_data["created_at"] < cutoff_time):
                
                sessions_to_remove.append(session_id)
        
        # Clean up identified sessions
        for session_id in sessions_to_remove:
            await self.close_session(session_id)
            cleanup_count += 1
        
        logger.info(f"Cleaned up {cleanup_count} voice sessions")
        return cleanup_count
    
    async def initialize_for_practice_question(
        self,
        user_id: str,
        question_context: Dict[str, Any]
    ) -> str:
        """
        Initialize voice session specifically for practice questions.
        
        Args:
            user_id: User identifier
            question_context: Context about the current question
            
        Returns:
            str: Session ID for the practice session
        """
        context = {
            "type": "practice_question",
            "competency": question_context.get("competency"),
            "difficulty": question_context.get("difficulty"),
            "question": question_context.get("question"),
            "industry": self.industry,
            "job_title": self.job_title
        }
        
        session_id = await self.create_voice_session(user_id, context)
        
        # Send initial context to the agent
        initial_prompt = f"""
        Starting practice session for {context['competency']} competency.
        Question: {context['question']}
        
        Please be ready to provide voice guidance and feedback as the candidate answers.
        Focus on helping them structure their response using the STAR method.
        """
        
        await self.send_text_to_session(session_id, initial_prompt)
        
        logger.info(f"Initialized practice question session {session_id}")
        return session_id
    
    async def initialize_for_practice_test(
        self,
        user_id: str,
        test_context: Dict[str, Any]
    ) -> str:
        """
        Initialize voice session specifically for practice tests.
        
        Args:
            user_id: User identifier
            test_context: Context about the current test
            
        Returns:
            str: Session ID for the test session
        """
        context = {
            "type": "practice_test",
            "total_questions": test_context.get("total_questions"),
            "current_question": test_context.get("current_question", 1),
            "competencies": test_context.get("competencies", []),
            "industry": self.industry,
            "job_title": self.job_title
        }
        
        session_id = await self.create_voice_session(user_id, context)
        
        # Send initial context to the agent
        initial_prompt = f"""
        Starting practice test session with {context['total_questions']} questions.
        Competencies covered: {', '.join(context['competencies'])}
        
        Please provide supportive voice guidance throughout the test.
        Help the candidate stay calm and structure their responses effectively.
        """
        
        await self.send_text_to_session(session_id, initial_prompt)
        
        logger.info(f"Initialized practice test session {session_id}")
        return session_id