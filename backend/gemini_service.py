"""
CV Snap - Gemini AI Service
Handles all AI-powered analysis using Google's Gemini API
"""

import google.generativeai as genai
import json
import logging
from typing import Dict, List, Any, Optional
import os
from dotenv import load_dotenv
import re

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class GeminiService:
    """Service class for Gemini AI operations"""
    
    def __init__(self):
        self.api_key = os.getenv("GOOGLE_API_KEY")
        if not self.api_key:
            raise ValueError("GOOGLE_API_KEY not found in environment variables")
        
        # Configure Gemini
        genai.configure(api_key=self.api_key)
        self.model = genai.GenerativeModel('gemini-1.5-flash')
        
        logger.info("Gemini AI service initialized successfully")
    
    def extract_job_requirements(self, job_description: str) -> Dict[str, Any]:
        """
        Extract structured information from job description
        
        Args:
            job_description (str): Raw job description text
            
        Returns:
            dict: Structured job requirements
        """
        prompt = """
        You are an AI resume/job description parser. 
        Your sole task is to analyze the given job description and output structured JSON only. 
        Do not add commentary, explanations, or extra text.

        Input:
        Job Description: """ + job_description + """

Instructions:
1. Extract and normalize job information into the exact JSON schema below.
2. If information is missing in the JD, leave the field as an empty string ("") or empty array ([]).
3. Skills must be categorized into technical, soft, or domain. Certifications fall under domain.
4. Rate "importance" from 1–10 where 10 = absolutely critical. 
5. Mark "required" = true only if the skill is explicitly stated as mandatory or must-have.

Output Schema (non-negotiable):
{
  "title": "job title",
  "company": "company name if mentioned",
  "location": "location if mentioned", 
  "employment_type": "full-time/part-time/contract/etc",
  "experience_level": "junior/mid/senior/lead/etc",
  "required_skills": [
    {
      "name": "skill name",
      "category": "technical/soft/domain",
      "importance": 1-10,
      "min_years": 0-20,
      "required": true/false
    }
  ],
  "preferred_skills": [
    {
      "name": "skill name", 
      "category": "technical/soft/domain",
      "importance": 1-10
    }
  ],
  "responsibilities": ["responsibility 1", "responsibility 2"],
  "qualifications": ["qualification 1", "qualification 2"],
  "min_years_experience": 0-20,
  "education_requirements": ["degree requirement"],
  "salary_range": "if mentioned",
  "benefits": ["benefit 1", "benefit 2"]
}

Critical Guardrails:
- Return only valid JSON that matches the schema above.
- Do not include comments, notes, or prose outside the JSON.
- If uncertain, make a reasonable assumption but keep it inside the JSON fields.

Final Answer: Output the JSON object only.
        """
        
        try:
            response = self.model.generate_content(prompt)
            
            # Clean the response to extract JSON
            response_text = response.text.strip()
            
            # Remove any markdown code blocks if present
            if '```json' in response_text:
                response_text = response_text.split('```json')[1].split('```')[0]
            elif '```' in response_text:
                response_text = response_text.split('```')[1]
            
            # Parse JSON
            job_data = json.loads(response_text)
            
            logger.info(f"Successfully extracted job requirements for: {job_data.get('title', 'Unknown')}")
            return job_data
            
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse JSON from Gemini response: {str(e)}")
            logger.error(f"Raw response: {response.text}")
            return self._fallback_job_extraction(job_description)
        except Exception as e:
            logger.error(f"Error extracting job requirements: {str(e)}")
            return self._fallback_job_extraction(job_description)
    
    def extract_candidate_profile(self, resume_text: str, filename: str = "") -> Dict[str, Any]:
        """
        Extract structured information from candidate resume
        
        Args:
            resume_text (str): Raw resume text
            filename (str): Original filename for reference
            
        Returns:
            dict: Structured candidate profile
        """
        prompt = f"""
        Analyze this resume and extract structured information in JSON format:
        
        Resume Text: {resume_text}
        
        Please return a JSON object with the following structure:
        {{
            "name": "candidate full name",
            "email": "email address",
            "phone": "phone number",
            "linkedin": "linkedin profile if mentioned",
            "github": "github profile if mentioned",
            "location": "current location",
            "summary": "professional summary",
            "skills": [
                {{
                    "name": "skill name",
                    "category": "technical/soft/domain", 
                    "proficiency": 1-10,
                    "years_experience": 0-20
                }}
            ],
            "experience": [
                {{
                    "role": "job title",
                    "company": "company name",
                    "duration": "duration text",
                    "start_date": "YYYY-MM if available",
                    "end_date": "YYYY-MM if available or 'present'",
                    "years_experience": 0-20,
                    "description": "job description",
                    "key_achievements": ["achievement 1", "achievement 2"],
                    "technologies_used": ["tech1", "tech2"]
                }}
            ],
            "education": [
                {{
                    "degree": "degree name",
                    "institution": "institution name", 
                    "year": "graduation year",
                    "field": "field of study",
                    "gpa": "if mentioned"
                }}
            ],
            "certifications": [
                {{
                    "name": "certification name",
                    "issuer": "issuing organization",
                    "year": "year obtained",
                    "expiry": "expiry date if applicable"
                }}
            ],
            "projects": [
                {{
                    "name": "project name",
                    "description": "project description",
                    "technologies": ["tech1", "tech2"],
                    "duration": "project duration",
                    "url": "project url if available"
                }}
            ],
            "languages": [
                {{
                    "language": "language name",
                    "proficiency": "native/fluent/intermediate/basic"
                }}
            ],
            "total_years_experience": 0-50
        }}
        
        For skills proficiency, rate from 1-10 based on:
        - Years of experience with the skill
        - Project complexity
        - Professional usage
        - Achievements related to the skill
        
        Be thorough in extracting all technical skills, including:
        - Programming languages
        - Frameworks and libraries
        - Databases
        - Cloud platforms
        - Tools and software
        - Methodologies (Agile, DevOps, etc.)
        
        Return only valid JSON, no additional text.
        """
        
        try:
            response = self.model.generate_content(prompt)
            
            # Clean the response to extract JSON
            response_text = response.text.strip()
            
            # Remove any markdown code blocks if present
            if '```json' in response_text:
                response_text = response_text.split('```json')[1].split('```')[0]
            elif '```' in response_text:
                response_text = response_text.split('```')[1]
            
            # Parse JSON
            candidate_data = json.loads(response_text)
            
            # Add filename for reference
            candidate_data['filename'] = filename
            
            logger.info(f"Successfully extracted candidate profile for: {candidate_data.get('name', 'Unknown')}")
            return candidate_data
            
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse JSON from Gemini response: {str(e)}")
            logger.error(f"Raw response: {response.text}")
            return self._fallback_candidate_extraction(resume_text, filename)
        except Exception as e:
            logger.error(f"Error extracting candidate profile: {str(e)}")
            return self._fallback_candidate_extraction(resume_text, filename)
    
    def generate_match_explanation(self, candidate_data: Dict[str, Any], 
                                  job_data: Dict[str, Any], 
                                  match_analysis: Dict[str, Any]) -> str:
        """
        Generate natural language explanation for candidate-job match
        
        Args:
            candidate_data (dict): Candidate profile
            job_data (dict): Job requirements  
            match_analysis (dict): Match analysis from Neo4j
            
        Returns:
            str: Natural language explanation
        """
        prompt = f"""
        Generate a concise, professional explanation for why this candidate matches (or doesn't match) this job opportunity.
        
        Candidate Profile:
        Name: {candidate_data.get('name', 'Unknown')}
        Skills: {[skill.get('name') for skill in candidate_data.get('skills', [])]}
        Experience: {candidate_data.get('total_years_experience', 0)} years total
        
        Job Requirements:
        Title: {job_data.get('title', 'Unknown')}
        Required Skills: {[skill.get('name') for skill in job_data.get('required_skills', [])]}
        Experience Level: {job_data.get('experience_level', 'Unknown')}
        
        Match Analysis:
        Match Score: {match_analysis.get('match_score', 0):.1f}%
        Skill Coverage: {match_analysis.get('skill_coverage', 0):.1f}%
        Matched Skills: {match_analysis.get('matched_skills', 0)}/{match_analysis.get('total_required_skills', 0)}
        
        Please provide a 2-3 sentence explanation that covers:
        1. Key strengths that align with the role
        2. Any notable gaps or areas of concern
        3. Overall recommendation (Strong Match/Good Match/Partial Match/Poor Match)
        
        Be specific about skills and experience levels. Keep it professional and actionable for recruiters.
        """
        
        try:
            response = self.model.generate_content(prompt)
            explanation = response.text.strip()
            
            # Add match category based on score
            score = match_analysis.get('match_score', 0)
            if score >= 80:
                category = "Strong Match"
            elif score >= 60:
                category = "Good Match" 
            elif score >= 40:
                category = "Partial Match"
            else:
                category = "Poor Match"
            
            return f"**{category}** - {explanation}"
            
        except Exception as e:
            logger.error(f"Error generating match explanation: {str(e)}")
            return self._generate_fallback_explanation(match_analysis)
    
    def _fallback_job_extraction(self, job_description: str) -> Dict[str, Any]:
        """Fallback method for job requirement extraction using regex"""
        logger.warning("Using fallback job extraction method")
        
        # Basic regex patterns for common job elements
        skills_keywords = [
            'python', 'java', 'javascript', 'react', 'node.js', 'sql', 'aws',
            'docker', 'kubernetes', 'git', 'agile', 'scrum', 'machine learning',
            'data science', 'frontend', 'backend', 'full stack', 'api', 'rest'
        ]
        
        found_skills = []
        text_lower = job_description.lower()
        
        for skill in skills_keywords:
            if skill in text_lower:
                found_skills.append({
                    "name": skill,
                    "category": "technical",
                    "importance": 5,
                    "required": True
                })
        
        return {
            "title": "Unknown Position",
            "required_skills": found_skills,
            "preferred_skills": [],
            "responsibilities": [],
            "qualifications": [],
            "min_years_experience": 0
        }
    
    def _fallback_candidate_extraction(self, resume_text: str, filename: str) -> Dict[str, Any]:
        """Fallback method for candidate profile extraction"""
        logger.warning("Using fallback candidate extraction method")
        
        # Extract basic contact info using regex
        email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        emails = re.findall(email_pattern, resume_text)
        
        return {
            "name": "Unknown Candidate",
            "email": emails[0] if emails else "",
            "phone": "",
            "skills": [],
            "experience": [],
            "education": [],
            "total_years_experience": 0,
            "filename": filename
        }
    
    def _generate_fallback_explanation(self, match_analysis: Dict[str, Any]) -> str:
        """Generate a basic explanation when AI fails"""
        score = match_analysis.get('match_score', 0)
        matched = match_analysis.get('matched_skills', 0)
        total = match_analysis.get('total_required_skills', 0)
        
        if score >= 70:
            return f"**Good Match** - Candidate matches {matched}/{total} required skills with {score:.1f}% overall compatibility."
        elif score >= 40:
            return f"**Partial Match** - Candidate matches {matched}/{total} required skills. Some gaps identified."
        else:
            return f"**Poor Match** - Limited skill alignment with only {matched}/{total} requirements met."

# Example usage
if __name__ == "__main__":
    # Initialize Gemini service
    gemini_service = GeminiService()
    
    # Test job description analysis
    sample_jd = """
    Senior Python Developer - Remote
    We are looking for an experienced Python developer with 5+ years of experience.
    Must have: Python, Django, PostgreSQL, AWS, Docker
    Nice to have: React, Machine Learning, Kubernetes
    """
    
    job_requirements = gemini_service.extract_job_requirements(sample_jd)
    print("Job Requirements:")
    print(json.dumps(job_requirements, indent=2))
    
    # Test resume analysis
    sample_resume = """
    John Doe
    john.doe@email.com
    
    Software Engineer with 6 years of experience in Python development.
    Expert in Django, Flask, PostgreSQL, and AWS cloud services.
    Led team of 4 developers on microservices architecture project.
    """
    
    candidate_profile = gemini_service.extract_candidate_profile(sample_resume)
    print("\nCandidate Profile:")
    print(json.dumps(candidate_profile, indent=2))