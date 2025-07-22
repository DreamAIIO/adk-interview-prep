"""
Job Description Analyzer using Google ADK.
Extracts key information and competencies from job descriptions.
"""
import re
import logging
from typing import Dict, List, Any, Optional
from collections import Counter
import google.generativeai as genai

from config import GOOGLE_API_KEY, DEFAULT_MODEL, INDUSTRY_KEYWORDS, CORE_COMPETENCIES

logger = logging.getLogger(__name__)

class JobAnalyzer:
    """Analyzes job descriptions to extract structured information."""
    
    def __init__(self):
        """Initialize the job analyzer."""
        genai.configure(api_key=GOOGLE_API_KEY)
        self.model = genai.GenerativeModel(DEFAULT_MODEL)
        logger.info("JobAnalyzer initialized")
    
    def analyze_job_description(self, job_description: str) -> Dict[str, Any]:
        """
        Analyze a job description and extract structured information.
        
        Args:
            job_description: The job description text
            
        Returns:
            Structured job information dictionary
        """
        logger.info("Starting job description analysis")
        
        # Basic extraction using regex
        basic_info = self._extract_basic_info(job_description)
        
        # AI-powered analysis using Gemini
        ai_analysis = self._ai_analyze_job(job_description)
        
        # Determine industry
        industry = self._determine_industry(job_description, basic_info)
        
        # Extract competencies
        competencies = self._extract_competencies(job_description, ai_analysis)
        
        # Combine all information
        job_info = {
            **basic_info,
            **ai_analysis,
            "industry": industry,
            "competencies": competencies,
            "full_description": job_description
        }
        
        # Defensive: ensure job_info is a dict and has required keys
        required_keys = ["title", "industry", "competencies", "skills", "technologies"]
        for key in required_keys:
            if key not in job_info:
                job_info[key] = "" if key in ["title", "industry"] else []
        
        logger.info(f"Job analysis complete for: {job_info.get('title', 'Unknown position')}")
        return job_info
    
    def _extract_basic_info(self, text: str) -> Dict[str, Any]:
        """Extract basic information using regex patterns."""
        info = {
            "title": "",
            "company": "",
            "location": "",
            "experience_level": "",
            "skills": [],
            "technologies": []
        }
        
        # Extract title (usually first line or after # markdown)
        title_patterns = [
            r'^#\s*(.+?)$',  # Markdown header
            r'^(.+?)(?:\n|$)',  # First line
            r'(?:position|role|job):\s*(.+?)(?:\n|$)'  # Position: format
        ]
        
        for pattern in title_patterns:
            match = re.search(pattern, text, re.MULTILINE | re.IGNORECASE)
            if match:
                info["title"] = match.group(1).strip()
                break
        
        # Extract company
        company_patterns = [
            r'(?:at|for|with)\s+([A-Za-z0-9\s\.&\'-]+?)(?:\s+(?:in|is|has|we|our))',
            r'company:\s*(.+?)(?:\n|$)',
            r'about\s+(.+?)(?:\n|$)'
        ]
        
        for pattern in company_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                company = match.group(1).strip()
                if len(company) < 50:  # Reasonable company name length
                    info["company"] = company
                    break
        
        # Extract experience level
        exp_patterns = [
            r'(\d+)\+?\s*years?\s*(?:of\s*)?experience',
            r'experience[:\s]*(\d+)\+?\s*years?',
            r'minimum\s*(?:of\s*)?(\d+)\+?\s*years?'
        ]
        
        for pattern in exp_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                years = match.group(1)
                info["experience_level"] = f"{years}+ years"
                break
        
        # Extract technologies
        tech_keywords = [
            "Python", "Java", "JavaScript", "React", "Node.js", "AWS", "Docker", 
            "Kubernetes", "SQL", "NoSQL", "MongoDB", "PostgreSQL", "Git", "Linux",
            "Django", "Flask", "FastAPI", "Angular", "Vue", "TypeScript", "Go",
            "Rust", "C++", "C#", "Ruby", "PHP", "Swift", "Kotlin", "Azure", "GCP"
        ]
        
        found_techs = []
        for tech in tech_keywords:
            if re.search(r'\b' + re.escape(tech) + r'\b', text, re.IGNORECASE):
                found_techs.append(tech)
        
        info["technologies"] = found_techs
        
        return info
    
    def _ai_analyze_job(self, job_description: str) -> Dict[str, Any]:
        """Use AI to analyze the job description."""
        prompt = f"""
        Analyze this job description and extract the following information in JSON format:
        
        Job Description:
        {job_description}
        
        Please extract:
        1. responsibilities: List of main job responsibilities
        2. requirements: List of key requirements
        3. qualifications: List of educational/experience qualifications
        4. skills: List of required skills
        5. benefits: List of benefits mentioned (if any)
        6. remote_work: Boolean indicating if remote work is mentioned
        7. salary_range: Salary range if mentioned (or null)
        
        Return only valid JSON without any markdown formatting.
        """
        
        try:
            response = self.model.generate_content(prompt)
            # Clean up the response to extract JSON
            text = response.text.strip()
            
            # Remove markdown code blocks if present
            if text.startswith("```"):
                text = re.sub(r'^```(?:json)?\n?', '', text)
                text = re.sub(r'\n?```$', '', text)
            
            # Try to parse JSON
            import json
            ai_info = json.loads(text)
            
            # Ensure all required keys exist
            default_structure = {
                "responsibilities": [],
                "requirements": [],
                "qualifications": [],
                "skills": [],
                "benefits": [],
                "remote_work": False,
                "salary_range": None
            }
            
            for key, default_value in default_structure.items():
                if key not in ai_info:
                    ai_info[key] = default_value
            
            return ai_info
            
        except Exception as e:
            logger.error(f"Error in AI analysis: {str(e)}")
            # Return default structure on error
            return {
                "responsibilities": [],
                "requirements": [],
                "qualifications": [],
                "skills": [],
                "benefits": [],
                "remote_work": False,
                "salary_range": None
            }
    
    def _determine_industry(self, text: str, basic_info: Dict[str, Any]) -> str:
        """Determine the most likely industry."""
        text_lower = text.lower()
        title_lower = basic_info.get("title", "").lower()
        
        # Score each industry
        industry_scores = Counter()
        
        for industry, keywords in INDUSTRY_KEYWORDS.items():
            score = 0
            for keyword in keywords:
                # Higher weight for title matches
                if keyword.lower() in title_lower:
                    score += 3
                # Regular weight for description matches
                if keyword.lower() in text_lower:
                    score += 1
            
            if score > 0:
                industry_scores[industry] = score
        
        # Return the highest scoring industry or default to technology
        if industry_scores:
            return industry_scores.most_common(1)[0][0]
        return "technology"
    
    def _extract_competencies(self, text: str, ai_analysis: Dict[str, Any]) -> List[str]:
        """Extract relevant competencies for the role."""
        text_lower = text.lower()
        
        # Competency keywords mapping
        competency_keywords = {
            "Problem Solving": ["problem", "solve", "troubleshoot", "debug", "resolve", "solution"],
            "Technical Expertise": ["technical", "development", "programming", "coding", "engineering"],
            "Project Management": ["project", "manage", "timeline", "deadline", "coordinate", "plan"],
            "Analytical Thinking": ["analyze", "data", "insight", "research", "evaluate", "assess"],
            "Attention to Detail": ["detail", "quality", "accuracy", "precision", "thorough", "careful"],
            "Written Communication": ["communication", "document", "write", "report", "present"],
            "Leadership": ["lead", "manage", "mentor", "guide", "direct", "supervise"],
            "Teamwork": ["team", "collaborate", "cooperation", "work with others"]
        }
        
        # Score each competency
        competency_scores = Counter()
        
        for competency, keywords in competency_keywords.items():
            score = 0
            for keyword in keywords:
                if keyword in text_lower:
                    score += text_lower.count(keyword)
            
            # Also check AI-extracted information
            ai_text = " ".join(
                ai_analysis.get("responsibilities", []) +
                ai_analysis.get("requirements", []) +
                ai_analysis.get("skills", [])
            ).lower()
            
            for keyword in keywords:
                if keyword in ai_text:
                    score += ai_text.count(keyword)
            
            if score > 0:
                competency_scores[competency] = score
        
        # Return top competencies, ensuring we have at least the core ones
        selected_competencies = [comp for comp, _ in competency_scores.most_common(6)]
        
        # Ensure we have essential competencies
        essential = ["Problem Solving", "Technical Expertise", "Analytical Thinking"]
        for essential_comp in essential:
            if essential_comp not in selected_competencies:
                selected_competencies.append(essential_comp)
        
        return selected_competencies[:8]  # Limit to 8 competencies