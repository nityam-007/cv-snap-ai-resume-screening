#type: ignore
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
        Enhanced job requirements extraction with better skill importance scoring
        """
        prompt = f"""
        Analyze this job description and extract structured information:

        Job Description: {job_description}

        Return ONLY this JSON structure with no additional text:
        {{
            "title": "exact job title",
            "experience_level": "junior/mid/senior/lead",
            "min_years_experience": 7,
            "required_skills": [
                {{
                    "name": "react.js",
                    "category": "technical",
                    "importance": 9,
                    "min_years": 3,
                    "required": true
                }},
                {{
                    "name": "node.js",
                    "category": "technical", 
                    "importance": 9,
                    "min_years": 3,
                    "required": true
                }}
            ],
            "preferred_skills": [
                {{
                    "name": "python",
                    "category": "technical",
                    "importance": 5,
                    "min_years": 2,
                    "required": false
                }}
            ],
            "responsibilities": ["responsibility 1", "responsibility 2"],
            "qualifications": ["qualification 1", "qualification 2"]
        }}

        SKILL NORMALIZATION:
        - Use lowercase: "react.js" not "React.js"
        - Standard names: "node.js", "express.js", "javascript", "postgresql", "mongodb"
        - Separate related skills: list "docker" and "kubernetes" separately

        IMPORTANCE SCORING (1-10):
        - 10: Core requirement, in job title, "must have"
        - 8-9: Very important, key technologies
        - 6-7: Important supporting skills  
        - 4-5: Nice to have
        - 1-3: Barely mentioned

        Extract ALL skills mentioned, including databases, cloud platforms, and methodologies.
        """
        
        try:
            response = self.model.generate_content(prompt)
            response_text = response.text.strip()
            
            # Better JSON cleaning
            response_text = self._clean_json_response(response_text)
            
            job_data = json.loads(response_text)
            
            # Validate and enhance
            job_data = self._validate_and_enhance_job_data(job_data)
            
            logger.info(f"Enhanced job extraction for: {job_data.get('title', 'Unknown')}")
            logger.info(f"Extracted {len(job_data.get('required_skills', []))} required skills")
            return job_data
            
        except json.JSONDecodeError as e:
            logger.error(f"JSON parsing failed: {str(e)}")
            logger.error(f"Raw response: {response.text[:300]}...")
            return self._fallback_job_extraction(job_description)
        except Exception as e:
            logger.error(f"Enhanced job extraction failed: {str(e)}")
            return self._fallback_job_extraction(job_description)

    def extract_candidate_profile(self, resume_text: str, filename: str = "") -> Dict[str, Any]:
        """
        Enhanced candidate profile extraction with better error handling
        """
        prompt = f"""
        Extract candidate information from this resume text:

        Resume: {resume_text}

        Return ONLY this JSON structure with no additional text:
        {{
            "name": "Full Name",
            "email": "email@example.com",
            "phone": "phone number",
            "summary": "professional summary",
            "skills": [
                {{
                    "name": "react.js",
                    "category": "technical",
                    "proficiency": 8,
                    "years_experience": 4,
                    "evidence": "Built responsive UIs using React"
                }},
                {{
                    "name": "node.js", 
                    "category": "technical",
                    "proficiency": 7,
                    "years_experience": 3,
                    "evidence": "Developed RESTful APIs with Node.js"
                }}
            ],
            "experience": [
                {{
                    "role": "Lead Software Engineer",
                    "company": "Tech Company",
                    "duration": "Jan 2020 – Present",
                    "years_experience": 4,
                    "description": "Led development team...",
                    "technologies_used": ["react.js", "node.js", "aws"]
                }}
            ],
            "total_years_experience": 8,
            "leadership_indicators": ["Led team of 5", "Managed projects"]
        }}

        EXTRACTION RULES:
        1. ALWAYS extract the person's name from the resume
        2. Include ALL technical skills mentioned (programming languages, frameworks, databases, cloud platforms)
        3. Use lowercase skill names: "react.js", "node.js", "javascript", "postgresql", "mongodb", "aws"
        4. Calculate years accurately (2020-Present = 4+ years in 2024)
        5. Extract leadership evidence: "Lead", "Senior", "Managed", "Mentored", "Architected"

        PROFICIENCY SCORING (1-10):
        - 9-10: Expert, Lead/Senior roles, 7+ years, managed teams
        - 7-8: Advanced, 4-6 years, complex projects
        - 5-6: Intermediate, 2-4 years, regular use
        - 3-4: Basic, 1-2 years, learning/junior
        - 1-2: Beginner, academic only

        Extract specific evidence for each skill from the resume text.
        """
        
        try:
            response = self.model.generate_content(prompt)
            response_text = response.text.strip()
            
            logger.info(f"Raw Gemini response for {filename}: {response_text[:200]}...")
            
            # Clean JSON response
            response_text = self._clean_json_response(response_text)
            
            candidate_data = json.loads(response_text)
            candidate_data['filename'] = filename
            
            # Validate and enhance
            candidate_data = self._validate_and_enhance_candidate_data(candidate_data)
            
            logger.info(f"Enhanced candidate extraction for: {candidate_data.get('name', 'Unknown')}")
            logger.info(f"Extracted {len(candidate_data.get('skills', []))} skills")
            return candidate_data
            
        except json.JSONDecodeError as e:
            logger.error(f"JSON parsing failed for {filename}: {str(e)}")
            logger.error(f"Raw response: {response.text[:300]}...")
            return self._fallback_candidate_extraction(resume_text, filename)
        except Exception as e:
            logger.error(f"Enhanced candidate extraction failed for {filename}: {str(e)}")
            return self._fallback_candidate_extraction(resume_text, filename)

    def _clean_json_response(self, response_text: str) -> str:
        """Clean and extract JSON from Gemini response"""
        # Remove code blocks
        if '```json' in response_text:
            response_text = response_text.split('```json')[1].split('```')[0]
        elif '```' in response_text:
            response_text = response_text.split('```')[1]
        
        # Find JSON object
        lines = response_text.split('\n')
        json_lines = []
        brace_count = 0
        capturing = False
        
        for line in lines:
            if '{' in line and not capturing:
                capturing = True
                brace_count += line.count('{')
                brace_count -= line.count('}')
                json_lines.append(line)
            elif capturing:
                brace_count += line.count('{')
                brace_count -= line.count('}')
                json_lines.append(line)
                if brace_count == 0:
                    break
        
        if json_lines:
            return '\n'.join(json_lines)
        else:
            return response_text.strip()

    def _validate_and_enhance_job_data(self, job_data: Dict[str, Any]) -> Dict[str, Any]:
        """Validate and enhance job data quality"""
        
        # Ensure required fields exist
        if 'required_skills' not in job_data:
            job_data['required_skills'] = []
        if 'preferred_skills' not in job_data:
            job_data['preferred_skills'] = []
        
        # Enhance required skills
        for skill in job_data.get('required_skills', []):
            if skill.get('importance', 0) < 6:
                skill['importance'] = max(skill.get('importance', 0), 7)
            skill['name'] = skill['name'].lower().strip()
            if 'min_years' not in skill:
                skill['min_years'] = 2
            if 'required' not in skill:
                skill['required'] = True
        
        # Enhance preferred skills
        for skill in job_data.get('preferred_skills', []):
            skill['name'] = skill['name'].lower().strip()
            if skill.get('importance', 0) < 1:
                skill['importance'] = 4
            if 'required' not in skill:
                skill['required'] = False
        
        return job_data

    def _validate_and_enhance_candidate_data(self, candidate_data: Dict[str, Any]) -> Dict[str, Any]:
        """Validate and enhance candidate data quality"""
        
            # Fix name extraction - try harder to get actual names
        if not candidate_data.get('name') or candidate_data.get('name') in ['Unknown Candidate', 'Unknown', '']:
            # Try to extract from resume text first
            resume_text = candidate_data.get('resume_text', '')
            if resume_text:
                # Look for name patterns in first few lines
                lines = resume_text.split('\n')[:10]
                for line in lines:
                    line = line.strip()
                    # Skip lines with common resume keywords
                    if line and len(line.split()) == 2 and len(line) < 50:
                        words = line.split()
                        if (not any(keyword in line.lower() for keyword in 
                            ['email', 'phone', '@', 'summary', 'experience', 'developer', 'engineer', 'skills']) 
                            and all(word.isalpha() or word.replace('.', '').isalpha() for word in words)):
                            candidate_data['name'] = line.title()
                            break
            
            # Fallback to filename cleaning
            if not candidate_data.get('name') or candidate_data['name'] in ['Unknown Candidate', 'Unknown']:
                filename = candidate_data.get('filename', '')
                if filename:
                    # Better filename parsing
                    name_from_file = filename.replace('.pdf', '').replace('.docx', '')
                    # Handle common patterns like "CV1_John", "John_Doe", etc.
                    if '_' in name_from_file:
                        parts = name_from_file.split('_')
                        # Take the part that looks most like a name
                        for part in parts:
                            if len(part) > 2 and part.replace(' ', '').isalpha():
                                candidate_data['name'] = part.replace('_', ' ').title()
                                break
                    else:
                        candidate_data['name'] = name_from_file.replace('_', ' ').title()
        
        
        # Ensure skills array exists and is valid
        if 'skills' not in candidate_data:
            candidate_data['skills'] = []
        
        # Normalize and validate skills
        for skill in candidate_data.get('skills', []):
            skill['name'] = skill['name'].lower().strip()
            
            # Validate proficiency
            if skill.get('proficiency', 0) > 10:
                skill['proficiency'] = 10
            elif skill.get('proficiency', 0) < 1:
                skill['proficiency'] = 1
            
            # Ensure years_experience exists
            if 'years_experience' not in skill:
                skill['years_experience'] = 0
        
        # Validate experience
        if 'experience' not in candidate_data:
            candidate_data['experience'] = []
        
        for exp in candidate_data.get('experience', []):
            if 'years_experience' not in exp:
                exp['years_experience'] = 1
        
        # Calculate total experience more accurately
        total_exp = sum([exp.get('years_experience', 0) for exp in candidate_data.get('experience', [])])
        stated_exp = candidate_data.get('total_years_experience', 0)
        
        # Use the higher of calculated vs stated
        candidate_data['total_years_experience'] = max(total_exp, stated_exp)
        
        return candidate_data

    def generate_match_explanation(self, candidate_data: Dict[str, Any], 
                                  job_data: Dict[str, Any], 
                                  match_analysis: Dict[str, Any]) -> str:
        """Generate natural language explanation for candidate-job match"""
        
        prompt = f"""
        Generate a professional explanation for this candidate-job match:
        
        Candidate: {candidate_data.get('name', 'Unknown')}
        Experience: {candidate_data.get('total_years_experience', 0)} years
        Skills: {[skill.get('name') for skill in candidate_data.get('skills', [])][:10]}
        
        Job: {job_data.get('title', 'Unknown')}
        Required Skills: {[skill.get('name') for skill in job_data.get('required_skills', [])][:10]}
        
        Match Score: {match_analysis.get('match_score', 0):.1f}%
        Skills Matched: {match_analysis.get('matched_skills', 0)}/{match_analysis.get('total_required_skills', 0)}
        
        Provide 2-3 sentences covering:
        1. Key strengths/alignments
        2. Notable gaps or concerns
        3. Overall recommendation
        
        Be specific about technologies and experience levels.
        """
        
        try:
            response = self.model.generate_content(prompt)
            explanation = response.text.strip()
            
            # Add match category
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
        """Improved fallback method for job requirement extraction"""
        logger.warning("Using fallback job extraction method")
        
        text_lower = job_description.lower()
        
        # Extract skills using better patterns
        skill_patterns = {
            'react.js': ['react', 'react.js', 'reactjs'],
            'node.js': ['node', 'node.js', 'nodejs'],
            'javascript': ['javascript', 'js', 'es6'],
            'python': ['python'],
            'java': ['java'],
            'postgresql': ['postgresql', 'postgres'],
            'mongodb': ['mongodb', 'mongo'],
            'mysql': ['mysql'],
            'aws': ['aws', 'amazon web services'],
            'docker': ['docker'],
            'kubernetes': ['kubernetes', 'k8s'],
            'express.js': ['express', 'express.js'],
            'redux': ['redux'],
            'typescript': ['typescript', 'ts']
        }
        
        found_skills = []
        for skill_name, patterns in skill_patterns.items():
            for pattern in patterns:
                if pattern in text_lower:
                    found_skills.append({
                        "name": skill_name,
                        "category": "technical",
                        "importance": 7,
                        "min_years": 2,
                        "required": True
                    })
                    break
        
        return {
            "title": "Senior Full Stack Developer",
            "experience_level": "senior",
            "min_years_experience": 5,
            "required_skills": found_skills,
            "preferred_skills": [],
            "responsibilities": [],
            "qualifications": []
        }
    
    def _fallback_candidate_extraction(self, resume_text: str, filename: str) -> Dict[str, Any]:
        """Improved fallback method for candidate profile extraction"""
        logger.warning(f"Using fallback candidate extraction for {filename}")
        
        # Extract name from text or filename
        name = "Unknown Candidate"
        
        # Try to extract name from filename first
        if filename:
            name_from_file = filename.replace('.pdf', '').replace('.docx', '').replace('_', ' ')
            if name_from_file and len(name_from_file) > 3:
                name = name_from_file.title()
        
        # Try to extract name from resume text
        lines = resume_text.split('\n')[:5]  # Check first 5 lines
        for line in lines:
            line = line.strip()
            if line and len(line.split()) >= 2 and len(line) < 50:
                # Looks like a name (2+ words, not too long)
                if not any(keyword in line.lower() for keyword in ['email', 'phone', '@', 'summary', 'experience']):
                    name = line.title()
                    break
        
        # Extract email
        email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        emails = re.findall(email_pattern, resume_text)
        
        # Extract basic skills
        skill_patterns = {
            'react.js': ['react', 'react.js'],
            'node.js': ['node', 'node.js'],
            'javascript': ['javascript', 'js'],
            'python': ['python'],
            'java': ['java'],
            'postgresql': ['postgresql', 'postgres'],
            'mongodb': ['mongodb', 'mongo'],
            'aws': ['aws']
        }
        
        found_skills = []
        text_lower = resume_text.lower()
        
        for skill_name, patterns in skill_patterns.items():
            for pattern in patterns:
                if pattern in text_lower:
                    found_skills.append({
                        "name": skill_name,
                        "category": "technical",
                        "proficiency": 5,
                        "years_experience": 2,
                        "evidence": f"Mentioned in resume"
                    })
                    break
        
        return {
            "name": name,
            "email": emails[0] if emails else "",
            "phone": "",
            "skills": found_skills,
            "experience": [{
                "role": "Software Developer",
                "company": "Unknown",
                "duration": "Unknown",
                "years_experience": 2,
                "description": "Professional experience",
                "technologies_used": [skill['name'] for skill in found_skills]
            }] if found_skills else [],
            "total_years_experience": 2 if found_skills else 0,
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