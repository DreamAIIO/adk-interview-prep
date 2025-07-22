"""
Enhanced Voice Workflow Agent - Parallel Content and Delivery Analysis
Orchestrates parallel analysis of both content and speech delivery using ADK multi-agent patterns.
"""
import logging
import uuid
import asyncio
from typing import Dict, Any, Optional, List, Tuple
from collections import defaultdict

from google.adk.agents import ParallelAgent, SequentialAgent, LlmAgent
from google.adk.runners import Runner
from google.adk.sessions.in_memory_session_service import InMemorySessionService
from google.genai.types import Content, Part

from agents.transcription_agent import TranscriptionAgent, get_transcription_agent
from agents.speech_coach_agent import SpeechCoachAgent, get_speech_coach_agent
from agents.interview_manager import InterviewManager
from config import ADK_CONFIG, DEFAULT_MODEL

logger = logging.getLogger(__name__)

class EnhancedVoiceWorkflowAgent:
    """
    Enhanced voice workflow with parallel content and delivery analysis.
    
    Architecture:
    VoiceWorkflowAgent
    ├── ParallelAnalysisAgent
    │   ├── TranscriptionAgent (content analysis)
    │   └── SpeechCoachAgent (delivery analysis)
    └── EvaluationSynthesisAgent (combines both)
    """
    
    def __init__(self, job_info: Dict[str, Any]):
        """Initialize enhanced voice workflow with parallel agents."""
        self.job_info = job_info
        self.industry = job_info.get("industry", "technology")
        self.job_title = job_info.get("title", "professional")
        
        # Initialize component agents
        self.transcription_agent = get_transcription_agent()
        self.speech_coach_agent = get_speech_coach_agent(job_info)
        self.interview_manager = InterviewManager(job_info)
        
        # Create evaluation synthesis agent
        self.synthesis_agent = self._create_synthesis_agent()
        
        # Create parallel analysis workflow
        self.parallel_analysis = ParallelAgent(
            name="voice_parallel_analysis",
            sub_agents=[
                # Note: We'll handle these manually since they're not standard LlmAgents
            ],
            description="Parallel analysis of content and delivery from voice input"
        )
        
        # Create main sequential workflow
        self.main_workflow = SequentialAgent(
            name="enhanced_voice_workflow",
            sub_agents=[
                self.synthesis_agent  # Will coordinate the parallel analysis internally
            ],
            description="Complete voice analysis workflow: audio → parallel analysis → synthesis"
        )
        
        # ADK session management
        self.app_name = f"{ADK_CONFIG['app_name_prefix']}_enhanced_voice"
        self.session_service = InMemorySessionService()
        self.runner = Runner(
            agent=self.main_workflow,
            app_name=self.app_name,
            session_service=self.session_service
        )
        
        # Workflow state tracking
        self.analysis_cache = {}
        self.workflow_metrics = defaultdict(int)
        
        logger.info(f"Initialized EnhancedVoiceWorkflowAgent for {self.industry}")
    
    def _create_synthesis_agent(self) -> LlmAgent:
        """Create synthesis agent that combines content and delivery analysis."""
        synthesis_tools = [self._create_synthesis_tools()]
        
        return LlmAgent(
            name="evaluation_synthesis_agent",
            model=DEFAULT_MODEL,
            description="Synthesizes content and delivery analysis into comprehensive evaluation",
            instruction=f"""
            You are an expert evaluation synthesis agent for {self.industry} interview preparation.
            Your role is to combine content analysis and speech delivery analysis into a unified, comprehensive evaluation.
            
            Job Context:
            - Industry: {self.industry}
            - Position: {self.job_title}
            - Evaluation Type: Comprehensive (Content + Delivery)
            
            Your Responsibilities:
            1. Integrate content quality assessment with delivery analysis
            2. Provide balanced evaluation considering both what was said and how it was said
            3. Generate actionable improvement recommendations across all dimensions
            4. Create holistic interview readiness assessment
            5. Prioritize improvements based on impact for {self.industry} interviews
            
            Evaluation Integration:
            - Weight content analysis appropriately for technical accuracy and completeness
            - Weight delivery analysis for professional communication and presence
            - Consider industry-specific expectations for both content and delivery
            - Provide unified scoring that reflects interview success likelihood
            - Balance technical competency demonstration with communication effectiveness
            
            Output Format:
            - Combined overall score reflecting both content and delivery
            - Integrated strengths that show content + delivery synergies
            - Prioritized improvement areas based on impact
            - Comprehensive coaching recommendations
            - Industry-specific interview readiness assessment
            
            Focus on helping candidates succeed in {self.industry} interviews by excelling in both what they say and how they say it.
            """,
            tools=synthesis_tools
        )
    
    def _create_synthesis_tools(self) -> List:
        """Create tools for evaluation synthesis."""
        from google.adk.tools import FunctionTool
        
        def calculate_weighted_score(content_score: float, delivery_score: float) -> str:
            """
            Calculate weighted overall score based on industry expectations.
            
            Args:
                content_score: Score from content analysis (0-10)
                delivery_score: Score from delivery analysis (0-10)
                
            Returns:
                Weighted score calculation and reasoning
            """
            # Industry-specific weighting
            industry_weights = {
                "technology": {"content": 0.7, "delivery": 0.3},
                "sales": {"content": 0.4, "delivery": 0.6},
                "consulting": {"content": 0.5, "delivery": 0.5},
                "healthcare": {"content": 0.6, "delivery": 0.4},
                "finance": {"content": 0.65, "delivery": 0.35},
                "marketing": {"content": 0.45, "delivery": 0.55},
                "education": {"content": 0.6, "delivery": 0.4}
            }
            
            weights = industry_weights.get(self.industry, {"content": 0.6, "delivery": 0.4})
            
            weighted_score = (content_score * weights["content"]) + (delivery_score * weights["delivery"])
            
            return f"""
            Weighted Score Calculation for {self.industry}:
            Content: {content_score}/10 (weight: {weights['content']*100}%) = {content_score * weights['content']:.1f}
            Delivery: {delivery_score}/10 (weight: {weights['delivery']*100}%) = {delivery_score * weights['delivery']:.1f}
            Overall: {weighted_score:.1f}/10
            
            Reasoning: In {self.industry}, {'content knowledge and technical accuracy' if weights['content'] > weights['delivery'] else 'communication and delivery skills'} are weighted more heavily for interview success.
            """
        
        def prioritize_improvements(content_improvements: List[str], delivery_improvements: List[str]) -> str:
            """
            Prioritize improvement areas based on industry impact.
            
            Args:
                content_improvements: List of content improvement areas
                delivery_improvements: List of delivery improvement areas
                
            Returns:
                Prioritized improvement recommendations
            """
            # Industry-specific priorities
            if self.industry in ["technology", "finance", "healthcare"]:
                priority_order = "Content accuracy and technical depth are primary, followed by clear communication delivery"
            elif self.industry in ["sales", "marketing", "consulting"]:
                priority_order = "Communication delivery and persuasive presence are primary, supported by solid content knowledge"
            else:
                priority_order = "Balanced focus on both content mastery and professional delivery"
            
            return f"""
            Improvement Priority for {self.industry}:
            
            Strategic Approach: {priority_order}
            
            HIGH PRIORITY (Address First):
            Content: {content_improvements[0] if content_improvements else 'No major content issues'}
            Delivery: {delivery_improvements[0] if delivery_improvements else 'No major delivery issues'}
            
            MEDIUM PRIORITY (Address Next):
            Content: {content_improvements[1] if len(content_improvements) > 1 else 'Continue content refinement'}
            Delivery: {delivery_improvements[1] if len(delivery_improvements) > 1 else 'Continue delivery practice'}
            
            ONGOING DEVELOPMENT:
            Content: {content_improvements[2] if len(content_improvements) > 2 else 'Maintain content knowledge'}
            Delivery: {delivery_improvements[2] if len(delivery_improvements) > 2 else 'Maintain delivery skills'}
            """
        
        return [FunctionTool(calculate_weighted_score), FunctionTool(prioritize_improvements)]
    
    async def process_voice_question_response(
        self,
        question: Dict[str, Any],
        audio_data: bytes,
        mime_type: str = "audio/wav"
    ) -> Dict[str, Any]:
        """
        Process voice response through enhanced parallel workflow.
        
        Args:
            question: Interview question data
            audio_data: Audio response bytes
            mime_type: Audio format
            
        Returns:
            Comprehensive evaluation with content and delivery analysis
        """
        workflow_id = str(uuid.uuid4())
        logger.info(f"Starting enhanced voice workflow {workflow_id} for {question.get('competency', 'Unknown')}")
        
        try:
            # Step 1: Parallel Analysis (Content + Delivery)
            content_analysis, delivery_analysis = await self._run_parallel_analysis(
                audio_data, mime_type, question, workflow_id
            )
            
            # Validate parallel analysis results
            if not content_analysis or content_analysis.get('status') != 'success':
                return self._generate_error_result(workflow_id, "content_analysis", content_analysis)
            
            if not delivery_analysis or delivery_analysis.get('overall_score', 0) < 0:
                logger.warning(f"Delivery analysis failed for workflow {workflow_id}, continuing with content only")
                delivery_analysis = self._generate_fallback_delivery_analysis()
            
            # Step 2: Synthesis Evaluation
            synthesis_result = await self._synthesize_evaluations(
                content_analysis, delivery_analysis, question, workflow_id
            )
            
            # Step 3: Compile Final Result
            final_result = self._compile_enhanced_result(
                workflow_id, content_analysis, delivery_analysis, synthesis_result, question
            )
            
            # Update metrics
            self.workflow_metrics['successful_workflows'] += 1
            self.workflow_metrics['content_and_delivery_analyzed'] += 1
            
            logger.info(f"Enhanced voice workflow {workflow_id} completed successfully")
            return final_result
            
        except Exception as e:
            logger.error(f"Enhanced voice workflow {workflow_id} failed: {str(e)}")
            self.workflow_metrics['failed_workflows'] += 1
            return self._generate_error_result(workflow_id, "workflow_error", str(e))
    
    async def _run_parallel_analysis(
        self,
        audio_data: bytes,
        mime_type: str,
        question: Dict[str, Any],
        workflow_id: str
    ) -> Tuple[Dict[str, Any], Dict[str, Any]]:
        """Run content and delivery analysis in parallel."""
        logger.info(f"Running parallel analysis for workflow {workflow_id}")
        
        # Create analysis tasks
        content_task = self._analyze_content(audio_data, mime_type, question, workflow_id)
        delivery_task = self._analyze_delivery(audio_data, mime_type, question, workflow_id)
        
        # Run in parallel
        content_result, delivery_result = await asyncio.gather(
            content_task,
            delivery_task,
            return_exceptions=True
        )
        
        # Handle exceptions
        if isinstance(content_result, Exception):
            logger.error(f"Content analysis failed: {content_result}")
            content_result = {"status": "failed", "error": str(content_result)}
        
        if isinstance(delivery_result, Exception):
            logger.error(f"Delivery analysis failed: {delivery_result}")
            delivery_result = self._generate_fallback_delivery_analysis()
        
        return content_result, delivery_result
    
    async def _analyze_content(
        self,
        audio_data: bytes,
        mime_type: str,
        question: Dict[str, Any],
        workflow_id: str
    ) -> Dict[str, Any]:
        """Analyze content through transcription and evaluation."""
        try:
            # Step 1: Transcription
            transcription_result = await self.transcription_agent.transcribe_audio_bytes(
                audio_data, mime_type
            )
            
            if transcription_result["status"] != "success":
                return {
                    "status": "failed",
                    "stage": "transcription",
                    "error": transcription_result.get("error", "Transcription failed"),
                    "workflow_id": workflow_id
                }
            
            transcribed_text = transcription_result["transcribed_text"]
            
            # Step 2: Content Evaluation
            evaluation = await self.interview_manager.evaluate_answer(question, transcribed_text)
            
            # Add transcription metadata
            evaluation["transcription_metadata"] = {
                "original_text": transcribed_text,
                "word_count": len(transcribed_text.split()),
                "audio_processed": True,
                "validation": transcription_result.get("validation", {})
            }
            evaluation["status"] = "success"
            evaluation["workflow_id"] = workflow_id
            evaluation["analysis_type"] = "content"
            
            return evaluation
            
        except Exception as e:
            logger.error(f"Content analysis failed for workflow {workflow_id}: {str(e)}")
            return {
                "status": "failed",
                "stage": "content_analysis",
                "error": str(e),
                "workflow_id": workflow_id
            }
    
    async def _analyze_delivery(
        self,
        audio_data: bytes,
        mime_type: str,
        question: Dict[str, Any],
        workflow_id: str
    ) -> Dict[str, Any]:
        """Analyze speech delivery."""
        try:
            context = {
                "competency": question.get("competency"),
                "question_type": "interview_response",
                "workflow_id": workflow_id
            }
            
            delivery_analysis = await self.speech_coach_agent.analyze_speech_delivery(
                audio_data, mime_type, context
            )
            
            delivery_analysis["analysis_type"] = "delivery"
            delivery_analysis["workflow_id"] = workflow_id
            
            return delivery_analysis
            
        except Exception as e:
            logger.error(f"Delivery analysis failed for workflow {workflow_id}: {str(e)}")
            return self._generate_fallback_delivery_analysis(workflow_id, str(e))
    
    async def _synthesize_evaluations(
        self,
        content_analysis: Dict[str, Any],
        delivery_analysis: Dict[str, Any],
        question: Dict[str, Any],
        workflow_id: str
    ) -> Dict[str, Any]:
        """Synthesize content and delivery evaluations."""
        try:
            # Create synthesis session
            session_id = f"synthesis_{workflow_id}"
            session = await self.session_service.create_session(
                app_name=self.app_name,
                user_id="synthesis_user",
                session_id=session_id
            )
            
            # Prepare synthesis prompt
            synthesis_prompt = self._create_synthesis_prompt(
                content_analysis, delivery_analysis, question
            )
            
            content = Content(role="user", parts=[Part(text=synthesis_prompt)])
            
            # Run synthesis through ADK
            events = []
            async for event in self.runner.run_async(
                user_id="synthesis_user",
                session_id=session_id,
                new_message=content
            ):
                events.append(event)
            
            # Extract synthesis response
            synthesis_text = self._extract_final_response(events)
            
            # Parse synthesis into structured format
            synthesis_result = self._parse_synthesis_response(
                synthesis_text, content_analysis, delivery_analysis
            )
            
            synthesis_result["workflow_id"] = workflow_id
            return synthesis_result
            
        except Exception as e:
            logger.error(f"Synthesis failed for workflow {workflow_id}: {str(e)}")
            return self._generate_fallback_synthesis(content_analysis, delivery_analysis, workflow_id)
    
    def _create_synthesis_prompt(
        self,
        content_analysis: Dict[str, Any],
        delivery_analysis: Dict[str, Any],
        question: Dict[str, Any]
    ) -> str:
        """Create prompt for evaluation synthesis."""
        content_score = content_analysis.get('score', 0)
        delivery_score = delivery_analysis.get('overall_score', 0)
        competency = question.get('competency', 'General')
        
        return f"""
        Synthesize these parallel analyses into a comprehensive interview evaluation:
        
        QUESTION CONTEXT:
        - Competency: {competency}
        - Industry: {self.industry}
        - Position: {self.job_title}
        
        CONTENT ANALYSIS (What was said):
        - Score: {content_score}/10
        - Assessment: {content_analysis.get('overall_assessment', 'No assessment available')}
        - Key Strengths: {', '.join(content_analysis.get('strengths', [])[:3])}
        - Key Improvements: {', '.join(content_analysis.get('improvements', [])[:3])}
        
        DELIVERY ANALYSIS (How it was said):
        - Score: {delivery_score}/10
        - Assessment: {delivery_analysis.get('delivery_assessment', 'No assessment available')}
        - Speaking Strengths: {', '.join(delivery_analysis.get('strengths', [])[:3])}
        - Speaking Improvements: {', '.join(delivery_analysis.get('improvements', [])[:3])}
        
        SYNTHESIS TASK:
        Create a unified evaluation that considers both content quality and delivery effectiveness for {self.industry} interviews.
        
        Provide your synthesis in this EXACT format:
        
        Overall Interview Score: [Weighted score 0-10]/10
        
        Comprehensive Assessment: [3-4 sentences integrating content and delivery performance]
        
        COMBINED STRENGTHS:
        - [Strength combining content + delivery]
        - [Strength combining content + delivery]
        - [Strength combining content + delivery]
        
        PRIORITY IMPROVEMENTS:
        - [High impact improvement combining both areas]
        - [Medium impact improvement]
        - [Lower impact but valuable improvement]
        
        INDUSTRY-SPECIFIC FEEDBACK: [Specific guidance for {self.industry} interviews considering both content and delivery expectations]
        
        INTERVIEW READINESS: [Assessment of overall readiness for {self.industry} interviews]
        
        DEVELOPMENT PLAN: [Specific recommendations for continued improvement in both areas]
        
        Focus on creating actionable, integrated feedback that helps the candidate excel in both content and delivery for {self.industry} interviews.
        """
    
    def _parse_synthesis_response(
        self,
        synthesis_text: str,
        content_analysis: Dict[str, Any],
        delivery_analysis: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Parse synthesis response into structured format."""
        import re
        
        synthesis = {
            "overall_score": 5,
            "comprehensive_assessment": "",
            "combined_strengths": [],
            "priority_improvements": [],
            "industry_feedback": "",
            "interview_readiness": "",
            "development_plan": "",
            "component_scores": {
                "content_score": content_analysis.get('score', 0),
                "delivery_score": delivery_analysis.get('overall_score', 0)
            }
        }
        
        try:
            # Extract overall score
            score_match = re.search(r'Overall Interview Score:\s*(\d+(?:\.\d+)?)(?:/10)?', synthesis_text)
            if score_match:
                synthesis["overall_score"] = float(score_match.group(1))
            
            # Extract assessment
            assessment_match = re.search(r'Comprehensive Assessment:\s*(.*?)(?=\nCOMBINED STRENGTHS:|\Z)', synthesis_text, re.DOTALL)
            if assessment_match:
                synthesis["comprehensive_assessment"] = assessment_match.group(1).strip()
            
            # Extract lists
            for section_name, key in [
                ("COMBINED STRENGTHS", "combined_strengths"),
                ("PRIORITY IMPROVEMENTS", "priority_improvements")
            ]:
                section_match = re.search(f'{section_name}:(.*?)(?=\n[A-Z]|\Z)', synthesis_text, re.DOTALL)
                if section_match:
                    items = re.findall(r'-\s*(.*?)(?=\n\s*-|\n[A-Z]|\Z)', section_match.group(1), re.DOTALL)
                    synthesis[key] = [item.strip() for item in items if item.strip()]
            
            # Extract specific sections
            feedback_match = re.search(r'INDUSTRY-SPECIFIC FEEDBACK:\s*(.*?)(?=\nINTERVIEW READINESS:|\Z)', synthesis_text, re.DOTALL)
            if feedback_match:
                synthesis["industry_feedback"] = feedback_match.group(1).strip()
            
            readiness_match = re.search(r'INTERVIEW READINESS:\s*(.*?)(?=\nDEVELOPMENT PLAN:|\Z)', synthesis_text, re.DOTALL)
            if readiness_match:
                synthesis["interview_readiness"] = readiness_match.group(1).strip()
            
            plan_match = re.search(r'DEVELOPMENT PLAN:\s*(.*?)(?=\Z)', synthesis_text, re.DOTALL)
            if plan_match:
                synthesis["development_plan"] = plan_match.group(1).strip()
            
        except Exception as e:
            logger.error(f"Error parsing synthesis response: {str(e)}")
        
        return synthesis
    
    def _compile_enhanced_result(
        self,
        workflow_id: str,
        content_analysis: Dict[str, Any],
        delivery_analysis: Dict[str, Any],
        synthesis_result: Dict[str, Any],
        question: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Compile final enhanced evaluation result."""
        return {
            "workflow_id": workflow_id,
            "status": "success",
            "evaluation_type": "enhanced_voice_analysis",
            "question": question,
            
            # Primary evaluation (synthesis)
            "score": synthesis_result.get("overall_score", 5),
            "overall_assessment": synthesis_result.get("comprehensive_assessment", ""),
            "strengths": synthesis_result.get("combined_strengths", []),
            "improvements": synthesis_result.get("priority_improvements", []),
            "industry_feedback": synthesis_result.get("industry_feedback", ""),
            "interview_readiness": synthesis_result.get("interview_readiness", ""),
            "development_plan": synthesis_result.get("development_plan", ""),
            
            # Component analyses
            "content_analysis": {
                "score": content_analysis.get("score", 0),
                "assessment": content_analysis.get("overall_assessment", ""),
                "strengths": content_analysis.get("strengths", []),
                "improvements": content_analysis.get("improvements", []),
                "star_analysis": content_analysis.get("star_analysis", {}),
                "transcription_metadata": content_analysis.get("transcription_metadata", {})
            },
            
            "delivery_analysis": {
                "score": delivery_analysis.get("overall_score", 0),
                "assessment": delivery_analysis.get("delivery_assessment", ""),
                "strengths": delivery_analysis.get("strengths", []),
                "improvements": delivery_analysis.get("improvements", []),
                "detailed_scores": delivery_analysis.get("detailed_scores", {}),
                "coaching_tips": delivery_analysis.get("coaching_tips", []),
                "industry_advice": delivery_analysis.get("industry_advice", "")
            },
            
            # Metadata
            "competency": question.get("competency"),
            "workflow_metadata": {
                "parallel_analysis": True,
                "content_and_delivery": True,
                "industry": self.industry,
                "job_title": self.job_title,
                "audio_processed": True
            }
        }
    
    def _generate_fallback_delivery_analysis(self, workflow_id: str = None, error: str = "") -> Dict[str, Any]:
        """Generate fallback delivery analysis."""
        return {
            "overall_score": 5,
            "delivery_assessment": f"Delivery analysis unavailable. {error}" if error else "Delivery analysis temporarily unavailable.",
            "strengths": [f"Provided response for {self.industry} interview", "Attempted comprehensive answer"],
            "improvements": ["Focus on clear delivery", "Practice professional communication"],
            "coaching_tips": ["Practice speaking clearly", "Record yourself for self-assessment"],
            "industry_advice": f"For {self.industry} interviews, focus on clear, confident communication.",
            "detailed_scores": {},
            "workflow_id": workflow_id,
            "analysis_type": "delivery_fallback"
        }
    
    def _generate_fallback_synthesis(
        self,
        content_analysis: Dict[str, Any],
        delivery_analysis: Dict[str, Any],
        workflow_id: str
    ) -> Dict[str, Any]:
        """Generate fallback synthesis when ADK synthesis fails."""
        content_score = content_analysis.get('score', 0)
        delivery_score = delivery_analysis.get('overall_score', 0)
        
        # Simple weighted average
        overall_score = (content_score * 0.6) + (delivery_score * 0.4)
        
        return {
            "overall_score": overall_score,
            "comprehensive_assessment": f"Combined content and delivery analysis completed. Content scored {content_score}/10, delivery scored {delivery_score}/10.",
            "combined_strengths": (content_analysis.get('strengths', [])[:2] + delivery_analysis.get('strengths', [])[:1]),
            "priority_improvements": (content_analysis.get('improvements', [])[:2] + delivery_analysis.get('improvements', [])[:1]),
            "industry_feedback": f"For {self.industry} interviews, continue developing both content knowledge and professional delivery.",
            "interview_readiness": "Developing - continue practicing both content and delivery",
            "development_plan": "Practice regularly with focus on both technical content and clear communication delivery",
            "workflow_id": workflow_id,
            "component_scores": {
                "content_score": content_score,
                "delivery_score": delivery_score
            }
        }
    
    def _generate_error_result(self, workflow_id: str, stage: str, error_details: Any) -> Dict[str, Any]:
        """Generate error result for failed workflows."""
        return {
            "workflow_id": workflow_id,
            "status": "failed",
            "stage": stage,
            "error": str(error_details),
            "evaluation_type": "enhanced_voice_analysis_failed",
            "score": 0,
            "overall_assessment": f"Analysis failed at {stage} stage. Please try again.",
            "strengths": [],
            "improvements": ["Try recording again with clear audio", "Ensure stable internet connection"],
            "workflow_metadata": {
                "parallel_analysis": False,
                "error_stage": stage,
                "industry": self.industry
            }
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
    
    async def get_workflow_capabilities(self) -> Dict[str, Any]:
        """Get comprehensive workflow capabilities."""
        return {
            "workflow_type": "enhanced_voice_analysis",
            "parallel_analysis": True,
            "components": {
                "transcription_agent": {
                    "type": type(self.transcription_agent).__name__,
                    "capabilities": ["audio_transcription", "multimodal_processing"]
                },
                "speech_coach_agent": {
                    "type": type(self.speech_coach_agent).__name__,
                    "capabilities": ["delivery_analysis", "speaking_coaching", "industry_specific"]
                },
                "synthesis_agent": {
                    "type": "LlmAgent",
                    "capabilities": ["evaluation_synthesis", "comprehensive_assessment"]
                }
            },
            "analysis_dimensions": ["content_quality", "delivery_effectiveness"],
            "industry_optimization": self.industry,
            "job_specific": self.job_title,
            "supported_formats": ["audio/wav", "audio/mp3", "audio/webm"],
            "workflow_metrics": dict(self.workflow_metrics)
        }
    
    async def cleanup(self):
        """Cleanup enhanced workflow resources."""
        try:
            # Cleanup component agents if they have cleanup methods
            if hasattr(self.transcription_agent, 'cleanup'):
                await self.transcription_agent.cleanup()
            
            # Clear analysis cache
            self.analysis_cache.clear()
            
            logger.info("Enhanced voice workflow cleanup completed")
        except Exception as e:
            logger.warning(f"Cleanup warning: {str(e)}")


class StreamlinedEnhancedWorkflow:
    """
    Streamlined version for direct integration with existing UI.
    Maintains compatibility while adding delivery analysis.
    """
    
    def __init__(self, job_info: Dict[str, Any]):
        """Initialize streamlined enhanced workflow."""
        self.job_info = job_info
        self.transcription_agent = get_transcription_agent()
        self.speech_coach_agent = get_speech_coach_agent(job_info)
        self.interview_manager = InterviewManager(job_info)
        
        logger.info("Initialized StreamlinedEnhancedWorkflow")
    
    async def audio_to_enhanced_evaluation(
        self,
        question: Dict[str, Any],
        audio_data: bytes,
        mime_type: str = "audio/wav"
    ) -> Dict[str, Any]:
        """
        Direct pipeline: Audio → Parallel Analysis → Enhanced Evaluation.
        Returns enhanced evaluation compatible with existing UI.
        """
        try:
            # Run parallel analysis
            content_task = self._analyze_content_simple(question, audio_data, mime_type)
            delivery_task = self._analyze_delivery_simple(audio_data, mime_type, question)
            
            content_eval, delivery_eval = await asyncio.gather(
                content_task, delivery_task, return_exceptions=True
            )
            
            # Handle exceptions
            if isinstance(content_eval, Exception):
                raise Exception(f"Content analysis failed: {content_eval}")
            
            if isinstance(delivery_eval, Exception):
                logger.warning(f"Delivery analysis failed: {delivery_eval}")
                delivery_eval = {"overall_score": 5, "delivery_assessment": "Delivery analysis unavailable"}
            
            # Create enhanced evaluation
            enhanced_eval = self._combine_evaluations(content_eval, delivery_eval)
            
            return enhanced_eval
            
        except Exception as e:
            logger.error(f"Enhanced evaluation failed: {str(e)}")
            # Fallback to content-only evaluation
            try:
                transcription_result = await self.transcription_agent.transcribe_audio_bytes(audio_data, mime_type)
                if transcription_result["status"] == "success":
                    content_eval = await self.interview_manager.evaluate_answer(
                        question, transcription_result["transcribed_text"]
                    )
                    content_eval["enhanced_analysis"] = {
                        "content_analysis_available": True,
                        "delivery_analysis_available": False,
                        "error": str(e)
                    }
                    return content_eval
            except:
                pass
            
            # Ultimate fallback
            return {
                "score": 0,
                "overall_assessment": f"Enhanced analysis failed: {str(e)}",
                "competency": question.get("competency", "Unknown"),
                "error": str(e),
                "enhanced_analysis": {
                    "content_analysis_available": False,
                    "delivery_analysis_available": False,
                    "error": str(e)
                }
            }
    
    async def _analyze_content_simple(self, question: Dict[str, Any], audio_data: bytes, mime_type: str) -> Dict[str, Any]:
        """Simple content analysis."""
        transcription_result = await self.transcription_agent.transcribe_audio_bytes(audio_data, mime_type)
        if transcription_result["status"] != "success":
            raise Exception("Transcription failed")
        
        evaluation = await self.interview_manager.evaluate_answer(
            question, transcription_result["transcribed_text"]
        )
        evaluation["transcription_metadata"] = {
            "original_text": transcription_result["transcribed_text"],
            "word_count": len(transcription_result["transcribed_text"].split()),
            "audio_processed": True
        }
        return evaluation
    
    async def _analyze_delivery_simple(self, audio_data: bytes, mime_type: str, question: Dict[str, Any]) -> Dict[str, Any]:
        """Simple delivery analysis."""
        context = {"competency": question.get("competency"), "question_type": "interview_response"}
        return await self.speech_coach_agent.analyze_speech_delivery(audio_data, mime_type, context)
    
    def _combine_evaluations(self, content_eval: Dict[str, Any], delivery_eval: Dict[str, Any]) -> Dict[str, Any]:
        """Combine content and delivery evaluations."""
        content_score = content_eval.get('score', 0)
        delivery_score = delivery_eval.get('overall_score', 0)
        
        # Industry-weighted overall score
        industry = self.job_info.get('industry', 'technology')
        if industry in ['technology', 'finance', 'healthcare']:
            overall_score = (content_score * 0.7) + (delivery_score * 0.3)
        elif industry in ['sales', 'marketing']:
            overall_score = (content_score * 0.4) + (delivery_score * 0.6)
        else:
            overall_score = (content_score * 0.6) + (delivery_score * 0.4)
        
        # Enhanced evaluation with both analyses
        enhanced_eval = content_eval.copy()
        enhanced_eval.update({
            "score": round(overall_score, 1),
            "overall_assessment": f"Enhanced analysis: Content {content_score}/10, Delivery {delivery_score}/10. {content_eval.get('overall_assessment', '')}",
            
            # Add delivery insights to existing structure
            "enhanced_analysis": {
                "content_analysis_available": True,
                "delivery_analysis_available": True,
                "content_score": content_score,
                "delivery_score": delivery_score,
                "weighted_overall": overall_score,
                "delivery_strengths": delivery_eval.get('strengths', []),
                "delivery_improvements": delivery_eval.get('improvements', []),
                "speaking_tips": delivery_eval.get('coaching_tips', []),
                "industry_delivery_advice": delivery_eval.get('industry_advice', '')
            },
            
            # Merge strengths and improvements
            "strengths": (content_eval.get('strengths', [])[:2] + 
                         [f"Speaking: {s}" for s in delivery_eval.get('strengths', [])[:1]]),
            "improvements": (content_eval.get('improvements', [])[:2] + 
                           [f"Delivery: {i}" for i in delivery_eval.get('improvements', [])[:1]])
        })
        
        return enhanced_eval