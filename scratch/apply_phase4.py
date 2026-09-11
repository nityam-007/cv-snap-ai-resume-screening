import re

# Update neo4j_service.py
neo_path = '/Users/nityam/cv-snap-project/backend/neo4j_service.py'
with open(neo_path, 'r') as f:
    neo_code = f.read()

neo_code = neo_code.replace("import logging\nfrom typing import Dict, List, Any, Optional", "import logging\nfrom typing import Dict, List, Any, Optional\nfrom difflib import SequenceMatcher")

fuzzy_func = """
    def _find_fuzzy_skill_match(self, candidate_skill: str, job_skills: List[str], threshold: float = 0.78) -> Optional[str]:
        best_match = None
        best_score = 0.0
        for job_skill in job_skills:
            if candidate_skill == job_skill: return job_skill
            similarity = SequenceMatcher(None, candidate_skill, job_skill).ratio()
            if candidate_skill in job_skill or job_skill in candidate_skill:
                similarity = max(similarity, 0.88)
            cw = set(candidate_skill.replace('-', ' ').replace('.', ' ').split())
            jw = set(job_skill.replace('-', ' ').replace('.', ' ').split())
            if cw and jw:
                overlap = len(cw & jw) / max(len(cw), len(jw))
                if overlap > 0.5: similarity = max(similarity, 0.80 + overlap * 0.15)
            if similarity > best_score and similarity >= threshold:
                best_score = similarity
                best_match = job_skill
        if best_match:
            logger.info(f"Fuzzy match: {candidate_skill} -> {best_match} ({best_score:.2f})")
        return best_match
        
    def link_job_requirements"""
neo_code = neo_code.replace("    def link_job_requirements", fuzzy_func)

fuzzy_pass_old = """                # Get preferred matches"""
fuzzy_pass_new = """                # Fuzzy matching pass for unmatched skills
                matched_skill_names = {m['skill'] for m in skill_matches}
                unmatched_required = [req['skill'] for req in all_required if req['skill'] not in matched_skill_names]
                
                if unmatched_required:
                    cand_all_query = "MATCH (c:Candidate {id: $candidate_id})-[r:HAS_SKILL]->(s:Skill) RETURN s.name as skill, coalesce(r.proficiency, 1) as proficiency, coalesce(r.years_experience, 0) as years_experience"
                    all_cand_skills = session.run(cand_all_query, candidate_id=candidate_id).data()
                    
                    for cand_s in all_cand_skills:
                        if cand_s['skill'] in matched_skill_names: continue
                        
                        fuzzy_match = self._find_fuzzy_skill_match(cand_s['skill'], unmatched_required)
                        if fuzzy_match:
                            req_info = next((r for r in all_required if r['skill'] == fuzzy_match), None)
                            if req_info:
                                skill_matches.append({
                                    'skill': fuzzy_match,
                                    'candidate_proficiency': float(cand_s['proficiency']) * 0.8,
                                    'candidate_years': float(cand_s['years_experience']),
                                    'job_importance': req_info['importance'],
                                    'required_years': req_info['required_years'],
                                    'fuzzy_matched': True,
                                    'original_skill': cand_s['skill']
                                })
                                unmatched_required.remove(fuzzy_match)
                                matched_skill_names.add(fuzzy_match)

                # Get preferred matches"""
neo_code = neo_code.replace(fuzzy_pass_old, fuzzy_pass_new)

with open(neo_path, 'w') as f:
    f.write(neo_code)


# Update file_parser.py
fp_path = '/Users/nityam/cv-snap-project/backend/file_parser.py'
with open(fp_path, 'r') as f:
    fp_code = f.read()

fp_clean_old = """    @staticmethod
    def clean_text(text: str) -> str:
        \"\"\"Clean extracted text from document\"\"\"
        if not text:
            return ""
            
        # Basic cleaning
        text = re.sub(r'\\s+', ' ', text)
        text = re.sub(r'[^a-zA-Z0-9\\s\\.,;:\\-\\_\\@\\#\\+\\*\\/\\(\\)]', ' ', text)
        return text.strip()"""
fp_clean_new = """    @staticmethod
    def clean_text(text: str) -> str:
        \"\"\"Clean extracted text from document while preserving structure\"\"\"
        if not text:
            return ""
            
        # Collapse 3+ newlines to 2
        text = re.sub(r'\\n{3,}', '\\n\\n', text)
        # Normalize horizontal whitespace only
        text = re.sub(r'[^\\S\\n]+', ' ', text)
        # Clean bullets
        text = re.sub(r'[•●▪▸►◆■]', '- ', text)
        # Remove non-printable (keep ASCII 32-126 and newline)
        text = re.sub(r'[^\\x20-\\x7E\\n]', '', text)
        
        # Clean up double spaces
        text = text.replace('  ', ' ')
        return text.strip()
        
    @staticmethod
    def extract_sections(text: str) -> dict:
        \"\"\"Split resume into sections\"\"\"
        sections = {}
        # Common headers
        header_patterns = [
            r'^(?i)(professional summary|summary|profile|about me)[\s\:]*$',
            r'^(?i)(experience|work experience|employment history|professional experience)[\s\:]*$',
            r'^(?i)(education|academic background|qualifications)[\s\:]*$',
            r'^(?i)(skills|technical skills|core competencies|technologies)[\s\:]*$',
            r'^(?i)(projects|personal projects|academic projects)[\s\:]*$',
            r'^(?i)(certifications|licenses)[\s\:]*$',
            r'^(?i)(achievements|awards|honors)[\s\:]*$'
        ]
        
        lines = text.split('\\n')
        current_section = 'Uncategorized'
        current_content = []
        
        for line in lines:
            line_clean = line.strip()
            is_header = False
            if 0 < len(line_clean) < 40:
                for pattern in header_patterns:
                    if re.match(pattern, line_clean):
                        if current_content:
                            sections[current_section] = '\\n'.join(current_content).strip()
                        current_section = re.sub(r'[\s\:]*$', '', line_clean).title()
                        current_content = []
                        is_header = True
                        break
            if not is_header and line_clean:
                current_content.append(line_clean)
                
        if current_content:
            sections[current_section] = '\\n'.join(current_content).strip()
            
        return sections"""
fp_code = fp_code.replace(fp_clean_old, fp_clean_new)

with open(fp_path, 'w') as f:
    f.write(fp_code)

print("Phase 4 applied successfully!")
