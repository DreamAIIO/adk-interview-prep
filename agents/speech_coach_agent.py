"""
Speech Coach Agent using Google ADK - Audio Delivery Analysis
Analyzes speaking delivery, pace, clarity, and professional communication skills.
"""
import logging
import uuid
import base64
from typing import Dict, List, Any, Optional
import asyncio

from google.adk.agents import LlmAgent
from google.adk.tools import FunctionTool
from google.adk.runners import Runner
from google.adk.sessions.in_memory_session_service import InMemorySessionService
from google.genai.types import Content, Part

from config import DEFAULT_MODEL, ADK_CONFIG

logger = logging.getLogger(__name__)

class SpeechCoachAgent:
    """
    Specialized ADK agent for analyzing speaking delivery and communication skills.
    Focuses on how something is said rather than what is said.
    """
    
    def __init__(
        self,
        job_info: Dict[str, Any],
        tools: Optional[List[Any]] = None
    ):
        """Initialize the speech coach agent with job-specific expertise."""
        self.job_info = job_info
        self.industry = job_info.get("industry", "technology")
        self.job_title = job_info.get("title", "professional")
        self.experience_level = job_info.get("experience_level", "mid-level")
        
        # Initialize tools
        if tools is None:
            tools = []
        tools.extend(self._create_speech_analysis_tools())
        
        # Create the ADK agent
        self.agent = LlmAgent(
            name="speech_coach_agent",
            model=DEFAULT_MODEL,
            description=f"Expert speech coach for {self.industry} interview delivery",
            instruction=self._generate_coaching_instruction(),
            tools=tools
        )
        
        # ADK session management
        self.app_name = f"{ADK_CONFIG['app_name_prefix']}_speech_coach"
        self.session_service = InMemorySessionService()
        self.runner = Runner(
            agent=self.agent,
            app_name=self.app_name,
            session_service=self.session_service
        )
        
        # Speech analysis parameters
        self.analysis_criteria = self._get_speech_criteria()
        
        logger.info(f"Initialized SpeechCoachAgent for {self.industry} - {self.job_title}")
    
    def _generate_coaching_instruction(self) -> str:
        """Generate specialized instruction for speech coaching."""
        return f"""
        You are an expert speech and communication coach specializing in {self.industry} interviews.
        Your expertise focuses on analyzing HOW people speak, not WHAT they say.
        
        Job Context:
        - Industry: {self.industry}
        - Position: {self.job_title}
        - Experience Level: {self.experience_level}
        - Communication Style Expected: {self._get_expected_communication_style()}
        
        Your Responsibilities:
        1. Analyze audio delivery characteristics (pace, clarity, confidence)
        2. Evaluate professional communication style for this industry
        3. Assess speaking patterns, energy, and engagement
        4. Identify filler words and speech habits
        5. Provide job-specific speaking improvement recommendations
        
        Analysis Areas:
        - TECHNICAL DELIVERY: Pace, rhythm, volume, clarity, articulation
        - PROFESSIONAL TONE: Confidence, authority, approachability, formality
        - ENGAGEMENT: Energy level, enthusiasm, conviction, presence
        - SPEECH PATTERNS: Filler words, pauses, repetition, flow
        - INDUSTRY FIT: Communication style appropriate for {self.industry}
        
        When analyzing audio:
        - Focus on delivery mechanics, not content accuracy
        - Listen for speaking confidence and clarity
        - Assess professional communication style
        - Consider industry-specific communication expectations
        - Provide specific, actionable speaking improvement tips
        - Rate delivery on a 1-10 scale with detailed feedback
        
        Remember: You're coaching HOW they speak for {self.industry} interviews, 
        focusing on delivery that builds credibility and connection.
        """
    
    def _get_expected_communication_style(self) -> str:
        """Get expected communication style for the industry/role."""
        style_map = {
            "technology": "Clear technical explanations, confident problem-solving discussion, collaborative tone",
            "healthcare": "Compassionate but authoritative, clear patient communication, professional confidence",
            "finance": "Precise and analytical, confident with numbers, trustworthy and measured",
            "consulting": "Persuasive and strategic, client-focused, confident advisory tone",
            "marketing": "Engaging and creative, persuasive storytelling, enthusiastic and dynamic",
            "education": "Clear explanatory style, patient and supportive, authoritative but approachable",
            "sales": "Persuasive and confident, relationship-building, energetic and engaging"
        }
        return style_map.get(self.industry, "Professional, clear, and confident communication")
    
    def _create_speech_analysis_tools(self) -> List[FunctionTool]:
        """Create tools specific to speech analysis."""
        
        def analyze_speaking_context(query: str) -> str:
            """
            Analyze speaking context for this specific role and industry.
            
            Args:
                query: The analysis query about speaking requirements
                
            Returns:
                Context-specific speaking analysis
            """
            speaking_contexts = {
                "pace": f"For {self.industry} interviews, optimal pace is measured and confident, allowing technical concepts to be clearly understood",
                "tone": f"Professional tone for {self.job_title} should be {self._get_expected_communication_style()}",
                "clarity": f"Crystal clear articulation is crucial for {self.industry} roles where precision matters",
                "confidence": f"Confidence indicators for {self.experience_level} {self.job_title}: steady voice, minimal hesitation, authoritative but not arrogant",
                "energy": f"Energy level should match {self.industry} culture: engaged and professional, demonstrating genuine interest",
                "filler_words": f"Minimal filler words expected for {self.experience_level} positions in {self.industry}"
            }
            
            # Find relevant context
            for key, context in speaking_contexts.items():
                if key in query.lower():
                    return f"{context}. Query: {query}"
            
            return f"General speaking analysis for {self.job_title} in {self.industry}. Context: {query}"
        
        def get_industry_speaking_standards(aspect: str) -> str:
            """
            Get industry-specific speaking standards and expectations.
            
            Args:
                aspect: Speaking aspect to analyze (pace, tone, clarity, etc.)
                
            Returns:
                Industry standards for the specified aspect
            """
            standards = {
                "technology": {
                    "pace": "Moderate pace allowing for technical explanations",
                    "tone": "Confident but collaborative, clear technical communication",
                    "clarity": "Essential for explaining complex technical concepts",
                    "energy": "Engaged and solution-focused"
                },
                "healthcare": {
                    "pace": "Measured and reassuring pace",
                    "tone": "Compassionate authority, patient-focused",
                    "clarity": "Critical for patient safety and communication",
                    "energy": "Calm confidence with genuine care"
                },
                "finance": {
                    "pace": "Precise and measured delivery",
                    "tone": "Trustworthy and analytical",
                    "clarity": "Essential for financial accuracy and trust",
                    "energy": "Steady confidence with analytical focus"
                }
            }
            
            industry_standards = standards.get(self.industry, {
                "pace": "Professional and measured",
                "tone": "Confident and appropriate",
                "clarity": "Clear and articulate",
                "energy": "Engaged and professional"
            })
            
            return industry_standards.get(aspect, f"Professional {aspect} appropriate for {self.industry}")
        
        return [
            FunctionTool(analyze_speaking_context),
            FunctionTool(get_industry_speaking_standards)
        ]
    
    def _get_speech_criteria(self) -> Dict[str, Dict[str, Any]]:
        """Define speech analysis criteria for this role/industry."""
        return {
            "pace_and_rhythm": {
                "weight": 0.2,
                "excellent": "Optimal pace for technical explanations, natural rhythm",
                "good": "Generally good pace with minor variations",
                "needs_improvement": "Too fast/slow, affects comprehension"
            },
            "clarity_and_articulation": {
                "weight": 0.25,
                "excellent": "Crystal clear pronunciation, easy to understand",
                "good": "Generally clear with minor unclear moments",
                "needs_improvement": "Difficult to understand, mumbling, unclear"
            },
            "confidence_and_authority": {
                "weight": 0.2,
                "excellent": "Strong, confident delivery with natural authority",
                "good": "Generally confident with minor hesitation",
                "needs_improvement": "Uncertain, hesitant, lacking confidence"
            },
            "professional_tone": {
                "weight": 0.15,
                "excellent": f"Perfect tone for {self.industry} interviews",
                "good": "Appropriate professional tone",
                "needs_improvement": "Tone doesn't match professional expectations"
            },
            "energy_and_engagement": {
                "weight": 0.1,
                "excellent": "High engagement, genuine enthusiasm",
                "good": "Good energy level, engaged delivery",
                "needs_improvement": "Low energy, monotone, disengaged"
            },
            "speech_patterns": {
                "weight": 0.1,
                "excellent": "Smooth flow, minimal filler words",
                "good": "Generally smooth with minor filler words",
                "needs_improvement": "Frequent filler words, choppy delivery"
            }
        }
    
    async def analyze_speech_delivery(
        self,
        audio_data: bytes,
        mime_type: str = "audio/wav",
        context: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """
        Analyze speech delivery using ADK multimodal capabilities.
        
        Args:
            audio_data: Raw audio bytes
            mime_type: Audio format
            context: Additional context (question, competency, etc.)
            
        Returns:
            Comprehensive speech delivery analysis
        """
        logger.info(f"Starting speech delivery analysis: {len(audio_data)} bytes")
        
        try:
            # Validate audio data
            if not audio_data or len(audio_data) < 1000:
                raise ValueError(f"Audio data too small: {len(audio_data)} bytes")
            
            # Create session for analysis
            session_id = f"speech_analysis_{int(asyncio.get_event_loop().time())}"
            user_id = "speech_coach"
            
            session = await self.session_service.create_session(
                app_name=self.app_name,
                user_id=user_id,
                session_id=session_id
            )
            
            # Prepare analysis prompt
            analysis_prompt = self._create_analysis_prompt(context)
            
            # Prepare multimodal content
            audio_part = Part(
                inline_data={
                    "mime_type": mime_type,
                    "data": base64.b64encode(audio_data).decode('utf-8')
                }
            )
            
            text_part = Part(text=analysis_prompt)
            
            content = Content(
                role="user",
                parts=[text_part, audio_part]
            )
            
            # Process through ADK agent
            events = []
            async for event in self.runner.run_async(
                user_id=user_id,
                session_id=session_id,
                new_message=content
            ):
                events.append(event)
                logger.debug(f"Received speech analysis event: {type(event).__name__}")
            
            # Extract analysis from events
            analysis_text = self._extract_final_response(events)
            
            if not analysis_text:
                raise Exception("No speech analysis generated")
            
            # Parse analysis into structured format
            analysis = self._parse_speech_analysis(analysis_text, audio_data, context)
            
            logger.info(f"Speech analysis completed: {analysis.get('overall_score', 0)}/10")
            return analysis
            
        except Exception as e:
            logger.error(f"Speech analysis failed: {str(e)}")
            return self._generate_fallback_analysis(audio_data, str(e), context)
    
    def _create_analysis_prompt(self, context: Dict[str, Any] = None) -> str:
        """Create analysis prompt for speech coaching."""
        competency = context.get('competency', 'General') if context else 'General'
        question_type = context.get('question_type', 'interview response') if context else 'interview response'
        
        return f"""
        Analyze this audio for SPEAKING DELIVERY (not content) in the context of a {self.industry} interview.
        
        CONTEXT:
        - Industry: {self.industry}
        - Position: {self.job_title}
        - Competency being assessed: {competency}
        - Response type: {question_type}
        - Expected communication style: {self._get_expected_communication_style()}
        
        ANALYZE THE FOLLOWING DELIVERY ASPECTS:
        
        1. PACE & RHYTHM (20%):
           - Speaking speed appropriate for technical/professional discussion
           - Natural rhythm and flow
           - Pauses used effectively
        
        2. CLARITY & ARTICULATION (25%):
           - Clear pronunciation and enunciation
           - Easy to understand
           - Professional diction
        
        3. CONFIDENCE & AUTHORITY (20%):
           - Vocal confidence and assurance
           - Steady voice without excessive hesitation
           - Appropriate authority for experience level
        
        4. PROFESSIONAL TONE (15%):
           - Tone appropriate for {self.industry} interviews
           - Professional demeanor
           - Engaging and personable
        
        5. ENERGY & ENGAGEMENT (10%):
           - Appropriate energy level
           - Genuine enthusiasm
           - Engaged delivery
        
        6. SPEECH PATTERNS (10%):
           - Minimal filler words (um, uh, like, you know)
           - Smooth transitions
           - Natural speech flow
        
        PROVIDE YOUR ANALYSIS IN THIS EXACT FORMAT:
        
        Overall Delivery Score: [0-10]/10
        
        Delivery Assessment: [2-3 sentences about overall speaking delivery]
        
        DETAILED ANALYSIS:
        
        Pace & Rhythm: [Score 0-10] - [Specific feedback about pace and rhythm]
        
        Clarity & Articulation: [Score 0-10] - [Specific feedback about clarity]
        
        Confidence & Authority: [Score 0-10] - [Specific feedback about confidence]
        
        Professional Tone: [Score 0-10] - [Specific feedback about tone]
        
        Energy & Engagement: [Score 0-10] - [Specific feedback about energy]
        
        Speech Patterns: [Score 0-10] - [Specific feedback about patterns]
        
        STRENGTHS:
        - [Speaking strength 1]
        - [Speaking strength 2]
        - [Speaking strength 3]
        
        AREAS FOR IMPROVEMENT:
        - [Improvement area 1]
        - [Improvement area 2]
        - [Improvement area 3]
        
        SPECIFIC COACHING TIPS:
        - [Actionable tip 1]
        - [Actionable tip 2]
        - [Actionable tip 3]
        
        INDUSTRY-SPECIFIC ADVICE: [Advice specific to {self.industry} communication expectations]
        
        PRACTICE RECOMMENDATIONS: [Specific practice exercises for improvement]
        
        Focus on delivery mechanics and professional communication style for {self.industry} interviews.
        """
    
    def _parse_speech_analysis(
        self,
        analysis_text: str,
        audio_data: bytes,
        context: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """Parse speech analysis response into structured format."""
        import re
        
        analysis = {
            "overall_score": 5,
            "delivery_assessment": "",
            "detailed_scores": {},
            "strengths": [],
            "improvements": [],
            "coaching_tips": [],
            "industry_advice": "",
            "practice_recommendations": "",
            "audio_metadata": {
                "size_bytes": len(audio_data),
                "analysis_type": "speech_delivery",
                "industry": self.industry,
                "job_title": self.job_title
            },
            "context": context or {}
        }
        
        try:
            # Extract overall score
            score_match = re.search(r'Overall Delivery Score:\s*(\d+)(?:/10)?', analysis_text)
            if score_match:
                analysis["overall_score"] = int(score_match.group(1))
            
            # Extract delivery assessment
            assessment_match = re.search(r'Delivery Assessment:\s*(.*?)(?=\n.*?:|\Z)', analysis_text, re.DOTALL)
            if assessment_match:
                analysis["delivery_assessment"] = assessment_match.group(1).strip()
            
            # Extract detailed scores
            score_patterns = [
                ("pace_rhythm", r'Pace & Rhythm:\s*(\d+).*?-\s*(.*?)(?=\n|$)'),
                ("clarity_articulation", r'Clarity & Articulation:\s*(\d+).*?-\s*(.*?)(?=\n|$)'),
                ("confidence_authority", r'Confidence & Authority:\s*(\d+).*?-\s*(.*?)(?=\n|$)'),
                ("professional_tone", r'Professional Tone:\s*(\d+).*?-\s*(.*?)(?=\n|$)'),
                ("energy_engagement", r'Energy & Engagement:\s*(\d+).*?-\s*(.*?)(?=\n|$)'),
                ("speech_patterns", r'Speech Patterns:\s*(\d+).*?-\s*(.*?)(?=\n|$)')
            ]
            
            for key, pattern in score_patterns:
                match = re.search(pattern, analysis_text, re.IGNORECASE)
                if match:
                    score = int(match.group(1))
                    feedback = match.group(2).strip()
                    analysis["detailed_scores"][key] = {
                        "score": score,
                        "feedback": feedback
                    }
            
            # Extract lists
            for section_name, key in [
                ("STRENGTHS", "strengths"),
                ("AREAS FOR IMPROVEMENT", "improvements"),
                ("SPECIFIC COACHING TIPS", "coaching_tips")
            ]:
                section_match = re.search(f'{section_name}:(.*?)(?=\n[A-Z]|\Z)', analysis_text, re.DOTALL)
                if section_match:
                    items = re.findall(r'-\s*(.*?)(?=\n\s*-|\n[A-Z]|\Z)', section_match.group(1), re.DOTALL)
                    analysis[key] = [item.strip() for item in items if item.strip()]
            
            # Extract specific advice sections
            industry_match = re.search(r'INDUSTRY-SPECIFIC ADVICE:\s*(.*?)(?=\nPRACTICE RECOMMENDATIONS:|\Z)', analysis_text, re.DOTALL)
            if industry_match:
                analysis["industry_advice"] = industry_match.group(1).strip()
            
            practice_match = re.search(r'PRACTICE RECOMMENDATIONS:\s*(.*?)(?=\Z)', analysis_text, re.DOTALL)
            if practice_match:
                analysis["practice_recommendations"] = practice_match.group(1).strip()
            
        except Exception as e:
            logger.error(f"Error parsing speech analysis: {str(e)}")
        
        return analysis
    
    def _generate_fallback_analysis(
        self,
        audio_data: bytes,
        error_msg: str,
        context: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """Generate fallback analysis when speech processing fails."""
        audio_size_kb = len(audio_data) / 1024 if audio_data else 0
        
        return {
            "overall_score": 5,
            "delivery_assessment": f"Speech analysis temporarily unavailable. Audio received ({audio_size_kb:.1f} KB) but processing failed.",
            "detailed_scores": {
                "pace_rhythm": {"score": 5, "feedback": "Unable to analyze pace due to processing error"},
                "clarity_articulation": {"score": 5, "feedback": "Unable to analyze clarity due to processing error"},
                "confidence_authority": {"score": 5, "feedback": "Unable to analyze confidence due to processing error"},
                "professional_tone": {"score": 5, "feedback": "Unable to analyze tone due to processing error"},
                "energy_engagement": {"score": 5, "feedback": "Unable to analyze energy due to processing error"},
                "speech_patterns": {"score": 5, "feedback": "Unable to analyze patterns due to processing error"}
            },
            "strengths": [
                "Audio was successfully recorded",
                f"Appropriate recording length for {self.industry} interview",
                "Attempted to provide comprehensive response"
            ],
            "improvements": [
                "Ensure clear audio quality for optimal analysis",
                "Check microphone settings and environment",
                "Try again with stable internet connection"
            ],
            "coaching_tips": [
                f"Practice speaking clearly for {self.industry} interviews",
                "Record in a quiet environment for best results",
                "Speak at a moderate pace for technical discussions"
            ],
            "industry_advice": f"For {self.industry} interviews, focus on clear, confident communication that demonstrates technical expertise and professional demeanor.",
            "practice_recommendations": "Practice speaking aloud, record yourself regularly, and focus on clear articulation and confident delivery.",
            "audio_metadata": {
                "size_bytes": len(audio_data) if audio_data else 0,
                "analysis_type": "speech_delivery_fallback",
                "industry": self.industry,
                "job_title": self.job_title,
                "error": error_msg
            },
            "context": context or {}
        }
    
    def _extract_final_response(self, events) -> str:
        """Extract final response text from ADK events."""
        response = ""
        
        for event in reversed(events):
            if hasattr(event, 'content') and event.content:
                if hasattr(event.content, 'parts') and event.content.parts:
                    for part in event.content.parts:
                        if hasattr(part, 'text') and part.text:
                            response = part.text
                            break
                if response:
                    break
        
        return response.strip() if response else ""
    
    def get_speech_coaching_summary(self) -> Dict[str, Any]:
        """Get summary of speech coaching capabilities and focus areas."""
        return {
            "coach_type": "speech_delivery",
            "industry_focus": self.industry,
            "job_title": self.job_title,
            "analysis_areas": list(self.analysis_criteria.keys()),
            "expected_communication_style": self._get_expected_communication_style(),
            "key_metrics": [
                "Pace & Rhythm (20%)",
                "Clarity & Articulation (25%)",
                "Confidence & Authority (20%)",
                "Professional Tone (15%)",
                "Energy & Engagement (10%)",
                "Speech Patterns (10%)"
            ],
            "coaching_specialties": [
                f"{self.industry} communication standards",
                f"{self.experience_level} professional presence",
                "Interview delivery optimization",
                "Technical explanation clarity",
                "Professional confidence building"
            ]
        }


class MockSpeechCoachAgent:
    """Mock speech coach for testing when ADK multimodal isn't available."""
    
    def __init__(self, job_info: Dict[str, Any], tools: Optional[List[Any]] = None):
        """Initialize mock speech coach."""
        self.job_info = job_info
        self.industry = job_info.get("industry", "technology")
        self.job_title = job_info.get("title", "professional")
        logger.info("Initialized MockSpeechCoachAgent (for testing)")
    
    async def analyze_speech_delivery(
        self,
        audio_data: bytes,
        mime_type: str = "audio/wav",
        context: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """Generate mock speech analysis."""
        audio_size_kb = len(audio_data) / 1024
        
        # Generate realistic mock scores based on audio size
        base_score = 6 if audio_size_kb > 10 else 5
        
        detailed_scores = {
            "pace_rhythm": {
                "score": base_score + 1,
                "feedback": "Good natural pace, appropriate for technical discussion"
            },
            "clarity_articulation": {
                "score": base_score,
                "feedback": "Generally clear pronunciation with minor unclear moments"
            },
            "confidence_authority": {
                "score": base_score,
                "feedback": "Shows confidence with some hesitation on technical details"
            },
            "professional_tone": {
                "score": base_score + 1,
                "feedback": f"Appropriate professional tone for {self.industry} interviews"
            },
            "energy_engagement": {
                "score": base_score,
                "feedback": "Good energy level, engaged delivery throughout"
            },
            "speech_patterns": {
                "score": base_score - 1,
                "feedback": "Some filler words present, generally smooth flow"
            }
        }
        
        overall_score = sum(scores["score"] for scores in detailed_scores.values()) // len(detailed_scores)
        
        return {
            "overall_score": overall_score,
            "delivery_assessment": f"Good overall delivery for {self.industry} interview. Clear communication with room for minor improvements in confidence and reducing filler words.",
            "detailed_scores": detailed_scores,
            "strengths": [
                "Clear and professional communication style",
                "Appropriate pace for technical explanations",
                "Good energy and engagement throughout"
            ],
            "improvements": [
                "Reduce filler words (um, uh) for more polished delivery",
                "Increase vocal confidence on technical topics",
                "Practice smoother transitions between ideas"
            ],
            "coaching_tips": [
                "Practice speaking technical concepts aloud to build confidence",
                "Record yourself and listen for filler words",
                "Use strategic pauses instead of filler words"
            ],
            "industry_advice": f"For {self.industry} interviews, focus on clear technical explanations with confident, measured delivery that demonstrates expertise.",
            "practice_recommendations": "Practice explaining technical concepts clearly, work on eliminating filler words, and build confidence through regular speaking practice.",
            "audio_metadata": {
                "size_bytes": len(audio_data),
                "analysis_type": "mock_speech_delivery",
                "industry": self.industry,
                "job_title": self.job_title,
                "note": "This is a mock analysis for testing purposes"
            },
            "context": context or {}
        }
    
    def get_speech_coaching_summary(self) -> Dict[str, Any]:
        """Get mock coaching summary."""
        return {
            "coach_type": "mock_speech_delivery",
            "industry_focus": self.industry,
            "job_title": self.job_title,
            "note": "Mock speech coach for testing"
        }


def get_speech_coach_agent(job_info: Dict[str, Any], tools: Optional[List[Any]] = None) -> SpeechCoachAgent:
    """Get the appropriate speech coach agent."""
    try:
        return SpeechCoachAgent(job_info, tools)
    except Exception as e:
        logger.warning(f"Could not initialize speech coach agent: {e}")
        logger.info("Using mock speech coach for testing")
        return MockSpeechCoachAgent(job_info, tools)