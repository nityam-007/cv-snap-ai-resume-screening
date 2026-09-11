import os
import json
import logging
import time
from typing import Dict, Any
from openai import OpenAI
from dotenv import load_dotenv

from ai_service import AIService

load_dotenv()
logger = logging.getLogger(__name__)

class GroqProvider(AIService):
    def __init__(self):
        self.api_key = os.getenv("GROQ_API_KEY")
        if not self.api_key:
            raise ValueError("GROQ_API_KEY not found in environment variables")
        self.client = OpenAI(
            api_key=self.api_key,
            base_url="https://api.groq.com/openai/v1"
        )
        self.model = "llama-3.1-8b-instant"
        logger.info("Groq AI service initialized successfully")

    def _call_with_retry(self, messages, response_format=None, max_retries=3):
        for attempt in range(max_retries):
            try:
                kwargs = {
                    "model": self.model,
                    "messages": messages,
                }
                if response_format:
                    kwargs["response_format"] = response_format
                response = self.client.chat.completions.create(**kwargs)
                return response.choices[0].message.content
            except Exception as e:
                # Basic rate limit check
                if "429" in str(e) or (hasattr(e, 'status_code') and e.status_code == 429):
                    retry_after = 2 ** attempt
                    if hasattr(e, 'response') and e.response is not None:
                        headers = e.response.headers
                        if 'retry-after' in headers:
                            try:
                                retry_after = int(headers['retry-after'])
                            except:
                                pass
                    if attempt < max_retries - 1:
                        logger.warning(f"Rate limited by Groq. Retrying in {retry_after}s... (Attempt {attempt+1}/{max_retries})")
                        time.sleep(retry_after)
                        continue
                logger.error(f"Groq API error: {str(e)}")
                raise e

    def extract_job_requirements(self, job_description: str) -> Dict[str, Any]:
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

Return ONLY a valid JSON object matching this schema, without any markdown formatting or code blocks:
{{
  "title": "string",
  "experience_level": "junior|mid|senior|lead",
  "min_years_experience": int,
  "required_skills": [
    {{"name": "string", "category": "string", "importance": int, "min_years": int, "required": bool}}
  ],
  "preferred_skills": [],
  "responsibilities": ["string"],
  "qualifications": ["string"]
}}
"""
        # Flag: Llama 3.1 8B might need tuning for exact schema adherence and JSON formatting
        try:
            messages = [{"role": "user", "content": prompt}]
            response_text = self._call_with_retry(messages, response_format={"type": "json_object"})
            job_data = json.loads(response_text)
            job_data = self._validate_and_enhance_job_data(job_data)
            return job_data
        except Exception as e:
            logger.error(f"Structured job extraction failed: {str(e)}")
            return self._fallback_job_extraction(job_description)

    def extract_candidate_profile(self, resume_text: str, filename: str = "") -> Dict[str, Any]:
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

Return ONLY a valid JSON object matching this schema, without any markdown formatting or code blocks:
{{
  "name": "string",
  "email": "string",
  "phone": "string",
  "summary": "string",
  "skills": [
    {{"name": "string", "category": "string", "proficiency": int, "years_experience": int, "evidence": "string"}}
  ],
  "experience": [
    {{"role": "string", "company": "string", "duration": "string", "years_experience": int, "description": "string", "technologies_used": ["string"]}}
  ],
  "education": [
    {{"degree": "string", "field": "string", "institution": "string", "year": "string"}}
  ],
  "total_years_experience": int,
  "leadership_indicators": ["string"]
}}
"""
        # Flag: Llama 3.1 8B might need tuning for context size and exact JSON formatting
        try:
            messages = [{"role": "user", "content": prompt}]
            response_text = self._call_with_retry(messages, response_format={"type": "json_object"})
            candidate_data = json.loads(response_text)
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
            messages = [{"role": "user", "content": prompt}]
            # No JSON formatting expected here
            explanation = self._call_with_retry(messages).strip()
            score = match_analysis.get('match_score', 0)
            if score >= 80: category = "Strong Match"
            elif score >= 60: category = "Potential Match"
            else: category = "Weak Match"
            return f"**{category} ({score:.1f}%):** {explanation}"
        except Exception as e:
            logger.error(f"Explanation generation failed: {str(e)}")
            return self._generate_fallback_explanation(candidate_data, job_data, match_analysis)
