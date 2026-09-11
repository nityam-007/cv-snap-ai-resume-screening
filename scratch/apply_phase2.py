import re

path = '/Users/nityam/cv-snap-project/backend/gemini_service.py'
with open(path, 'r') as f:
    code = f.read()

# 1. Imports
code = code.replace("import google.generativeai as genai", "from google import genai\nfrom pydantic import BaseModel, Field\nfrom typing import List, Optional")

# 2. Pydantic Models and GEMINI_MODEL
models = """
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

GEMINI_MODEL = "gemini-2.5-flash"

class GeminiService:"""
code = code.replace("class GeminiService:", models)

# 3. __init__
init_old = """    def __init__(self):
        self.api_key = os.getenv("GOOGLE_API_KEY")
        if not self.api_key:
            raise ValueError("GOOGLE_API_KEY not found in environment variables")
        
        # Configure Gemini
        genai.configure(api_key=self.api_key)
        self.model = genai.GenerativeModel('gemini-1.5-flash')
        
        logger.info("Gemini AI service initialized successfully")"""
init_new = """    def __init__(self):
        self.api_key = os.getenv("GOOGLE_API_KEY")
        if not self.api_key:
            raise ValueError("GOOGLE_API_KEY not found in environment variables")
        
        self.client = genai.Client(api_key=self.api_key)
        logger.info("Gemini AI service initialized successfully")"""
code = code.replace(init_old, init_new)

# Replace extract_job_requirements and extract_candidate_profile and generate_match_explanation and delete _clean_json_response
methods_replacement = '''
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
            
    def _validate_and_enhance_job_data(self,'''

pattern = r'    def extract_job_requirements\(self, job_description: str\) -> Dict\[str, Any\]:(.*?)def _validate_and_enhance_job_data\(self,'
code = re.sub(pattern, methods_replacement, code, flags=re.DOTALL)

# generate_match_explanation replacement
match_exp_replacement = '''
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

    def _fallback_job_extraction'''

pattern2 = r'    def generate_match_explanation\(self,(.*?)def _fallback_job_extraction'
code = re.sub(pattern2, match_exp_replacement, code, flags=re.DOTALL)

with open(path, 'w') as f:
    f.write(code)

req_path = '/Users/nityam/cv-snap-project/backend/requirements.txt'
with open(req_path, 'r') as f:
    reqs = f.read()
reqs = re.sub(r'google-ai-generativelanguage==.*?\n', '', reqs)
reqs = re.sub(r'google-generativeai==.*?\n', 'google-genai>=1.0.0\npydantic>=2.0.0\n', reqs)
with open(req_path, 'w') as f:
    f.write(reqs)

print("Phase 2 applied successfully!")
