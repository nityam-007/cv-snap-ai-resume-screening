# type: ignore
"""
CV Snap - Neo4j Graph Database Service
Handles all graph database operations for candidate-skill-job relationships
"""
# \type: ignore
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
        with self.driver.session() as session: # type: ignore
            session.run("MATCH (n) DETACH DELETE n")
            logger.info("Database cleared")
    
    def create_indexes(self):
        """Create necessary indexes for better performance"""
        with self.driver.session() as session: # type: ignore
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
        with self.driver.session() as session: # type: ignore
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
                resume_text=candidate_data.get('resume_text', '')
            )
            
            candidate_id = result.single()['candidate_id']
            logger.info(f"Created candidate node: {candidate_id}")
            return candidate_id
    
    def create_skill_nodes(self, skills: List[Dict[str, Any]]) -> List[str]:
        """
        Create skill nodes in the graph
        
        Args:
            skills (list): List of skill dictionaries
            
        Returns:
            list: List of created skill names
        """
        with self.driver.session() as session:
            created_skills = []
            for skill in skills:
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
                
                result = session.run(query,
                    skill_name=skill.get('name', '').lower(),
                    category=skill.get('category', 'general'),
                    level=skill.get('level', 1)
                )
                
                skill_name = result.single()['skill_name']
                created_skills.append(skill_name)
            
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
                
                result = session.run(query,
                    candidate_id=candidate_id,
                    exp_id=exp_id,
                    role=exp.get('role', 'Unknown'),
                    company=exp.get('company', 'Unknown'),
                    duration=exp.get('duration', 'Unknown'),
                    description=exp.get('description', ''),
                    years_experience=exp.get('years_experience', 0)
                )
                
                created_exp_id = result.single()['exp_id']
                created_experiences.append(created_exp_id)
            
            logger.info(f"Created {len(created_experiences)} experience nodes for candidate {candidate_id}")
            return created_experiences
    
    def link_candidate_skills(self, candidate_id: str, skills: List[Dict[str, Any]]):
        """
        Create relationships between candidate and skills
        
        Args:
            candidate_id (str): Candidate ID
            skills (list): List of skill dictionaries with proficiency levels
        """
        with self.driver.session() as session:
            for skill in skills:
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
                
                session.run(query,
                    candidate_id=candidate_id,
                    skill_name=skill.get('name', '').lower(),
                    proficiency=skill.get('proficiency', 1),
                    years_experience=skill.get('years_experience', 0)
                )
            
            logger.info(f"Linked {len(skills)} skills to candidate {candidate_id}")
    
    def link_job_requirements(self, job_id: str, required_skills: List[Dict[str, Any]]):
        """
        Create relationships between job and required skills
        
        Args:
            job_id (str): Job ID
            required_skills (list): List of required skill dictionaries
        """
        with self.driver.session() as session:
            for skill in required_skills:
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
                
                session.run(query,
                    job_id=job_id,
                    skill_name=skill.get('name', '').lower(),
                    importance=skill.get('importance', 1),
                    min_years=skill.get('min_years', 0),
                    required=skill.get('required', False)
                )
            
            logger.info(f"Linked {len(required_skills)} required skills to job {job_id}")
    
    def calculate_candidate_job_match(self, candidate_id: str, job_id: str) -> Dict[str, Any]:
        """
        Calculate match score between candidate and job using graph relationships
        
        Args:
            candidate_id (str): Candidate ID
            job_id (str): Job ID
            
        Returns:
            dict: Match analysis results
        """
        with self.driver.session() as session:
            # Get skill matches
            skill_match_query = """
            MATCH (c:Candidate {id: $candidate_id})-[ch:HAS_SKILL]->(s:Skill)<-[jr:REQUIRES_SKILL]-(j:Job {id: $job_id})
            RETURN 
                s.name as skill,
                ch.proficiency as candidate_proficiency,
                ch.years_experience as candidate_years,
                jr.importance as job_importance,
                jr.min_years as required_years,
                jr.required as is_required
            """
            
            skill_matches = session.run(skill_match_query, 
                candidate_id=candidate_id, 
                job_id=job_id
            ).data()
            
            # Get total required skills
            total_required_query = """
            MATCH (j:Job {id: $job_id})-[:REQUIRES_SKILL]->(s:Skill)
            RETURN count(s) as total_required
            """
            
            total_required = session.run(total_required_query, job_id=job_id).single()['total_required']
            
            # Calculate scores
            matched_skills = len(skill_matches)
            skill_coverage = matched_skills / max(total_required, 1)
            
            # Calculate weighted score
            total_weight = 0
            weighted_score = 0
            
            for match in skill_matches:
                importance = match['job_importance'] or 1
                proficiency = match['candidate_proficiency'] or 1
                
                # Experience bonus
                candidate_years = match['candidate_years'] or 0
                required_years = match['required_years'] or 0
                experience_bonus = min(candidate_years / max(required_years, 1), 2.0)
                
                skill_score = (proficiency * experience_bonus) * importance
                weighted_score += skill_score
                total_weight += importance
            
            final_score = (weighted_score / max(total_weight, 1)) * skill_coverage
            
            return {
                'candidate_id': candidate_id,
                'job_id': job_id,
                'match_score': min(final_score * 100, 100),  # Cap at 100%
                'skill_coverage': skill_coverage * 100,
                'matched_skills': matched_skills,
                'total_required_skills': total_required,
                'skill_matches': skill_matches
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
            """
            
            candidates = session.run(query).data()
            
            # Calculate match scores for each candidate
            results = []
            for candidate in candidates:
                match_result = self.calculate_candidate_job_match(
                    candidate['candidate_id'], 
                    job_id
                )
                match_result.update({
                    'name': candidate['name'],
                    'email': candidate['email']
                })
                results.append(match_result)
            
            # Sort by match score descending
            results.sort(key=lambda x: x['match_score'], reverse=True)
            return results

# Example usage
if __name__ == "__main__":
    # Initialize Neo4j service
    neo4j_service = Neo4jService()
    
    # Create indexes
    neo4j_service.create_indexes()
    
    # Example: Create a job
    job_data = {
        'id': 'job_001',
        'title': 'Senior Python Developer',
        'description': 'Looking for experienced Python developer...',
        'company': 'Tech Corp'
    }
    
    job_id = neo4j_service.create_job_node(job_data)
    print(f"Created job: {job_id}")
    
    # Close connection
    neo4j_service.close()