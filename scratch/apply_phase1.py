import re

path = '/Users/nityam/cv-snap-project/backend/neo4j_service.py'
with open(path, 'r') as f:
    code = f.read()

aliases_str = """
SKILL_ALIASES = {
    "react": "react.js", "reactjs": "react.js", "react js": "react.js", "react.js": "react.js",
    "node": "node.js", "nodejs": "node.js", "node js": "node.js", "node.js": "node.js",
    "express": "express.js", "expressjs": "express.js", "express.js": "express.js",
    "next": "next.js", "nextjs": "next.js", "next.js": "next.js",
    "vue": "vue.js", "vuejs": "vue.js", "vue.js": "vue.js",
    "js": "javascript", "es6": "javascript", "javascript": "javascript",
    "ts": "typescript", "typescript": "typescript",
    "python": "python", "python3": "python", "py": "python",
    "sklearn": "scikit-learn", "scikit learn": "scikit-learn", "scikit-learn": "scikit-learn",
    "tf": "tensorflow", "tensorflow": "tensorflow",
    "torch": "pytorch", "pytorch": "pytorch",
    "spring boot": "spring-boot", "springboot": "spring-boot", "spring-boot": "spring-boot",
    "kotlin": "kotlin",
    "postgres": "postgresql", "pg": "postgresql", "postgresql": "postgresql",
    "mongo": "mongodb", "mongodb": "mongodb",
    "dynamodb": "dynamodb", "redis": "redis", "elasticsearch": "elasticsearch",
    "sqlite": "sqlite", "sql server": "mssql", "mssql": "mssql", "cassandra": "cassandra",
    "amazon web services": "aws", "aws": "aws",
    "google cloud": "gcp", "google cloud platform": "gcp", "gcp": "gcp",
    "microsoft azure": "azure", "azure": "azure",
    "k8s": "kubernetes", "kube": "kubernetes", "kubernetes": "kubernetes",
    "cicd": "ci/cd", "ci cd": "ci/cd", "ci/cd": "ci/cd",
    "containerization": "docker", "docker": "docker",
    "github actions": "github-actions", "github-actions": "github-actions",
    "jenkins": "jenkins", "terraform": "terraform", "ansible": "ansible",
    "html5": "html", "html": "html",
    "css3": "css", "css": "css",
    "tailwind": "tailwind-css", "tailwindcss": "tailwind-css", "tailwind-css": "tailwind-css",
    "bootstrap": "bootstrap",
    "sass": "sass", "scss": "sass",
    "material ui": "material-ui", "mui": "material-ui", "material-ui": "material-ui",
    "react native": "react-native", "react-native": "react-native",
    "flutter": "flutter", "swift": "swift", "ios": "ios", "android": "android",
    "ml": "machine-learning", "machine learning": "machine-learning", "machine-learning": "machine-learning",
    "dl": "deep-learning", "deep learning": "deep-learning", "deep-learning": "deep-learning",
    "ai": "ai", "nlp": "nlp", "data science": "data-science", "data-science": "data-science",
    "rest api": "rest", "restful": "rest", "rest": "rest",
    "graphql": "graphql", "grpc": "grpc",
    "websocket": "websocket", "websockets": "websocket",
    "git": "git", "github": "github", "gitlab": "gitlab",
    "c++": "c++", "cpp": "c++",
    "c#": "c#", "csharp": "c#",
    "go": "go", "golang": "go",
    "rust": "rust", "ruby": "ruby", "php": "php", "r": "r", "sql": "sql",
    "agile": "agile", "scrum": "scrum",
    "tdd": "tdd", "test driven development": "tdd",
    "oop": "oop", "object oriented": "oop",
}
"""
norm_method = """    def normalize_skill_name(self, name: str) -> str:
        if not name:
            return ""
        cleaned = name.lower().strip().rstrip('.')
        cleaned = cleaned.replace(' (programming language)', '').replace(' framework', '')
        return SKILL_ALIASES.get(cleaned, cleaned)
        
"""

code = code.replace("logger = logging.getLogger(__name__)", "logger = logging.getLogger(__name__)\n" + aliases_str)
code = code.replace("    def __init__(self):", norm_method + "    def __init__(self):")
code = code.replace("skill_name = skill.get('name', '').lower().strip()", "skill_name = self.normalize_skill_name(skill.get('name', ''))")

job_old = """            CREATE (j:Job {
                id: $job_id,
                title: $title,
                description: $description,
                company: $company,
                location: $location,
                created_at: datetime()
            })"""
job_new = """            CREATE (j:Job {
                id: $job_id,
                title: $title,
                description: $description,
                company: $company,
                location: $location,
                min_years_experience: $min_years_experience,
                experience_level: $experience_level,
                created_at: datetime()
            })"""
code = code.replace(job_old, job_new)

job_run_old = """            result = session.run(query, 
                job_id=job_data.get('id'),
                title=job_data.get('title', 'Unknown'),
                description=job_data.get('description', ''),
                company=job_data.get('company', 'Unknown'),
                location=job_data.get('location', 'Unknown')
            )"""
job_run_new = """            result = session.run(query, 
                job_id=job_data.get('id'),
                title=job_data.get('title', 'Unknown'),
                description=job_data.get('description', ''),
                company=job_data.get('company', 'Unknown'),
                location=job_data.get('location', 'Unknown'),
                min_years_experience=job_data.get('min_years_experience', 0),
                experience_level=job_data.get('experience_level', 'mid')
            )"""
code = code.replace(job_run_old, job_run_new)

scoring_logic = '''
                # Get candidate total experience
                candidate_query = """
                MATCH (c:Candidate {id: $candidate_id})
                RETURN coalesce(c.total_years_experience, 0) as total_years
                """
                
                candidate_result = session.run(candidate_query, candidate_id=candidate_id).single()
                candidate_total_years = candidate_result['total_years'] if candidate_result else 0
                
                # Get job's minimum years requirement
                job_query = """
                MATCH (j:Job {id: $job_id})
                RETURN coalesce(j.min_years_experience, 0) as min_years,
                       coalesce(j.experience_level, 'mid') as experience_level
                """
                job_result = session.run(job_query, job_id=job_id).single()
                job_min_years = job_result['min_years'] if job_result else 0
                job_experience_level = job_result['experience_level'] if job_result else 'mid'
                
                # Calculate scores
                scores = self._calculate_detailed_scores(
                    skill_matches, all_required, candidate_total_years,
                    job_min_years=job_min_years,
                    job_experience_level=job_experience_level
                )
                
                logger.info(f"Match calculation for {candidate_id}: {scores['final_score']:.1f}% ({len(skill_matches)}/{len(all_required)} skills)")
                
                return {
                    'candidate_id': candidate_id,
                    'job_id': job_id,
                    'match_score': scores['final_score'],
                    'skill_coverage': scores['skill_coverage'],
                    'matched_skills': len(skill_matches),
                    'total_required_skills': len(all_required),
                    'skill_matches': skill_matches,
                    'matched_skill_names': [m['skill'] for m in skill_matches],
                    'missing_skill_names': scores['breakdown'].get('missing_critical_skills', []),
                    'score_breakdown': scores['breakdown']
                }
                
        except Exception as e:
            logger.error(f"Error calculating match for {candidate_id}: {str(e)}")
            return {
                'candidate_id': candidate_id,
                'job_id': job_id,
                'match_score': 0.0,
                'skill_coverage': 0.0,
                'matched_skills': 0,
                'total_required_skills': 1,
                'skill_matches': []
            }
    
    def _calculate_detailed_scores(self, skill_matches, all_required, candidate_total_years,
                                    job_min_years=0, job_experience_level='mid'):
        """
        Calculate detailed scoring with multiple factors and improved weighting.
        """
        total_required = len(all_required)
        matched_count = len(skill_matches)
        
        if total_required == 0:
            return {'final_score': 0, 'skill_coverage': 0, 'breakdown': {}}
        
        # 1. Skill Coverage Score (30% weight)
        skill_coverage = (matched_count / total_required) * 100
        coverage_score = min(skill_coverage, 100) * 0.30
        
        # 2. Skill Quality Score (30% weight)
        quality_score = 0
        total_quality_weight = 0
        
        for match in skill_matches:
            candidate_proficiency = float(match.get('candidate_proficiency', 1))
            candidate_years = float(match.get('candidate_years', 0))
            required_years = float(match.get('required_years', 0))
            importance = float(match.get('job_importance', 5))
            
            if required_years > 0:
                exp_ratio = candidate_years / required_years
                if exp_ratio >= 1.5: exp_factor = 1.2
                elif exp_ratio >= 1.0: exp_factor = 1.0
                elif exp_ratio >= 0.7: exp_factor = 0.8
                elif exp_ratio >= 0.4: exp_factor = 0.5
                else: exp_factor = 0.3
            else:
                if candidate_years >= 5: exp_factor = 1.1
                elif candidate_years >= 3: exp_factor = 1.0
                elif candidate_years >= 1: exp_factor = 0.8
                else: exp_factor = 0.6
            
            prof_factor = min(candidate_proficiency / 10.0, 1.0)
            
            skill_score = prof_factor * exp_factor * importance
            quality_score += skill_score
            total_quality_weight += importance
        
        # Penalize unmatched skills
        for req_skill in all_required:
            skill_found = any(m['skill'] == req_skill['skill'] for m in skill_matches)
            if not skill_found:
                total_quality_weight += float(req_skill.get('importance', 5))
        
        if total_quality_weight > 0:
            quality_score = (quality_score / total_quality_weight) * 30
        else:
            quality_score = 0
        
        # 3. Experience Level Match (20% weight)
        experience_score = 0
        required_years_exp = max(job_min_years, 1)
        exp_ratio = candidate_total_years / required_years_exp
        
        if exp_ratio >= 1.5: experience_score = 20
        elif exp_ratio >= 1.2: experience_score = 18
        elif exp_ratio >= 1.0: experience_score = 16
        elif exp_ratio >= 0.75: experience_score = 12
        elif exp_ratio >= 0.5: experience_score = 7
        elif exp_ratio >= 0.25: experience_score = 4
        else: experience_score = 1
        
        # 4. Critical Skills Score (10% weight)
        critical_score = 0
        critical_skills_present = 0
        total_critical_skills = 0
        missing_critical_skills = []
        
        for required_skill in all_required:
            if required_skill.get('is_required', True):
                total_critical_skills += 1
                skill_found = any(match['skill'] == required_skill['skill'] for match in skill_matches)
                if skill_found:
                    critical_skills_present += 1
                else:
                    missing_critical_skills.append(required_skill['skill'])
        
        if total_critical_skills > 0:
            critical_ratio = critical_skills_present / total_critical_skills
            critical_score = critical_ratio * 10
        else:
            critical_score = 10
        
        # 5. Bonus Pool (10% weight)
        bonus_score = 0
        
        if exp_ratio >= 2.0: bonus_score += 4
        elif exp_ratio >= 1.5: bonus_score += 2
        
        if skill_coverage >= 90: bonus_score += 3
        elif skill_coverage >= 80: bonus_score += 2
        elif skill_coverage >= 70: bonus_score += 1
        
        if skill_matches:
            avg_proficiency = sum(float(m.get('candidate_proficiency', 1)) for m in skill_matches) / len(skill_matches)
            if avg_proficiency >= 8: bonus_score += 3
            elif avg_proficiency >= 7: bonus_score += 2
            elif avg_proficiency >= 6: bonus_score += 1
        
        bonus_score = min(bonus_score, 10)
        
        final_score = coverage_score + quality_score + experience_score + critical_score + bonus_score
        final_score = min(final_score, 98.0)
        
        if matched_count == 0:
            final_score = max(experience_score * 0.3, 0)
            final_score = min(final_score, 15)
        elif skill_coverage < 15:
            final_score = min(final_score, 25)
        elif skill_coverage < 30:
            final_score = min(final_score, 45)
        
        return {
            'final_score': round(final_score, 1),
            'skill_coverage': round(skill_coverage, 1),
            'breakdown': {
                'coverage_score': round(coverage_score, 1),
                'quality_score': round(quality_score, 1),
                'experience_score': round(experience_score, 1),
                'critical_skills_score': round(critical_score, 1),
                'bonus_score': round(bonus_score, 1),
                'matched_skills': matched_count,
                'total_required': total_required,
                'candidate_years': candidate_total_years,
                'job_min_years': job_min_years,
                'missing_critical_skills': missing_critical_skills
            }
        }
    
    def get_all_candidates_for_job(self, job_id: str) -> List[Dict[str, Any]]:'''

pattern = r'# Get candidate total experience(.*?)def get_all_candidates_for_job\(self, job_id: str\) -> List\[Dict\[str, Any\]\]:'
code = re.sub(pattern, scoring_logic, code, flags=re.DOTALL)

with open(path, 'w') as f:
    f.write(code)
print("Phase 1 applied successfully!")
