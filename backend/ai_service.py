import os
import json
import logging
import re
from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field
from abc import ABC, abstractmethod

logger = logging.getLogger(__name__)

class SkillRequirement(BaseModel):
    name: str = Field(description="Canonical lowercase skill name, e.g. 'react.js', 'python'")
    category: str = Field(description="Skill category: 'technical', 'soft', 'domain'")
    importance: int = Field(description="Importance 1-10 where 10=must-have, 1=barely mentioned")
    min_years: int = Field(description="Minimum years of experience needed for this skill")
    required: bool = Field(description="True if this is a must-have, False if nice-to-have")

class JobRequirements(BaseModel):
    title: str = Field(description="Exact job title from the description")
    experience_level: str = Field(description="One of: junior, mid, senior, lead")
    min_years_experience: int = Field(description="Minimum total years of experience required")
    required_skills: List[SkillRequirement] = Field(description="Must-have skills")
    preferred_skills: List[SkillRequirement] = Field(description="Nice-to-have skills")
    responsibilities: List[str] = Field(description="Key job responsibilities")
    qualifications: List[str] = Field(description="Required qualifications")

class CandidateSkill(BaseModel):
    name: str = Field(description="Canonical lowercase skill name")
    category: str = Field(description="Skill category: 'technical', 'soft', 'domain'")
    proficiency: int = Field(description="Proficiency level 1-10")
    years_experience: int = Field(description="Years of experience with this skill")
    evidence: str = Field(description="Specific quote or reference from resume text")

class WorkExperience(BaseModel):
    role: str = Field(description="Job title/role")
    company: str = Field(description="Company name")
    duration: str = Field(description="Duration string, e.g. 'Jan 2020 - Present'")
    years_experience: int = Field(description="Number of years at this position")
    description: str = Field(description="Brief description of responsibilities")
    technologies_used: List[str] = Field(description="Technologies used in this role")

class Education(BaseModel):
    degree: str = Field(description="Degree type, e.g. 'Bachelor of Science', 'Master of Technology'")
    field: str = Field(description="Field of study, e.g. 'Computer Science'")
    institution: str = Field(description="University or college name")
    year: str = Field(description="Graduation year")

class CandidateProfile(BaseModel):
    name: str = Field(description="Full name of the candidate")
    email: str = Field(description="Email address")
    phone: str = Field(description="Phone number")
    summary: str = Field(description="Professional summary")
    skills: List[CandidateSkill] = Field(description="All technical and relevant skills")
    experience: List[WorkExperience] = Field(description="Work experience entries")
    education: List[Education] = Field(description="Educational qualifications")
    total_years_experience: int = Field(description="Total years of professional experience")
    leadership_indicators: List[str] = Field(description="Evidence of leadership")


class AIService(ABC):
    @abstractmethod
    def extract_job_requirements(self, job_description: str) -> Dict[str, Any]:
        pass

    @abstractmethod
    def extract_candidate_profile(self, resume_text: str, filename: str = "") -> Dict[str, Any]:
        pass

    @abstractmethod
    def generate_match_explanation(self, candidate_data: Dict[str, Any], job_data: Dict[str, Any], match_analysis: Dict[str, Any]) -> str:
        pass

    def _validate_and_enhance_job_data(self, job_data: Dict[str, Any]) -> Dict[str, Any]:
        if 'required_skills' not in job_data:
            job_data['required_skills'] = []
        if 'preferred_skills' not in job_data:
            job_data['preferred_skills'] = []
        
        for skill in job_data.get('required_skills', []):
            if skill.get('importance', 0) < 6:
                skill['importance'] = max(skill.get('importance', 0), 7)
            skill['name'] = skill['name'].lower().strip()
            if 'min_years' not in skill:
                skill['min_years'] = 2
            if 'required' not in skill:
                skill['required'] = True
        
        for skill in job_data.get('preferred_skills', []):
            skill['name'] = skill['name'].lower().strip()
            if skill.get('importance', 0) < 1:
                skill['importance'] = 4
            if 'required' not in skill:
                skill['required'] = False
        return job_data

    def _validate_and_enhance_candidate_data(self, candidate_data: Dict[str, Any]) -> Dict[str, Any]:
        if not candidate_data.get('name') or candidate_data.get('name') in ['Unknown Candidate', 'Unknown', '']:
            resume_text = candidate_data.get('resume_text', '')
            if resume_text:
                lines = resume_text.split('\n')[:10]
                for line in lines:
                    line = line.strip()
                    if line and len(line.split()) == 2 and len(line) < 50:
                        words = line.split()
                        if (not any(keyword in line.lower() for keyword in 
                            ['email', 'phone', '@', 'summary', 'experience', 'developer', 'engineer', 'skills']) 
                            and all(word.isalpha() or word.replace('.', '').isalpha() for word in words)):
                            candidate_data['name'] = line.title()
                            break
            if not candidate_data.get('name') or candidate_data['name'] in ['Unknown Candidate', 'Unknown']:
                filename = candidate_data.get('filename', '')
                if filename:
                    name_from_file = filename.replace('.pdf', '').replace('.docx', '')
                    if '_' in name_from_file:
                        parts = name_from_file.split('_')
                        for part in parts:
                            if len(part) > 2 and part.replace(' ', '').isalpha():
                                candidate_data['name'] = part.replace('_', ' ').title()
                                break
                    else:
                        candidate_data['name'] = name_from_file.replace('_', ' ').title()
        
        if 'skills' not in candidate_data:
            candidate_data['skills'] = []
        for skill in candidate_data.get('skills', []):
            skill['name'] = skill['name'].lower().strip()
            if skill.get('proficiency', 0) > 10:
                skill['proficiency'] = 10
            elif skill.get('proficiency', 0) < 1:
                skill['proficiency'] = 1
            if 'years_experience' not in skill:
                skill['years_experience'] = 0
                
        if 'experience' not in candidate_data:
            candidate_data['experience'] = []
        for exp in candidate_data.get('experience', []):
            if 'years_experience' not in exp:
                exp['years_experience'] = 1
                
        total_exp = sum([exp.get('years_experience', 0) for exp in candidate_data.get('experience', [])])
        stated_exp = candidate_data.get('total_years_experience', 0)
        candidate_data['total_years_experience'] = max(total_exp, stated_exp)
        return candidate_data

    def _fallback_job_extraction(self, job_description: str) -> Dict[str, Any]:
        logger.warning("Using fallback job extraction method")
        text_lower = job_description.lower()
        years_match = re.search(r'(\d+)[\+–-]?\d*\s*years?', text_lower)
        min_years = int(years_match.group(1)) if years_match else 2
        title_match = job_description.strip().split('\n')[0]
        title = title_match if len(title_match) < 100 else "Software Engineer"
        skill_patterns = {
            'react.js': ['react'], 'node.js': ['node'], 'javascript': ['javascript', 'js'],
            'python': ['python'], 'java': ['java'], 'postgresql': ['postgresql', 'postgres'],
            'mysql': ['mysql'], 'aws': ['aws'], 'docker': ['docker'], 'kubernetes': ['kubernetes', 'k8s'],
            'django': ['django'], 'flask': ['flask'], 'fastapi': ['fastapi'], 'spring-boot': ['spring boot', 'springboot'],
            'ci/cd': ['ci/cd', 'jenkins', 'github actions']
        }
        found_skills = []
        for skill_name, patterns in skill_patterns.items():
            if any(p in text_lower for p in patterns):
                found_skills.append({
                    "name": skill_name, "category": "technical", "importance": 7, "min_years": max(1, min_years-1), "required": True
                })
        return {
            "title": title,
            "experience_level": "junior" if min_years <= 3 else "senior",
            "min_years_experience": min_years,
            "required_skills": found_skills,
            "preferred_skills": [],
            "responsibilities": [],
            "qualifications": []
        }
    
    def _fallback_candidate_extraction(self, resume_text: str, filename: str) -> Dict[str, Any]:
        logger.warning(f"Using fallback candidate extraction for {filename}")
        name = "Unknown Candidate"
        if filename:
            name_from_file = filename.replace('.pdf', '').replace('.docx', '').replace('_', ' ')
            if name_from_file and len(name_from_file) > 3:
                name = name_from_file.title()
        text_lower = resume_text.lower()
        years_match = re.search(r'(\d+)[\+–-]?\d*\s*years?', text_lower)
        cand_years = int(years_match.group(1)) if years_match else 2
        skill_patterns = {
            'react.js': ['react'], 'node.js': ['node'], 'javascript': ['javascript', 'js'],
            'python': ['python'], 'java': ['java'], 'postgresql': ['postgresql', 'postgres'],
            'mysql': ['mysql'], 'aws': ['aws'], 'docker': ['docker'], 'kubernetes': ['kubernetes', 'k8s'],
            'django': ['django'], 'flask': ['flask'], 'fastapi': ['fastapi'], 'spring-boot': ['spring boot', 'springboot'],
            'ci/cd': ['ci/cd', 'jenkins', 'github actions']
        }
        found_skills = []
        for skill_name, patterns in skill_patterns.items():
            if any(p in text_lower for p in patterns):
                found_skills.append({
                    "name": skill_name, "category": "technical", "proficiency": 7, "years_experience": cand_years, "evidence": "Fallback"
                })
        return {
            "name": name,
            "email": "",
            "phone": "",
            "skills": found_skills,
            "experience": [{"role": "Developer", "company": "Unknown", "duration": "Unknown", "years_experience": cand_years, "description": "", "technologies_used": []}],
            "total_years_experience": cand_years,
            "filename": filename
        }

    def _generate_fallback_explanation(self, candidate_data: Dict[str, Any], job_data: Dict[str, Any], match_analysis: Dict[str, Any]) -> str:
        score = match_analysis.get('match_score', 0)
        matched = match_analysis.get('matched_skills', 0)
        total = match_analysis.get('total_required_skills', 0)
        if score >= 70:
            return f"**Good Match** - Candidate matches {matched}/{total} required skills with {score:.1f}% overall compatibility."
        elif score >= 40:
            return f"**Partial Match** - Candidate matches {matched}/{total} required skills. Some gaps identified."
        else:
            return f"**Poor Match** - Limited skill alignment with only {matched}/{total} requirements met."


def get_ai_provider() -> AIService:
    provider = os.getenv("AI_PROVIDER", "gemini").lower()
    if provider == "groq":
        from groq_service import GroqProvider
        return GroqProvider()
    else:
        from gemini_service import GeminiProvider
        return GeminiProvider()
