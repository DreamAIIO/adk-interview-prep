"""
Competency Agent using Google ADK - Updated for voice streaming integration.
UPDATED: Streamlined for modern voice server integration, clean evaluations.
"""
import logging
import uuid
import random
from typing import Dict, List, Any, Optional
import asyncio

from google.adk.agents import LlmAgent
from google.adk.tools import FunctionTool
from google.adk.runners import Runner
from google.adk.sessions.in_memory_session_service import InMemorySessionService
from google.genai.types import Content, Part

from config import DEFAULT_MODEL, SCORE_THRESHOLDS, ADK_CONFIG

logger = logging.getLogger(__name__)

class CompetencyAgent:
    """
    Specialized agent for specific interview competencies using Google ADK.
    Updated for voice streaming integration via separate voice server.
    """
    
    def __init__(
        self,
        competency: str,
        description: str,
        job_info: Dict[str, Any],
        tools: Optional[List[Any]] = None
    ):
        """Initialize the competency agent with proper ADK patterns."""
        self.competency = competency
        self.description = description
        self.job_info = job_info
        self.industry = job_info.get("industry", "technology")
        self.job_title = job_info.get("title", "position")
        
        # Initialize tools
        if tools is None:
            tools = []
        tools.extend(self._create_competency_tools())
        
        # Create the ADK agent
        self.agent = LlmAgent(
            name=f"{competency.lower().replace(' ', '_')}_agent",
            model=DEFAULT_MODEL,
            description=f"Expert in {competency} for {self.industry} roles",
            instruction=self._generate_system_instruction(),
            tools=tools
        )
        
        # Proper app name for session service
        self.app_name = f"{ADK_CONFIG['app_name_prefix']}_{competency.lower().replace(' ', '_')}"
        
        # ADK session service and runner
        self.session_service = InMemorySessionService()
        self.runner = Runner(
            agent=self.agent,
            app_name=self.app_name,
            session_service=self.session_service
        )
        
        # Sub-competencies for this area
        self.sub_competencies = self._get_sub_competencies()
        
        logger.info(f"Initialized {competency} competency agent for {self.industry}")
    
    def _generate_system_instruction(self) -> str:
        """Generate system instruction for this competency agent."""
        return f"""
        You are an expert interview coach specializing in {self.competency} for {self.industry} roles.
        
        Your expertise focuses on {self.competency} within the context of this job:
        - Title: {self.job_title}
        - Industry: {self.industry}
        - Required Skills: {', '.join(self.job_info.get('skills', [])[:5])}
        - Technologies: {', '.join(self.job_info.get('technologies', [])[:5])}
        
        Your responsibilities:
        1. Create high-quality, job-specific interview questions for {self.competency}
        2. Evaluate candidate answers with detailed, constructive feedback
        3. Provide expert guidance on improving {self.competency} skills
        
        When creating questions:
        - Make them relevant to {self.industry} and the specific job
        - Structure them to encourage STAR method responses
        - Ensure they assess {self.competency} effectively
        - Include realistic scenarios from {self.industry}
        
        When evaluating answers:
        - Assess how well the candidate demonstrated {self.competency}
        - Provide specific, actionable feedback
        - Be constructive and encouraging while being honest
        - Focus on both content and structure (STAR method)
        - Do not mention or consider the input method (voice/text) used by the candidate
        - Evaluate solely based on the content and quality of the response
        
        Always maintain a professional, supportive tone while providing substantial value.
        Remember: Candidates may use voice or text input - focus only on their response content.
        """
    
    def _create_competency_tools(self) -> List[FunctionTool]:
        """Create tools specific to this competency."""
        def analyze_competency_context(query: str) -> str:
            """
            Analyze context specific to this competency area.
            
            Args:
                query: The analysis query
                
            Returns:
                Analysis results
            """
            competency_contexts = {
                "Problem Solving": "Focus on analytical approach, solution methodology, and outcome measurement",
                "Technical Expertise": "Evaluate technical depth, implementation skills, and best practices",
                "Project Management": "Assess planning, organization, stakeholder management, and delivery",
                "Analytical Thinking": "Review data interpretation, logical reasoning, and decision-making",
                "Attention to Detail": "Check thoroughness, quality assurance, and error prevention",
                "Written Communication": "Analyze clarity, structure, audience awareness, and effectiveness",
                "Leadership": "Evaluate team management, influence, and strategic thinking",
                "Teamwork": "Assess collaboration, communication, and team contribution"
            }
            
            context = competency_contexts.get(
                self.competency,
                "General competency analysis focusing on demonstration and application"
            )
            
            return f"Context for {self.competency} in {self.industry}: {context}. Query: {query}"
        
        return [FunctionTool(analyze_competency_context)]
    
    def _get_sub_competencies(self) -> List[str]:
        """Get sub-competencies for this main competency."""
        sub_competency_map = {
            "Problem Solving": [
                "Root Cause Analysis", "Solution Design", 
                "Implementation Planning", "Problem Prevention"
            ],
            "Technical Expertise": [
                "Technical Knowledge", "Implementation Skills",
                "Best Practices", "Technology Selection"
            ],
            "Project Management": [
                "Planning & Organization", "Timeline Management",
                "Resource Allocation", "Stakeholder Communication"
            ],
            "Analytical Thinking": [
                "Data Analysis", "Logical Reasoning",
                "Pattern Recognition", "Decision Making"
            ],
            "Attention to Detail": [
                "Quality Assurance", "Error Prevention",
                "Documentation", "Verification Processes"
            ],
            "Written Communication": [
                "Clarity & Structure", "Audience Awareness",
                "Technical Writing", "Persuasive Communication"
            ],
            "Leadership": [
                "Team Management", "Strategic Thinking",
                "Influence & Motivation", "Change Management"
            ],
            "Teamwork": [
                "Collaboration", "Communication",
                "Conflict Resolution", "Team Contribution"
            ]
        }
        
        return sub_competency_map.get(self.competency, [])
    
    async def generate_practice_question(
        self,
        sub_competency: Optional[str] = None,
        difficulty: str = "balanced"
    ) -> Dict[str, Any]:
        """
        Generate a practice question for this competency.
        """
        logger.info(f"Generating {difficulty} question for {self.competency}")
        
        # Build prompt for question generation
        sub_focus = f", specifically focusing on {sub_competency}" if sub_competency else ""
        
        prompt = f"""
        Create a high-quality interview question for {self.competency}{sub_focus} 
        for a {self.job_title} position in the {self.industry} industry.
        
        Job Context:
        - Skills needed: {', '.join(self.job_info.get('skills', [])[:3])}
        - Technologies: {', '.join(self.job_info.get('technologies', [])[:3])}
        - Experience level: {self.job_info.get('experience_level', 'Mid-level')}
        
        Requirements:
        - Question should encourage a STAR method response
        - Difficulty level: {difficulty}
        - Must be specific to {self.industry} and realistic
        - Should clearly assess {self.competency} skills
        - Consider that candidates may respond via voice or text input
        
        Provide your response in this exact format:
        
        Question: [Your interview question here]
        
        Expected Answer Guidelines: [What a strong answer should include using STAR method]
        
        Evaluation Criteria: [How to assess the response - specific criteria for {self.competency}]
        
        Sub-Competency: {sub_competency or "General"}
        """
        
        try:
            # Create session BEFORE calling run_async
            user_id = "question_generator"
            session_id = f"gen_{uuid.uuid4().hex[:8]}"
            
            # Create session through session service
            session = await self.session_service.create_session(
                app_name=self.app_name,
                user_id=user_id,
                session_id=session_id
            )
            
            logger.info(f"Created session: {session.id} for app: {self.app_name}")
            
            # Format prompt as Content object
            content = Content(role="user", parts=[Part(text=prompt)])
            
            # Use Runner's run_async method with created session
            events = []
            async for event in self.runner.run_async(
                user_id=user_id,
                session_id=session_id,
                new_message=content
            ):
                events.append(event)
                logger.debug(f"Received event: {type(event).__name__}")
            
            # Extract response from final event
            response = self._extract_final_response(events)
            logger.info(f"Generated response length: {len(response)}")
            
            # Parse the response
            question_data = self._parse_question_response(response, sub_competency, difficulty)
            
            return question_data
            
        except Exception as e:
            logger.error(f"Error generating question: {str(e)}")
            return self._generate_fallback_question(sub_competency, difficulty)
    
    async def evaluate_answer(
        self,
        question: Dict[str, Any],
        answer: str
    ) -> Dict[str, Any]:
        """
        Evaluate a candidate's answer to a practice question.
        Note: Input method (voice/text) is handled by UI layer - focus only on content.
        """
        logger.info(f"Evaluating answer for {self.competency}")
        
        prompt = f"""
        Evaluate this candidate's interview answer for a {self.competency} question 
        in the context of a {self.job_title} position.
        
        QUESTION:
        {question.get('question', '')}
        
        CANDIDATE'S ANSWER:
        {answer}
        
        EVALUATION CONTEXT:
        - Competency being assessed: {self.competency}
        - Industry: {self.industry}
        - Sub-competency focus: {question.get('sub_competency', 'General')}
        - Expected answer guidelines: {question.get('expected_answer', '')}
        
        IMPORTANT: Focus solely on the content and quality of the answer. 
        Do not consider or mention how the answer was provided (voice vs text input).
        Evaluate based on content, structure, examples, and demonstration of competency.
        
        Please provide a comprehensive evaluation in this exact format:
        
        Score: [0-10]/10
        
        Overall Assessment: [2-3 sentences explaining the overall performance]
        
        STAR Method Analysis:
        - Situation: [How well they described the situation]
        - Task: [How well they explained their responsibilities]
        - Action: [Quality of actions described]
        - Result: [Effectiveness of results shared]
        
        Strengths:
        - [Specific strength 1]
        - [Specific strength 2]
        - [Specific strength 3]
        
        Areas for Improvement:
        - [Specific improvement area 1]
        - [Specific improvement area 2]
        - [Specific improvement area 3]
        
        Missing Elements:
        - [Key element missing from answer 1]
        - [Key element missing from answer 2]
        
        Advice for Improvement: [Specific guidance on how to improve this answer]
        
        Sample Strong Answer: [Provide a brief example of what a strong answer would include]
        """
        
        try:
            # Create session BEFORE calling run_async
            user_id = "answer_evaluator"
            session_id = f"eval_{uuid.uuid4().hex[:8]}"
            
            # Create session through session service
            session = await self.session_service.create_session(
                app_name=self.app_name,
                user_id=user_id,
                session_id=session_id
            )
            
            logger.info(f"Created evaluation session: {session.id}")
            
            # Format prompt as Content object
            content = Content(role="user", parts=[Part(text=prompt)])
            
            # Use Runner's run_async method with created session
            events = []
            async for event in self.runner.run_async(
                user_id=user_id,
                session_id=session_id,
                new_message=content
            ):
                events.append(event)
            
            # Extract response from final event
            response = self._extract_final_response(events)
            
            # Parse the evaluation response
            evaluation = self._parse_evaluation_response(response, answer)
            
            return evaluation
            
        except Exception as e:
            logger.error(f"Error evaluating answer: {str(e)}")
            return self._generate_fallback_evaluation(answer)
    
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
        
        return response or "No response generated"
    
    def _parse_question_response(
        self,
        response: str,
        sub_competency: Optional[str],
        difficulty: str
    ) -> Dict[str, Any]:
        """Parse the agent's response into structured question data."""
        import re
        
        question_data = {
            "id": str(uuid.uuid4()),
            "competency": self.competency,
            "sub_competency": sub_competency or "",
            "difficulty": difficulty,
            "question": "",
            "expected_answer": "",
            "evaluation_criteria": "",
            "industry": self.industry,
            "job_title": self.job_title
        }
        
        try:
            logger.debug(f"Parsing response: {response[:200]}...")
            
            # Simple and robust regex patterns
            # Extract question
            question_match = re.search(r'Question:\s*(.*?)(?=\n.*?:|\Z)', response, re.DOTALL)
            if question_match:
                question_text = question_match.group(1).strip()
                question_text = re.sub(r'\n+', ' ', question_text)
                if len(question_text) > 20:
                    question_data["question"] = question_text
            
            # Extract expected answer guidelines
            expected_match = re.search(r'Expected Answer Guidelines:\s*(.*?)(?=\n.*?:|\Z)', response, re.DOTALL)
            if expected_match:
                expected_text = expected_match.group(1).strip()
                question_data["expected_answer"] = expected_text
            
            # Extract evaluation criteria
            criteria_match = re.search(r'Evaluation Criteria:\s*(.*?)(?=\n.*?:|\Z)', response, re.DOTALL)
            if criteria_match:
                criteria_text = criteria_match.group(1).strip()
                question_data["evaluation_criteria"] = criteria_text
            
            # Log what we extracted
            logger.info(f"Extracted question: {question_data['question'][:100]}...")
            
            # Ensure we have a valid question
            if not question_data["question"] or len(question_data["question"]) < 20:
                logger.warning("Failed to extract valid question, using fallback")
                return self._generate_fallback_question(sub_competency, difficulty)
                
        except Exception as e:
            logger.error(f"Error parsing question response: {str(e)}")
            return self._generate_fallback_question(sub_competency, difficulty)
        
        return question_data
    
    def _parse_evaluation_response(self, response: str, original_answer: str) -> Dict[str, Any]:
        """Parse the agent's evaluation response."""
        import re
        
        evaluation = {
            "score": 5,
            "overall_assessment": "",
            "star_analysis": {
                "situation": "",
                "task": "",
                "action": "",
                "result": ""
            },
            "strengths": [],
            "improvements": [],
            "missing_elements": [],
            "advice": "",
            "sample_answer": "",
            "competency": self.competency,
            "original_answer": original_answer
        }
        
        try:
            # Extract score
            score_match = re.search(r'Score:\s*(\d+)(?:/10)?', response)
            if score_match:
                evaluation["score"] = int(score_match.group(1))
            
            # Extract overall assessment
            assessment_match = re.search(r'Overall Assessment:\s*(.*?)(?=\n.*?:|\Z)', response, re.DOTALL)
            if assessment_match:
                evaluation["overall_assessment"] = assessment_match.group(1).strip()
            
            # Extract STAR analysis
            star_section = re.search(r'STAR Method Analysis:(.*?)(?=\nStrengths:|\Z)', response, re.DOTALL)
            if star_section:
                star_text = star_section.group(1)
                
                for component in ["situation", "task", "action", "result"]:
                    pattern = f'{component.title()}:\s*(.*?)(?=\n\s*-|\n[A-Z]|\Z)'
                    match = re.search(pattern, star_text, re.DOTALL | re.IGNORECASE)
                    if match:
                        evaluation["star_analysis"][component] = match.group(1).strip()
            
            # Extract lists (strengths, improvements, missing elements)
            for section_name, key in [
                ("Strengths", "strengths"),
                ("Areas for Improvement", "improvements"),
                ("Missing Elements", "missing_elements")
            ]:
                section_match = re.search(f'{section_name}:(.*?)(?=\n[A-Z]|\Z)', response, re.DOTALL)
                if section_match:
                    items = re.findall(r'-\s*(.*?)(?=\n\s*-|\n[A-Z]|\Z)', section_match.group(1), re.DOTALL)
                    evaluation[key] = [item.strip() for item in items if item.strip()]
            
            # Extract advice
            advice_match = re.search(r'Advice for Improvement:\s*(.*?)(?=\nSample Strong Answer:|\Z)', response, re.DOTALL)
            if advice_match:
                evaluation["advice"] = advice_match.group(1).strip()
            
            # Extract sample answer
            sample_match = re.search(r'Sample Strong Answer:\s*(.*?)(?=\Z)', response, re.DOTALL)
            if sample_match:
                evaluation["sample_answer"] = sample_match.group(1).strip()
        
        except Exception as e:
            logger.error(f"Error parsing evaluation: {str(e)}")
        
        return evaluation
    
    def _generate_fallback_question(
        self,
        sub_competency: Optional[str],
        difficulty: str
    ) -> Dict[str, Any]:
        """Generate a fallback question when AI generation fails."""
        
        # Industry-specific question templates
        templates = {
            "technology": {
                "Problem Solving": "Describe a time when you debugged a complex technical issue in a {job_title} role. What was your systematic approach?",
                "Technical Expertise": "Tell me about a challenging technical implementation you completed. What technologies did you use and why?",
                "Project Management": "Walk me through how you managed a software project from conception to deployment.",
                "Analytical Thinking": "Describe a situation where you had to analyze data or metrics to make a technical decision.",
                "Attention to Detail": "Give me an example of when your attention to detail prevented a significant technical problem.",
                "Written Communication": "Tell me about a time you had to write technical documentation for different audiences.",
                "Leadership": "Describe how you led a technical team through a challenging project or change.",
                "Teamwork": "Share an example of successful collaboration on a technical project with multiple stakeholders."
            },
            "marketing": {
                "Problem Solving": "Describe a time when a marketing campaign wasn't performing as expected. How did you identify and solve the problem?",
                "Technical Expertise": "Tell me about a time you had to adapt your design skills to meet specific technical requirements for a marketing platform.",
                "Project Management": "Walk me through how you managed a complex marketing campaign from concept to launch.",
                "Analytical Thinking": "Describe a situation where you had to analyze campaign data to make strategic design decisions.",
                "Attention to Detail": "Give me an example of when your attention to detail was crucial in a marketing project.",
                "Written Communication": "Tell me about a time you had to explain a complex design concept to stakeholders with limited design knowledge.",
                "Leadership": "Describe how you led a creative team through a challenging marketing project.",
                "Teamwork": "Share an example of successful collaboration on a marketing campaign with multiple stakeholders."
            }
        }
        
        # Get template for industry and competency
        industry_templates = templates.get(self.industry, templates["technology"])
        template = industry_templates.get(self.competency, 
            f"Tell me about a time when you demonstrated {self.competency} in your {self.industry} work.")
        
        question = template.format(job_title=self.job_title)
        
        return {
            "id": str(uuid.uuid4()),
            "competency": self.competency,
            "sub_competency": sub_competency or "",
            "difficulty": difficulty,
            "question": question,
            "expected_answer": f"A strong answer should follow the STAR method and clearly demonstrate {self.competency} skills relevant to {self.industry}.",
            "evaluation_criteria": f"Evaluate based on: 1) Clear demonstration of {self.competency}, 2) STAR method structure, 3) Relevance to {self.industry}, 4) Specific examples and outcomes.",
            "industry": self.industry,
            "job_title": self.job_title
        }
    
    def _generate_fallback_evaluation(self, answer: str) -> Dict[str, Any]:
        """Generate a basic evaluation when AI evaluation fails."""
        # Simple scoring based on answer length and STAR keywords
        score = 5  # Base score
        
        if len(answer.split()) > 100:
            score += 1  # Substantial answer
        
        star_keywords = ["situation", "task", "action", "result", "when", "what", "how", "outcome"]
        star_count = sum(1 for keyword in star_keywords if keyword.lower() in answer.lower())
        
        if star_count >= 4:
            score += 2
        elif star_count >= 2:
            score += 1
        
        return {
            "score": min(score, 8),  # Cap at 8 for fallback
            "overall_assessment": f"Your answer demonstrates some understanding of {self.competency}. Consider providing more specific details and following the STAR method structure.",
            "star_analysis": {
                "situation": "Partially described" if "situation" in answer.lower() else "Could be clearer",
                "task": "Some task description" if any(word in answer.lower() for word in ["task", "responsible", "role"]) else "Needs more detail",
                "action": "Actions mentioned" if any(word in answer.lower() for word in ["did", "action", "approach"]) else "Could be more specific",
                "result": "Results discussed" if any(word in answer.lower() for word in ["result", "outcome", "achieved"]) else "Needs measurable outcomes"
            },
            "strengths": [
                f"Shows understanding of {self.competency}",
                "Provided a relevant example",
                "Demonstrates practical experience"
            ],
            "improvements": [
                "Use more specific details and examples",
                "Follow STAR method structure more clearly",
                "Include quantifiable results and outcomes"
            ],
            "missing_elements": [
                "More detailed situation context",
                "Clearer explanation of specific actions taken",
                "Measurable results and impact"
            ],
            "advice": f"To improve your {self.competency} answers, focus on providing a clear STAR structure with specific details about the situation, your role, the actions you took, and the measurable results achieved.",
            "sample_answer": f"A strong {self.competency} answer would include: a specific situation from your {self.industry} experience, your clear role and responsibilities, detailed actions you took that demonstrate {self.competency}, and measurable outcomes that show the impact of your work.",
            "competency": self.competency,
            "original_answer": answer
        }