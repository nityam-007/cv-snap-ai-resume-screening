import re

gem_path = '/Users/nityam/cv-snap-project/backend/gemini_service.py'
with open(gem_path, 'r') as f:
    code = f.read()

# Fix fallback job extraction
fallback_job = """    def _fallback_job_extraction(self, job_description: str) -> Dict[str, Any]:
        logger.warning("Using fallback job extraction method")
        text_lower = job_description.lower()
        
        # Regex to find years
        years_match = re.search(r'(\d+)[\+–-]?\d*\s*years?', text_lower)
        min_years = int(years_match.group(1)) if years_match else 2
        
        title_match = job_description.strip().split('\\n')[0]
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
            "experience_level": "mid",
            "min_years_experience": min_years,
            "required_skills": found_skills,
            "preferred_skills": [],
            "responsibilities": [],
            "qualifications": []
        }"""

code = re.sub(r'    def _fallback_job_extraction.*?return \{.*?\}', fallback_job, code, flags=re.DOTALL)

with open(gem_path, 'w') as f:
    f.write(code)

print("Fallback logic hotfixed!")
