"""
Fixed Interview Manager - Proper ADK Patterns
Uses correct session management and separates streaming from regular operations.
"""
import logging
import asyncio
import uuid
from typing import Dict, List, Any, Optional
from collections import defaultdict

from google.adk.agents import LlmAgent
from google.adk.tools import FunctionTool
from google.adk.runners import InMemoryRunner
from google.adk.sessions.in_memory_session_service import InMemorySessionService
from google.genai.types import Content, Part

from config import DEFAULT_MODEL, CORE_COMPETENCIES, ADK_CONFIG, VOICE_MODEL

logger = logging.getLogger(__name__)

class InterviewManager:
    """
    Fixed interview manager with proper ADK session management.
    Separates streaming (voice) from regular HTTP operations.
    """
    
    def __init__(self, job_info: Dict[str, Any]):
        """Initialize with proper session management."""
        self.job_info = job_info
        self.industry = job_info.get("industry", "technology")
        self.competencies = job_info.get("competencies", CORE_COMPETENCIES)
        
        # Single session service for the entire conversation
        self.session_service = InMemorySessionService()
        
        # Initialize competency agents
        self.competency_agents = {}
        self._initialize_competency_agents()
        
        # Create main coordinator
        self.coordinator = self._create_coordinator_agent()
        
        # Single runner for HTTP operations (non-streaming)
        self.http_runner = InMemoryRunner(
            app_name=f"{ADK_CONFIG['app_name_prefix']}_http",
            agent=self.coordinator
        )
        
        # Persistent session for conversation continuity
        self.conversation_session = None
        self.conversation_session_id = str(uuid.uuid4())
        
        # Progress tracking
        self.progress_data = defaultdict(list)
        
        logger.info(f"FixedInterviewManager initialized for {self.industry}")
    
    async def initialize_conversation_session(self):
        """Initialize persistent conversation session."""
        if not self.conversation_session:
            self.conversation_session = await self.session_service.create_session(
                app_name=f"{ADK_CONFIG['app_name_prefix']}_http",
                user_id="candidate",
                session_id=self.conversation_session_id
            )
            logger.info(f"Initialized conversation session: {self.conversation_session_id}")
    
    def _initialize_competency_agents(self):
        """Initialize specialized competency agents."""
        from agents.competency_agent import CompetencyAgent
        
        competency_descriptions = {
            "Problem Solving": "Expert in evaluating problem-solving approaches and analytical thinking",
            "Technical Expertise": "Specialist in technical skills, programming, and implementation knowledge",
            "Project Management": "Expert in project planning, organization, and delivery",
            "Analytical Thinking": "Specialist in data analysis, logical reasoning, and decision-making",
            "Attention to Detail": "Expert in quality assurance, precision, and error prevention",
            "Written Communication": "Specialist in clear writing, documentation, and communication",
            "Leadership": "Expert in team management, influence, and strategic thinking",
            "Teamwork": "Specialist in collaboration, team dynamics, and interpersonal skills"
        }
        
        shared_tools = [self._create_knowledge_tool()]
        
        for competency in self.competencies:
            description = competency_descriptions.get(
                competency,
                f"Specialist in {competency} for interview preparation"
            )
            
            self.competency_agents[competency] = CompetencyAgent(
                competency=competency,
                description=description,
                job_info=self.job_info,
                tools=shared_tools.copy()
            )
    
    def _create_knowledge_tool(self) -> FunctionTool:
        """Create job-specific knowledge tool."""
        def get_job_context(query: str) -> str:
            """Retrieve job-specific context for interview preparation."""
            context_parts = []
            
            # Add relevant job information based on query
            if "skills" in query.lower():
                context_parts.append(f"Required skills: {', '.join(self.job_info.get('skills', []))}")
            
            if "technologies" in query.lower() or "tech" in query.lower():
                context_parts.append(f"Technologies: {', '.join(self.job_info.get('technologies', []))}")
            
            if "responsibilities" in query.lower():
                context_parts.append(f"Key responsibilities: {'; '.join(self.job_info.get('responsibilities', [])[:3])}")
            
            # Always include basic context
            context_parts.append(f"Position: {self.job_info.get('title', 'Unknown')} in {self.industry}")
            context_parts.append(f"Experience level: {self.job_info.get('experience_level', 'Not specified')}")
            
            return " | ".join(context_parts)
        
        return FunctionTool(get_job_context)
    
    def _create_coordinator_agent(self) -> LlmAgent:
        """Create the main coordinator agent."""
        tools = [
            self._create_knowledge_tool(),
            self._create_progress_tool()
        ]
        
        coordinator_instruction = f"""
        You are an expert interview preparation coordinator for a {self.job_info.get('title', 'position')} 
        role in the {self.industry} industry.
        
        Your responsibilities:
        1. Help candidates prepare for interviews by providing guidance and practice
        2. Coordinate with specialized competency agents for detailed assessments
        3. Track progress and provide personalized recommendations
        4. Generate practice tests and evaluate performance
        
        Key competencies for this role: {', '.join(self.competencies)}
        
        Job context:
        - Title: {self.job_info.get('title', 'Unknown')}
        - Industry: {self.industry}
        - Experience level: {self.job_info.get('experience_level', 'Not specified')}
        - Key skills: {', '.join(self.job_info.get('skills', [])[:5])}
        - Technologies: {', '.join(self.job_info.get('technologies', [])[:5])}
        
        Always provide specific, actionable advice tailored to this role and industry.
        Be encouraging while maintaining professional standards.
        
        Focus on the content and quality of responses, regardless of input method.
        Provide clear, structured guidance for interview success.
        """
        
        # Convert competency agents to list for sub_agents
        competency_agent_list = [agent.agent for agent in self.competency_agents.values()]
        
        return LlmAgent(
            name="interview_coordinator",
            model="gemini-2.0-flash-live-001",  # Use Live API model for voice streaming
            description="Main coordinator for interview preparation",
            instruction=coordinator_instruction,
            tools=tools,
            sub_agents=competency_agent_list
        )
    
    def _create_progress_tool(self) -> FunctionTool:
        """Create progress tracking tool."""
        def track_progress(competency: str, score: float, notes: str = "") -> str:
            """Track progress for a specific competency."""
            import time
            self.progress_data[competency].append({
                "score": score,
                "timestamp": time.time(),
                "notes": notes
            })
            
            avg_score = sum(entry["score"] for entry in self.progress_data[competency]) / len(self.progress_data[competency])
            attempts = len(self.progress_data[competency])
            
            return f"Progress tracked for {competency}: Score {score}/10, Average: {avg_score:.1f}, Attempts: {attempts}"
        
        return FunctionTool(track_progress)
    
    async def answer_question(self, question: str, context: str = "") -> str:
        """
        Answer general interview preparation question via HTTP (non-streaming).
        """
        try:
            # Ensure conversation session is initialized
            await self.initialize_conversation_session()
            
            full_prompt = f"""
            Candidate question: {question}
            
            Additional context: {context}
            
            Please provide helpful, specific advice for interview preparation.
            If this relates to a specific competency, mention which competency agent 
            would be best suited for detailed practice.
            
            Focus on providing clear, actionable guidance based on the content of their question.
            """
            
            # Use persistent session for conversation continuity
            content = Content(role="user", parts=[Part(text=full_prompt)])
            
            # Use run_async for single-turn HTTP operations
            events = []
            async for event in self.http_runner.run_async(
                user_id="candidate",
                session_id=self.conversation_session_id,
                new_message=content
            ):
                events.append(event)
            
            response = self._extract_final_response(events)
            return response or "I'm here to help with interview preparation. Could you please rephrase your question?"
            
        except Exception as e:
            logger.error(f"Error answering question: {str(e)}")
            return f"I apologize, but I encountered an error processing your question. Please try again."
    
    async def generate_practice_question(
        self,
        competency: str,
        sub_competency: Optional[str] = None,
        difficulty: str = "balanced"
    ) -> Dict[str, Any]:
        """Generate practice question via HTTP (non-streaming)."""
        if competency not in self.competency_agents:
            raise ValueError(f"No agent available for competency: {competency}")
        
        agent = self.competency_agents[competency]
        question = await agent.generate_practice_question(sub_competency, difficulty)
        
        logger.info(f"Generated {difficulty} question for {competency}")
        return question
    
    async def evaluate_answer(
        self,
        question: Dict[str, Any],
        answer: str
    ) -> Dict[str, Any]:
        """
        Evaluate candidate's answer via HTTP (non-streaming).
        """
        competency = question.get("competency")
        if competency not in self.competency_agents:
            raise ValueError(f"No agent available for competency: {competency}")
        
        agent = self.competency_agents[competency]
        evaluation = await agent.evaluate_answer(question, answer)
        
        # Track progress
        score = evaluation.get("score", 0)
        await self._track_progress_async(competency, score, f"Question: {question.get('id', 'unknown')}")
        
        logger.info(f"Evaluated answer for {competency}, score: {score}/10")
        return evaluation
    
    async def generate_practice_test(self, num_questions: int = 6) -> List[Dict[str, Any]]:
        """Generate comprehensive practice test."""
        questions = []
        
        # Distribute questions across competencies
        competencies_to_use = self.competencies[:num_questions]
        if len(competencies_to_use) < num_questions:
            # Repeat competencies if needed
            competencies_to_use.extend(
                self.competencies[:num_questions - len(competencies_to_use)]
            )
        
        # Generate questions in parallel for efficiency
        tasks = []
        for competency in competencies_to_use:
            if competency in self.competency_agents:
                task = self.generate_practice_question(competency)
                tasks.append(task)
        
        if tasks:
            questions = await asyncio.gather(*tasks, return_exceptions=True)
            
            # Filter out any exceptions
            valid_questions = [q for q in questions if isinstance(q, dict)]
            
            logger.info(f"Generated practice test with {len(valid_questions)} questions")
            return valid_questions
        
        return []
    
    async def analyze_performance(self, evaluations: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze overall performance across multiple evaluations."""
        if not evaluations:
            return {"error": "No evaluations to analyze"}
        
        # Group by competency
        competency_scores = defaultdict(list)
        for eval_data in evaluations:
            competency = eval_data.get("competency")
            if competency and "score" in eval_data:
                competency_scores[competency].append(eval_data["score"])
        
        # Calculate statistics
        analysis = {
            "overall_score": 0,
            "competency_breakdown": {},
            "strengths": [],
            "weaknesses": [],
            "recommendations": [],
            "progress_trend": "stable"
        }
        
        all_scores = []
        for competency, scores in competency_scores.items():
            if scores:
                avg_score = sum(scores) / len(scores)
                all_scores.extend(scores)
                
                analysis["competency_breakdown"][competency] = {
                    "average_score": avg_score,
                    "attempts": len(scores),
                    "latest_score": scores[-1] if scores else 0,
                    "improvement": scores[-1] - scores[0] if len(scores) > 1 else 0
                }
                
                # Categorize strengths and weaknesses
                if avg_score >= 7:
                    analysis["strengths"].append(competency)
                elif avg_score < 5:
                    analysis["weaknesses"].append(competency)
        
        # Calculate overall score
        if all_scores:
            analysis["overall_score"] = sum(all_scores) / len(all_scores)
        
        # Generate recommendations
        analysis["recommendations"] = await self._generate_recommendations(analysis)
        
        logger.info(f"Performance analysis complete: Overall score {analysis['overall_score']:.1f}/10")
        return analysis
    
    async def _generate_recommendations(self, analysis: Dict[str, Any]) -> List[str]:
        """Generate personalized recommendations based on performance analysis."""
        recommendations = []
        
        # Recommendations for weaknesses
        for weakness in analysis["weaknesses"]:
            if weakness in self.competency_agents:
                agent = self.competency_agents[weakness]
                sub_comps = agent.sub_competencies
                if sub_comps:
                    recommendations.append(
                        f"Focus on improving {weakness}, particularly {sub_comps[0]} and {sub_comps[1] if len(sub_comps) > 1 else 'related skills'}"
                    )
                else:
                    recommendations.append(f"Practice more {weakness} questions to build confidence")
        
        # Recommendations for strengths
        if analysis["strengths"]:
            recommendations.append(
                f"Continue leveraging your strengths in {', '.join(analysis['strengths'][:2])} during interviews"
            )
        
        # Overall recommendations based on score
        overall_score = analysis["overall_score"]
        if overall_score < 5:
            recommendations.append("Consider taking more practice tests to build overall interview skills")
        elif overall_score < 7:
            recommendations.append("Focus on providing more specific examples and measurable results in your answers")
        else:
            recommendations.append("You're well-prepared! Practice mock interviews to maintain your skills")
        
        return recommendations
    
    async def _track_progress_async(self, competency: str, score: float, notes: str = ""):
        """Async version of progress tracking."""
        import time
        self.progress_data[competency].append({
            "score": score,
            "timestamp": time.time(),
            "notes": notes
        })
    
    def _extract_final_response(self, events: List[Any]) -> str:
        """Extract the final response text from ADK events."""
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
        
        return response
    
    def get_progress_summary(self) -> Dict[str, Any]:
        """Get progress summary across all competencies."""
        summary = {
            "competencies": {},
            "total_attempts": 0,
            "overall_trend": "no_data"
        }
        
        all_recent_scores = []
        all_early_scores = []
        
        for competency, entries in self.progress_data.items():
            if not entries:
                continue
                
            scores = [entry["score"] for entry in entries]
            summary["competencies"][competency] = {
                "average_score": sum(scores) / len(scores),
                "attempts": len(scores),
                "latest_score": scores[-1],
                "best_score": max(scores),
                "improvement": scores[-1] - scores[0] if len(scores) > 1 else 0
            }
            
            summary["total_attempts"] += len(scores)
            
            # Collect scores for trend analysis
            if len(scores) >= 2:
                all_recent_scores.append(scores[-1])
                all_early_scores.append(scores[0])
        
        # Calculate overall trend
        if all_recent_scores and all_early_scores:
            recent_avg = sum(all_recent_scores) / len(all_recent_scores)
            early_avg = sum(all_early_scores) / len(all_early_scores)
            
            if recent_avg > early_avg + 0.5:
                summary["overall_trend"] = "improving"
            elif recent_avg < early_avg - 0.5:
                summary["overall_trend"] = "declining"
            else:
                summary["overall_trend"] = "stable"
        
        return summary
    
    async def create_personalized_study_plan(self) -> Dict[str, Any]:
        """Create personalized study plan based on performance data."""
        progress = self.get_progress_summary()
        
        study_plan = {
            "focus_areas": [],
            "practice_schedule": {},
            "resources": {},
            "goals": {}
        }
        
        # Identify focus areas based on performance
        weak_competencies = []
        strong_competencies = []
        
        for competency, data in progress["competencies"].items():
            avg_score = data["average_score"]
            if avg_score < 6:
                weak_competencies.append((competency, avg_score))
            elif avg_score >= 7:
                strong_competencies.append((competency, avg_score))
        
        # Sort by score (weakest first)
        weak_competencies.sort(key=lambda x: x[1])
        
        # Set focus areas (prioritize weakest competencies)
        study_plan["focus_areas"] = [comp for comp, _ in weak_competencies[:3]]
        
        # Create practice schedule
        for competency in study_plan["focus_areas"]:
            if competency in self.competency_agents:
                agent = self.competency_agents[competency]
                study_plan["practice_schedule"][competency] = {
                    "sessions_per_week": 3,
                    "sub_competencies": agent.sub_competencies,
                    "difficulty_progression": ["easy", "balanced", "challenging"]
                }
        
        # Add maintenance for strong areas
        for competency, _ in strong_competencies[:2]:
            study_plan["practice_schedule"][competency] = {
                "sessions_per_week": 1,
                "focus": "maintenance",
                "difficulty_progression": ["challenging"]
            }
        
        # Set goals
        study_plan["goals"] = {
            "target_overall_score": 7.5,
            "timeline_weeks": 4,
            "weak_competency_target": 6.0,
            "practice_sessions_total": len(study_plan["focus_areas"]) * 3 * 4
        }
        
        return study_plan
    
    def export_progress_report(self) -> Dict[str, Any]:
        """Export comprehensive progress report."""
        progress = self.get_progress_summary()
        
        report = {
            "candidate_info": {
                "target_role": self.job_info.get("title", "Unknown"),
                "industry": self.industry,
                "preparation_date": "current_time"
            },
            "performance_summary": progress,
            "detailed_history": dict(self.progress_data),
            "competency_analysis": {},
            "system_info": {
                "adk_integration": True,
                "voice_streaming_available": True,
                "modern_architecture": True,
                "proper_session_management": True
            },
            "recommendations": []
        }
        
        # Detailed competency analysis
        for competency in self.competencies:
            if competency in progress["competencies"]:
                comp_data = progress["competencies"][competency]
                analysis = {
                    "readiness_level": self._assess_readiness_level(comp_data["average_score"]),
                    "key_strengths": [],
                    "improvement_areas": [],
                    "next_steps": []
                }
                
                # Determine readiness level and recommendations
                avg_score = comp_data["average_score"]
                if avg_score >= 8:
                    analysis["readiness_level"] = "Excellent - Interview Ready"
                    analysis["next_steps"].append("Maintain skills with periodic practice")
                elif avg_score >= 6:
                    analysis["readiness_level"] = "Good - Nearly Ready"
                    analysis["next_steps"].append("Practice challenging scenarios")
                elif avg_score >= 4:
                    analysis["readiness_level"] = "Developing - Needs Practice"
                    analysis["next_steps"].append("Focus on STAR method structure")
                else:
                    analysis["readiness_level"] = "Needs Significant Improvement"
                    analysis["next_steps"].append("Start with basic competency understanding")
                
                report["competency_analysis"][competency] = analysis
        
        return report
    
    def _assess_readiness_level(self, avg_score: float) -> str:
        """Assess interview readiness based on average score."""
        if avg_score >= 8:
            return "Excellent"
        elif avg_score >= 6:
            return "Good"
        elif avg_score >= 4:
            return "Developing"
        else:
            return "Needs Improvement"