#type: ignore
"""
CV Snap - Neo4j Graph Database Service
Handles all graph database operations for candidate-skill-job relationships
"""

from neo4j import GraphDatabase
import logging
from typing import List, Dict, Any, Optional
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class Neo4jService:
    """Service class for Neo4j graph database operations"""
    
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
            raise
    
    def close(self):
        """Close the database connection"""
        if self.driver:
            self.driver.close()
            logger.info("Neo4j connection closed")
    
    def clear_database(self):
        """Clear all nodes and relationships (use carefully!)"""
        with self.driver.session() as session:
            session.run("MATCH (n) DETACH DELETE n")
            logger.info("Database cleared")
    
    def create_indexes(self):
        """Create necessary indexes for better performance"""
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
                created_at: datetime()
            })
            RETURN j.id as job_id
            """
            
            result = session.run(query, 
                job_id=job_data.get('id'),
                title=job_data.get('title', 'Unknown'),
                description=job_data.get('description', ''),
                company=job_data.get('company', 'Unknown'),
                location=job_data.get('location', 'Unknown')
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
                skill_name = skill.get('name', '').lower().strip()
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
                skill_name = skill.get('name', '').lower().strip()
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
                skill_name = skill.get('name', '').lower().strip()
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
                
                # Calculate scores
                scores = self._calculate_detailed_scores(skill_matches, all_required, candidate_total_years)
                
                logger.info(f"Match calculation for {candidate_id}: {scores['final_score']:.1f}% ({len(skill_matches)}/{len(all_required)} skills)")
                
                return {
                    'candidate_id': candidate_id,
                    'job_id': job_id,
                    'match_score': scores['final_score'],
                    'skill_coverage': scores['skill_coverage'],
                    'matched_skills': len(skill_matches),
                    'total_required_skills': len(all_required),
                    'skill_matches': skill_matches,
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
    
    def _calculate_detailed_scores(self, skill_matches, all_required, candidate_total_years):
        """
        Calculate detailed scoring with multiple factors and improved weighting
        """
        total_required = len(all_required)
        matched_count = len(skill_matches)
        
        if total_required == 0:
            return {'final_score': 0, 'skill_coverage': 0, 'breakdown': {}}
        
        # 1. Skill Coverage Score (35% weight)
        skill_coverage = (matched_count / total_required) * 100
        coverage_score = min(skill_coverage, 100) * 0.35
        
        # 2. Skill Quality Score (40% weight) - Increased importance
        quality_score = 0
        total_quality_weight = 0
        
        for match in skill_matches:
            candidate_proficiency = float(match.get('candidate_proficiency', 1))
            candidate_years = float(match.get('candidate_years', 0))
            required_years = float(match.get('required_years', 0))
            importance = float(match.get('job_importance', 5))
            
            # Enhanced experience factor (0.6 to 2.2 multiplier)
            if required_years > 0:
                exp_factor = min(candidate_years / required_years, 2.2)
                exp_factor = max(exp_factor, 0.6)
            else:
                exp_factor = min(candidate_years / 2, 1.8)
            
            # Proficiency factor with boost for high proficiency
            prof_factor = min(candidate_proficiency / 10, 1.0)
            if prof_factor >= 0.7:
                prof_factor *= 1.1  # 10% boost for high proficiency
            
            # Combined skill score
            skill_score = prof_factor * exp_factor * importance
            quality_score += skill_score
            total_quality_weight += importance
        
        if total_quality_weight > 0:
            quality_score = (quality_score / total_quality_weight) * 40
        else:
            quality_score = 0
        
        # 3. Experience Level Match (20% weight) - Increased from 15%
        experience_score = 0
        if candidate_total_years >= 7:  # Senior level requirement
            if candidate_total_years >= 10:
                experience_score = 20  # Perfect match
            elif candidate_total_years >= 8:
                experience_score = 18  # Very good
            else:
                experience_score = 15  # Good match (7 years)
        elif candidate_total_years >= 5:
            experience_score = 10  # Some penalty
        elif candidate_total_years >= 3:
            experience_score = 6   # Significant penalty
        else:
            experience_score = 2   # Major penalty
        
        # 4. Critical Skills Score (5% weight) - Reduced from 10%
        critical_score = 0
        critical_skills_present = 0
        total_critical_skills = 0
        
        for required_skill in all_required:
            if required_skill.get('is_required', True):
                total_critical_skills += 1
                skill_found = any(match['skill'] == required_skill['skill'] for match in skill_matches)
                if skill_found:
                    critical_skills_present += 1
        
        if total_critical_skills > 0:
            critical_ratio = critical_skills_present / total_critical_skills
            critical_score = critical_ratio * 5
        else:
            critical_score = 5
        
        # Calculate final score
        final_score = coverage_score + quality_score + experience_score + critical_score

        # Boost for senior candidates with high skill coverage
        if skill_coverage >= 60 and candidate_total_years >= 7:
            if skill_coverage >= 80:
                final_score *= 1.15  # 15% boost for excellent coverage + senior experience
            else:
                final_score *= 1.10  # 10% boost for good coverage + senior experience

        # Leadership bonus
        has_leadership = any('lead' in str(match.get('skill', '')).lower() or 
                            'senior' in str(match.get('skill', '')).lower() or
                            'manage' in str(match.get('skill', '')).lower()
                            for match in skill_matches)
        if has_leadership and candidate_total_years >= 5:
            final_score += 5  # Additional 5 points for leadership
        
        # Apply realistic caps and thresholds
        final_score = min(final_score, 95.0)  # Realistic maximum

        if matched_count == 0:
            final_score = 0
        elif skill_coverage < 20:
            final_score = min(final_score, 30)
        elif skill_coverage < 40:
            final_score = min(final_score, 55)
        
        return {
            'final_score': round(final_score, 1),
            'skill_coverage': round(skill_coverage, 1),
            'breakdown': {
                'coverage_score': round(coverage_score, 1),
                'quality_score': round(quality_score, 1),
                'experience_score': round(experience_score, 1),
                'critical_skills_score': round(critical_score, 1),
                'matched_skills': matched_count,
                'total_required': total_required,
                'candidate_years': candidate_total_years
            }
        }
    
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