import re

gem_path = '/Users/nityam/cv-snap-project/backend/gemini_service.py'
with open(gem_path, 'r') as f:
    code = f.read()

fallback_cand = """    def _fallback_candidate_extraction(self, resume_text: str, filename: str) -> Dict[str, Any]:
        import re
        logger.warning(f"Using fallback candidate extraction for {filename}")
        
        name = "Unknown Candidate"
        if filename:
            name_from_file = filename.replace('.pdf', '').replace('.docx', '').replace('_', ' ')
            if name_from_file and len(name_from_file) > 3:
                name = name_from_file.title()
                
        text_lower = resume_text.lower()
        years_match = re.search(r'(\\d+)[\\+–-]?\\d*\\s*years?', text_lower)
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
        }"""

code = re.sub(r'    def _fallback_candidate_extraction.*?return \{.*?\}', lambda m: fallback_cand, code, flags=re.DOTALL)

with open(gem_path, 'w') as f:
    f.write(code)

print("Fallback candidate hotfixed correctly!")
