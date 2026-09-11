#type: ignore
"""
CV Snap - Gemini AI Service
Handles all AI-powered analysis using Google's Gemini API
"""

from google import genai
import json
import logging
from typing import Dict, Any, Optional
import os
from dotenv import load_dotenv

from ai_service import AIService, JobRequirements, CandidateProfile

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

GEMINI_MODEL = "gemini-1.5-flash-8b"

class GeminiProvider(AIService):
    """Service class for Gemini AI operations"""
    
    def __init__(self):
        self.api_key = os.getenv("GOOGLE_API_KEY")
        if not self.api_key:
            raise ValueError("GOOGLE_API_KEY not found in environment variables")
        
        self.client = genai.Client(api_key=self.api_key)
        logger.info("Gemini AI service initialized successfully")
    
    def extract_job_requirements(self, job_description: str) -> Dict[str, Any]:
        """Extract structured job requirements"""
        prompt = f"""Analyze this job description and extract structured information.

Job Description:
{job_description}

SKILL NORMALIZATION:
Use these EXACT canonical names for skills: "react.js", "node.js", "express.js", "next.js", "vue.js", "javascript", "typescript", "python", "postgresql", "mongodb", "aws", "gcp", "kubernetes", "docker", "ci/cd", "machine-learning", "tailwind-css", "spring-boot"

IMPORTANCE SCORING (1-10):
- 10: Core requirement, in title, "must have"
- 8-9: Very important
- 6-7: Important supporting skills
- 4-5: Nice to have, "preferred"
- 1-3: Barely mentioned

Extract all skills and separate them into required_skills and preferred_skills.
"""
        try:
            response = self.client.models.generate_content(
                model=GEMINI_MODEL,
                contents=prompt,
                config={
                    "response_mime_type": "application/json",
                    "response_schema": JobRequirements,
                }
            )
            job_data = json.loads(response.text)
            job_data = self._validate_and_enhance_job_data(job_data)
            return job_data
        except Exception as e:
            logger.error(f"Structured job extraction failed: {str(e)}")
            return self._fallback_job_extraction(job_description)

    def extract_candidate_profile(self, resume_text: str, filename: str = "") -> Dict[str, Any]:
        """Extract structured candidate profile"""
        prompt = f"""Extract candidate information from this resume.

Resume Text:
{resume_text}

CRITICAL EXTRACTION RULES:
1. ALWAYS find the person's actual name
2. Use EXACT canonical skill names (e.g. "react.js", "python", "kubernetes")
3. Provide evidence for each skill
4. Calculate years_experience accurately (Current year is 2026)
5. Leadership indicators: "Led team", "Senior", "Managed"
6. EDUCATION extraction: Extract degree type, field, institution, and year. If no formal education section exists, set education to empty list.
"""
        try:
            response = self.client.models.generate_content(
                model=GEMINI_MODEL,
                contents=prompt,
                config={
                    "response_mime_type": "application/json",
                    "response_schema": CandidateProfile,
                }
            )
            candidate_data = json.loads(response.text)
            candidate_data['filename'] = filename
            candidate_data = self._validate_and_enhance_candidate_data(candidate_data)
            return candidate_data
        except Exception as e:
            logger.error(f"Structured candidate extraction failed for {filename}: {str(e)}")
            return self._fallback_candidate_extraction(resume_text, filename)
            
    def generate_match_explanation(self, candidate_data: Dict[str, Any], 
                                  job_data: Dict[str, Any], 
                                  match_analysis: Dict[str, Any]) -> str:
        matched_skills = match_analysis.get('matched_skill_names', [])
        missing_skills = match_analysis.get('missing_skill_names', [])
        
        prompt = f"""Generate a professional 2-3 sentence explanation for this candidate-job match.

Candidate: {candidate_data.get('name', 'Unknown')}
Total Experience: {candidate_data.get('total_years_experience', 0)} years
Candidate Skills: {[s.get('name') for s in candidate_data.get('skills', [])][:15]}

Job Title: {job_data.get('title', 'Unknown')}
Required Experience: {job_data.get('min_years_experience', 0)} years

Match Score: {match_analysis.get('match_score', 0):.1f}%
Skills Matched: {matched_skills}
Skills Missing: {missing_skills}

Cover key strengths, missing skills, and a brief recommendation."""
        try:
            response = self.client.models.generate_content(
                model=GEMINI_MODEL,
                contents=prompt,
            )
            explanation = response.text.strip()
            score = match_analysis.get('match_score', 0)
            if score >= 80: category = "Strong Match"
            elif score >= 60: category = "Potential Match"
            else: category = "Weak Match"
            return f"**{category} ({score:.1f}%):** {explanation}"
        except Exception as e:
            logger.error(f"Explanation generation failed: {str(e)}")
            return self._generate_fallback_explanation(candidate_data, job_data, match_analysis)
