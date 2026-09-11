#type: ignore
"""
CV Snap - Neo4j Graph Database Service
Handles all graph database operations for candidate-skill-job relationships
"""

from neo4j import GraphDatabase
import logging
from difflib import SequenceMatcher
from typing import List, Dict, Any, Optional
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

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


class Neo4jService:
    """Service class for Neo4j graph database operations"""
    
    def normalize_skill_name(self, name: str) -> str:
        if not name:
            return ""
        cleaned = name.lower().strip().rstrip('.')
        cleaned = cleaned.replace(' (programming language)', '').replace(' framework', '')
        return SKILL_ALIASES.get(cleaned, cleaned)
        
    def __init__(self):
        self.uri = os.getenv("NEO4J_URI", "bolt://localhost:7687")
        self.user = os.getenv("NEO4J_USER", "neo4j")
        self.password = os.getenv("NEO4J_PASSWORD", "password")
        self.driver = None
        self.connect()
    
    def connect(self):
        """Establish connection to Neo4j database"""
        try:
            self.driver = GraphDatabase.driver(
                self.uri, 
                auth=(self.user, self.password)
            )
            # Test the connection
            self.driver.verify_connectivity()
            logger.info("Successfully connected to Neo4j database")
        except Exception as e:
            logger.error(f"Failed to connect to Neo4j: {str(e)}")
            # Don't raise here so the app can start up, but endpoints needing DB will fail gracefully
            self.driver = None
    
    def close(self):
        """Close the database connection"""
        if self.driver:
            self.driver.close()
            logger.info("Neo4j connection closed")
    
    def clear_database(self):
        """Clear all nodes and relationships (use carefully!)"""
        if not self.driver:
            logger.warning("Neo4j not connected. Cannot clear database.")
            return
        with self.driver.session() as session:
            session.run("MATCH (n) DETACH DELETE n")
            logger.info("Database cleared")
    
    def create_indexes(self):
        """Create necessary indexes for better performance"""
        if not self.driver:
            logger.warning("Neo4j not connected. Cannot create indexes.")
            return
        with self.driver.session() as session:
            # Create indexes
            indexes = [
                "CREATE INDEX candidate_id_idx IF NOT EXISTS FOR (c:Candidate) ON (c.id)",
                "CREATE INDEX job_id_idx IF NOT EXISTS FOR (j:Job) ON (j.id)",
                "CREATE INDEX skill_name_idx IF NOT EXISTS FOR (s:Skill) ON (s.name)",
                "CREATE INDEX experience_role_idx IF NOT EXISTS FOR (e:Experience) ON (e.role)"
            ]
            
            for index_query in indexes:
                try:
                    session.run(index_query)
                    logger.info(f"Created index: {index_query.split()[2]}")
                except Exception as e:
                    logger.warning(f"Index creation failed or already exists: {str(e)}")
    
    def create_job_node(self, job_data: Dict[str, Any]) -> str:
        """
        Create a job node in the graph
        
        Args:
            job_data (dict): Job information including id, title, description, required_skills, etc.
            
        Returns:
            str: Job ID
        """
        with self.driver.session() as session:
            query = """
            CREATE (j:Job {
                id: $job_id,
                title: $title,
                description: $description,
                company: $company,
                location: $location,
                min_years_experience: $min_years_experience,
                experience_level: $experience_level,
                created_at: datetime()
            })
            RETURN j.id as job_id
            """
            
            result = session.run(query, 
                job_id=job_data.get('id'),
                title=job_data.get('title', 'Unknown'),
                description=job_data.get('description', ''),
                company=job_data.get('company', 'Unknown'),
                location=job_data.get('location', 'Unknown'),
                min_years_experience=job_data.get('min_years_experience', 0),
                experience_level=job_data.get('experience_level', 'mid')
            )
            
            job_id = result.single()['job_id']
            logger.info(f"Created job node: {job_id}")
            return job_id
    
    def create_candidate_node(self, candidate_data: Dict[str, Any]) -> str:
        """
        Create a candidate node in the graph
        
        Args:
            candidate_data (dict): Candidate information
            
        Returns:
            str: Candidate ID
        """
        with self.driver.session() as session:
            query = """
            CREATE (c:Candidate {
                id: $candidate_id,
                name: $name,
                email: $email,
                phone: $phone,
                linkedin: $linkedin,
                github: $github,
                resume_text: $resume_text,
                total_years_experience: $total_years_experience,
                created_at: datetime()
            })
            RETURN c.id as candidate_id
            """
            
            result = session.run(query, 
                candidate_id=candidate_data.get('id'),
                name=candidate_data.get('name', 'Unknown'),
                email=candidate_data.get('email', ''),
                phone=candidate_data.get('phone', ''),
                linkedin=candidate_data.get('linkedin', ''),
                github=candidate_data.get('github', ''),
                resume_text=candidate_data.get('resume_text', ''),
                total_years_experience=candidate_data.get('total_years_experience', 0)
            )
            
            candidate_id = result.single()['candidate_id']
            logger.info(f"Created candidate node: {candidate_id} - {candidate_data.get('name', 'Unknown')}")
            return candidate_id
    
    def create_skill_nodes(self, skills: List[Dict[str, Any]]) -> List[str]:
        """
        Create skill nodes in the graph
        
        Args:
            skills (list): List of skill dictionaries
            
        Returns:
            list: List of created skill names
        """
        if not skills:
            logger.warning("No skills provided to create")
            return []
            
        with self.driver.session() as session:
            created_skills = []
            for skill in skills:
                skill_name = self.normalize_skill_name(skill.get('name', ''))
                if not skill_name:
                    continue
                    
                query = """
                MERGE (s:Skill {name: $skill_name})
                ON CREATE SET 
                    s.category = $category,
                    s.level = $level,
                    s.created_at = datetime()
                ON MATCH SET 
                    s.level = CASE WHEN $level > s.level THEN $level ELSE s.level END
                RETURN s.name as skill_name
                """
                
                try:
                    result = session.run(query,
                        skill_name=skill_name,
                        category=skill.get('category', 'general'),
                        level=skill.get('level', skill.get('proficiency', 1))
                    )
                    
                    skill_result = result.single()
                    if skill_result:
                        created_skills.append(skill_result['skill_name'])
                except Exception as e:
                    logger.error(f"Error creating skill {skill_name}: {str(e)}")
            
            logger.info(f"Created/updated {len(created_skills)} skill nodes")
            return created_skills
    
    def create_experience_nodes(self, candidate_id: str, experiences: List[Dict[str, Any]]) -> List[str]:
        """
        Create experience nodes and link them to candidate
        
        Args:
            candidate_id (str): Candidate ID
            experiences (list): List of experience dictionaries
            
        Returns:
            list: List of created experience IDs
        """
        if not experiences:
            logger.info(f"No experience data provided for candidate {candidate_id}")
            return []
            
        with self.driver.session() as session:
            created_experiences = []
            for i, exp in enumerate(experiences):
                exp_id = f"{candidate_id}_exp_{i}"
                query = """
                MATCH (c:Candidate {id: $candidate_id})
                CREATE (e:Experience {
                    id: $exp_id,
                    role: $role,
                    company: $company,
                    duration: $duration,
                    description: $description,
                    years_experience: $years_experience
                })
                CREATE (c)-[:HAS_EXPERIENCE]->(e)
                RETURN e.id as exp_id
                """
                
                try:
                    result = session.run(query,
                        candidate_id=candidate_id,
                        exp_id=exp_id,
                        role=exp.get('role', 'Unknown'),
                        company=exp.get('company', 'Unknown'),
                        duration=exp.get('duration', 'Unknown'),
                        description=exp.get('description', ''),
                        years_experience=exp.get('years_experience', 1)
                    )
                    
                    created_exp_id = result.single()['exp_id']
                    created_experiences.append(created_exp_id)
                except Exception as e:
                    logger.error(f"Error creating experience {exp_id}: {str(e)}")
            
            logger.info(f"Created {len(created_experiences)} experience nodes for candidate {candidate_id}")
            return created_experiences
    
    def link_candidate_skills(self, candidate_id: str, skills: List[Dict[str, Any]]):
        """
        Create relationships between candidate and skills
        
        Args:
            candidate_id (str): Candidate ID
            skills (list): List of skill dictionaries with proficiency levels
        """
        if not skills:
            logger.warning(f"No skills to link for candidate {candidate_id}")
            return
            
        with self.driver.session() as session:
            linked_count = 0
            for skill in skills:
                skill_name = self.normalize_skill_name(skill.get('name', ''))
                if not skill_name:
                    continue
                    
                query = """
                MATCH (c:Candidate {id: $candidate_id})
                MATCH (s:Skill {name: $skill_name})
                MERGE (c)-[r:HAS_SKILL]->(s)
                ON CREATE SET 
                    r.proficiency = $proficiency,
                    r.years_experience = $years_experience,
                    r.created_at = datetime()
                ON MATCH SET
                    r.proficiency = $proficiency,
                    r.years_experience = $years_experience
                """
                
                try:
                    session.run(query,
                        candidate_id=candidate_id,
                        skill_name=skill_name,
                        proficiency=skill.get('proficiency', 1),
                        years_experience=skill.get('years_experience', 0)
                    )
                    linked_count += 1
                except Exception as e:
                    logger.error(f"Error linking skill {skill_name} to candidate {candidate_id}: {str(e)}")
            
            logger.info(f"Linked {linked_count} skills to candidate {candidate_id}")
    

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
        
    def link_job_requirements(self, job_id: str, required_skills: List[Dict[str, Any]]):
        """
        Create relationships between job and required skills
        
        Args:
            job_id (str): Job ID
            required_skills (list): List of required skill dictionaries
        """
        if not required_skills:
            logger.warning(f"No required skills to link for job {job_id}")
            return
            
        with self.driver.session() as session:
            linked_count = 0
            for skill in required_skills:
                skill_name = self.normalize_skill_name(skill.get('name', ''))
                if not skill_name:
                    continue
                    
                query = """
                MATCH (j:Job {id: $job_id})
                MATCH (s:Skill {name: $skill_name})
                MERGE (j)-[r:REQUIRES_SKILL]->(s)
                ON CREATE SET 
                    r.importance = $importance,
                    r.min_years = $min_years,
                    r.required = $required
                ON MATCH SET
                    r.importance = $importance,
                    r.min_years = $min_years,
                    r.required = $required
                """
                
                try:
                    session.run(query,
                        job_id=job_id,
                        skill_name=skill_name,
                        importance=skill.get('importance', 5),
                        min_years=skill.get('min_years', 0),
                        required=skill.get('required', True)
                    )
                    linked_count += 1
                except Exception as e:
                    logger.error(f"Error linking skill {skill_name} to job {job_id}: {str(e)}")
            
            logger.info(f"Linked {linked_count} required skills to job {job_id}")
    
    def calculate_candidate_job_match(self, candidate_id: str, job_id: str) -> Dict[str, Any]:
        """
        Enhanced match score calculation with improved accuracy
        """
        try:
            with self.driver.session() as session:
                # Get skill matches
                skill_match_query = """
                MATCH (c:Candidate {id: $candidate_id})-[ch:HAS_SKILL]->(s:Skill)<-[jr:REQUIRES_SKILL]-(j:Job {id: $job_id})
                RETURN 
                    s.name as skill,
                    coalesce(ch.proficiency, 1) as candidate_proficiency,
                    coalesce(ch.years_experience, 0) as candidate_years,
                    coalesce(jr.importance, 5) as job_importance,
                    coalesce(jr.min_years, 0) as required_years,
                    coalesce(jr.required, true) as is_required
                """
                
                skill_matches = session.run(skill_match_query, 
                    candidate_id=candidate_id, 
                    job_id=job_id
                ).data()
                
                # Get total required skills
                all_required_query = """
                MATCH (j:Job {id: $job_id})-[jr:REQUIRES_SKILL]->(s:Skill)
                RETURN 
                    s.name as skill,
                    coalesce(jr.importance, 5) as importance,
                    coalesce(jr.required, true) as is_required,
                    coalesce(jr.min_years, 0) as min_years
                """
                
                all_required = session.run(all_required_query, job_id=job_id).data()
                
                
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
                
                # Fuzzy matching pass for unmatched skills
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

                # Get preferred matches
                pref_query = "MATCH (c:Candidate {id: $candidate_id})-[ch:HAS_SKILL]->(s:Skill)<-[jp:PREFERS_SKILL]-(j:Job {id: $job_id}) RETURN s.name as skill, coalesce(ch.proficiency, 1) as candidate_proficiency, coalesce(jp.importance, 4) as job_importance"
                pref_matches = session.run(pref_query, candidate_id=candidate_id, job_id=job_id).data()
                
                # Get education
                edu_query = "MATCH (c:Candidate {id: $candidate_id})-[:HAS_EDUCATION]->(ed:Education) RETURN ed.degree as degree, ed.field as field"
                cand_edu = session.run(edu_query, candidate_id=candidate_id).data()
                
                # Calculate scores
                scores = self._calculate_detailed_scores(
                    skill_matches, all_required, candidate_total_years,
                    job_min_years=job_min_years,
                    job_experience_level=job_experience_level,
                    preferred_matches=pref_matches,
                    candidate_education=cand_edu
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
                    'preferred_skills_matched': [m['skill'] for m in (pref_matches or [])],
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
                                    job_min_years=0, job_experience_level='mid',
                                    preferred_matches=None, candidate_education=None):
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
        
        if preferred_matches:
            pref_count = len(preferred_matches)
            if pref_count >= 4: bonus_score += 3
            elif pref_count >= 2: bonus_score += 2
            elif pref_count >= 1: bonus_score += 1
            
        edu_bonus = 0
        if candidate_education:
            relevant_fields = {'computer science','computer engineering','software engineering','information technology','data science','electrical engineering','electronics','mathematics','statistics','it','cs','ece','eee','mca','bca'}
            degree_scores = {'phd':3, 'doctorate':3, 'master':2, 'mtech':2, 'm.tech':2, 'ms':2, 'mca':2, 'bachelor':1, 'btech':1, 'b.tech':1, 'bs':1, 'be':1, 'bca':1, 'bsc':1}
            for edu in candidate_education:
                f_low = str(edu.get('field', '')).lower()
                d_low = str(edu.get('degree', '')).lower()
                f_rel = any(rf in f_low for rf in relevant_fields)
                d_level = 0
                for k,v in degree_scores.items():
                    if k in d_low:
                        d_level = v; break
                if f_rel: edu_bonus = max(edu_bonus, d_level)
                elif d_level > 0: edu_bonus = max(edu_bonus, 1)
            bonus_score += min(edu_bonus, 3)
            
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
                'preferred_skills_matched': len(preferred_matches) if preferred_matches else 0,
                'education_bonus': min(edu_bonus, 3) if candidate_education else 0,
                'matched_skills': matched_count,
                'total_required': total_required,
                'candidate_years': candidate_total_years,
                'job_min_years': job_min_years,
                'missing_critical_skills': missing_critical_skills
            }
        }
    

    def create_education_nodes(self, candidate_id: str, education: List[Dict[str, Any]]) -> List[str]:
        if not education: return []
        with self.driver.session() as session:
            created = []
            for i, edu in enumerate(education):
                edu_id = f"{candidate_id}_edu_{i}"
                query = '''MATCH (c:Candidate {id: $candidate_id})
                           CREATE (ed:Education {id: $edu_id, degree: $degree, field: $field, institution: $inst, year: $year})
                           CREATE (c)-[:HAS_EDUCATION]->(ed)
                           RETURN ed.id as edu_id'''
                try:
                    res = session.run(query, candidate_id=candidate_id, edu_id=edu_id,
                                      degree=edu.get('degree', 'Unknown'), field=edu.get('field', 'Unknown'),
                                      inst=edu.get('institution', 'Unknown'), year=edu.get('year', 'Unknown'))
                    created.append(res.single()['edu_id'])
                except Exception as e: pass
            return created

    def get_all_candidates_for_job(self, job_id: str) -> List[Dict[str, Any]]:
        """
        Get all candidates and their match scores for a specific job
        
        Args:
            job_id (str): Job ID
            
        Returns:
            list: List of candidates with match scores
        """
        with self.driver.session() as session:
            query = """
            MATCH (c:Candidate)
            RETURN c.id as candidate_id, c.name as name, c.email as email
            ORDER BY c.created_at
            """
            
            candidates = session.run(query).data()
            
            if not candidates:
                logger.warning(f"No candidates found for job {job_id}")
                return []
            
            # Calculate match scores for each candidate
            results = []
            for candidate in candidates:
                try:
                    match_result = self.calculate_candidate_job_match(
                        candidate['candidate_id'], 
                        job_id
                    )
                    match_result.update({
                        'name': candidate['name'],
                        'email': candidate['email']
                    })
                    results.append(match_result)
                except Exception as e:
                    logger.error(f"Error calculating match for candidate {candidate['candidate_id']}: {str(e)}")
            
            # Sort by match score descending
            results.sort(key=lambda x: x['match_score'], reverse=True)
            
            logger.info(f"Calculated matches for {len(results)} candidates")
            return results