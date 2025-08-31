# type: ignore
"""
CV Snap - Main FastAPI Application
AI-Powered Resume Screening and Ranking System
"""

from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from typing import List, Dict, Any
import uuid
import asyncio
import logging
import os
from dotenv import load_dotenv

# Import our services
from file_parser import DocumentParser
from gemini_service import GeminiService
from neo4j_service import Neo4jService

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="CV Snap - AI Resume Screening",
    description="AI-powered resume ranking and screening system",
    version="1.0.0"
)

# Configure CORS
allowed_origins = os.getenv("ALLOWED_ORIGINS", "http://localhost:3000").split(",")
app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize services
document_parser = DocumentParser()
gemini_service = GeminiService()
neo4j_service = Neo4jService()

# Configuration
MAX_FILE_SIZE = int(os.getenv("MAX_FILE_SIZE", 10485760))  # 10MB
ALLOWED_EXTENSIONS = os.getenv("ALLOWED_EXTENSIONS", "pdf,docx").split(",")

class CVSnapProcessor:
    """Main processing class for CV Snap operations"""
    
    def __init__(self):
        self.document_parser = document_parser
        self.gemini_service = gemini_service
        self.neo4j_service = neo4j_service
    
    async def process_resumes(self, job_description: str, resume_files: List[UploadFile]) -> Dict[str, Any]:
        """
        Process job description and resumes to generate ranked candidates
        
        Args:
            job_description (str): Job description text
            resume_files (List[UploadFile]): List of uploaded resume files
            
        Returns:
            dict: Processing results with ranked candidates
        """
        try:
            self.neo4j_service.clear_database()
            # Generate unique job ID
            job_id = f"job_{uuid.uuid4().hex[:8]}"
            
            logger.info(f"Starting analysis for job {job_id} with {len(resume_files)} resumes")
            
            # Step 1: Extract job requirements using Gemini AI
            logger.info("Extracting job requirements...")
            job_data = self.gemini_service.extract_job_requirements(job_description)
            job_data['id'] = job_id
            
            # Step 2: Create job node in Neo4j
            logger.info("Creating job node in graph database...")
            self.neo4j_service.create_job_node(job_data)
            
            # Step 3: Create required skills nodes and link to job
            if job_data.get('required_skills'):
                skill_names = self.neo4j_service.create_skill_nodes(job_data['required_skills'])
                self.neo4j_service.link_job_requirements(job_id, job_data['required_skills'])
            
            # Step 4: Process each resume
            candidates = []
            processing_errors = []
            
            for i, resume_file in enumerate(resume_files):
                try:
                    candidate_result = await self._process_single_resume(
                        resume_file, job_id, job_data, i
                    )
                    if candidate_result:
                        candidates.append(candidate_result)
                except Exception as e:
                    logger.error(f"Error processing resume {resume_file.filename}: {str(e)}")
                    processing_errors.append({
                        'filename': resume_file.filename,
                        'error': str(e)
                    })
            
            # Step 5: Calculate match scores and rank candidates
            logger.info("Calculating match scores...")
            ranked_candidates = self.neo4j_service.get_all_candidates_for_job(job_id)
            
            # Step 6: Generate explanations for top candidates
            logger.info("Generating match explanations...")
            for candidate in ranked_candidates:
                try:
                    # Get candidate data from Neo4j or storage
                    candidate_data = self._get_candidate_data(candidate['candidate_id'])
                    if candidate_data:
                        explanation = self.gemini_service.generate_match_explanation(
                            candidate_data, job_data, candidate
                        )
                        candidate['explanation'] = explanation
                    else:
                        candidate['explanation'] = "Unable to generate detailed explanation"
                except Exception as e:
                    logger.warning(f"Failed to generate explanation for {candidate['candidate_id']}: {str(e)}")
                    candidate['explanation'] = "Explanation generation failed"
            
            # Prepare final results
            results = {
                'job_id': job_id,
                'job_info': {
                    'title': job_data.get('title', 'Unknown Position'),
                    'total_required_skills': len(job_data.get('required_skills', [])),
                    'experience_level': job_data.get('experience_level', 'Not specified')
                },
                'total_resumes': len(resume_files),
                'successfully_processed': len(candidates),
                'processing_errors': processing_errors,
                'ranked_candidates': ranked_candidates[:20],  # Top 20 candidates
                'processing_time': 'Completed successfully'
            }
            
            logger.info(f"Analysis completed for job {job_id}. Processed {len(candidates)} candidates")
            return results
            
        except Exception as e:
            logger.error(f"Error in resume processing: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Processing failed: {str(e)}")
    
    async def _process_single_resume(self, resume_file: UploadFile, job_id: str, 
                                   job_data: Dict[str, Any], index: int) -> Dict[str, Any]:
        """Process a single resume file"""
        
        # Validate file
        if not self._validate_file(resume_file):
            raise HTTPException(status_code=400, detail=f"Invalid file: {resume_file.filename}")
        
        # Read file content
        file_content = await resume_file.read()
        
        # Parse document
        logger.info(f"Parsing resume: {resume_file.filename}")
        resume_text = self.document_parser.parse_document(resume_file.filename, file_content)
        
        if not resume_text:
            raise ValueError(f"Could not extract text from {resume_file.filename}")
        
        # Extract candidate profile using Gemini AI
        logger.info(f"Extracting profile from: {resume_file.filename}")
        candidate_data = self.gemini_service.extract_candidate_profile(
            resume_text, resume_file.filename
        )
        
        # Generate unique candidate ID
        candidate_id = f"candidate_{uuid.uuid4().hex[:8]}_{index}"
        candidate_data['id'] = candidate_id
        candidate_data['resume_text'] = resume_text
        
        # Create candidate node in Neo4j
        logger.info(f"Creating candidate node: {candidate_id}")
        self.neo4j_service.create_candidate_node(candidate_data)
        
        # Create skill nodes and link to candidate
        if candidate_data.get('skills'):
            self.neo4j_service.create_skill_nodes(candidate_data['skills'])
            self.neo4j_service.link_candidate_skills(candidate_id, candidate_data['skills'])
        
        # Create experience nodes
        if candidate_data.get('experience'):
            self.neo4j_service.create_experience_nodes(candidate_id, candidate_data['experience'])
        
        # Store candidate data for later reference (in production, use proper storage)
        self._store_candidate_data(candidate_id, candidate_data)
        
        return {
            'candidate_id': candidate_id,
            'filename': resume_file.filename,
            'name': candidate_data.get('name', 'Unknown'),
            'email': candidate_data.get('email', ''),
            'skills_count': len(candidate_data.get('skills', [])),
            'experience_years': candidate_data.get('total_years_experience', 0)
        }
    
    def _validate_file(self, file: UploadFile) -> bool:
        """Validate uploaded file"""
        # Check file extension
        file_extension = file.filename.split('.')[-1].lower() if '.' in file.filename else ''
        if file_extension not in ALLOWED_EXTENSIONS:
            return False
        
        # Check file size (this is approximate, actual size check happens during read)
        if file.size and file.size > MAX_FILE_SIZE:
            return False
            
        return True
    
    def _store_candidate_data(self, candidate_id: str, candidate_data: Dict[str, Any]):
        """Store candidate data (in production, use proper database/cache)"""
        # For demo purposes, we'll use a simple in-memory store
        # In production, use Redis, database, or file storage
        if not hasattr(self, '_candidate_store'):
            self._candidate_store = {}
        self._candidate_store[candidate_id] = candidate_data
    
    def _get_candidate_data(self, candidate_id: str) -> Dict[str, Any]:
        """Retrieve candidate data"""
        if hasattr(self, '_candidate_store'):
            return self._candidate_store.get(candidate_id)
        return None

# Initialize processor
cv_processor = CVSnapProcessor()

@app.on_event("startup")
async def startup_event():
    """Initialize services on startup"""
    logger.info("CV Snap server starting up...")
    
    # Create Neo4j indexes
    neo4j_service.create_indexes()
    logger.info("Neo4j indexes created")
    
    logger.info("CV Snap server ready!")

@app.on_event("shutdown") 
async def shutdown_event():
    """Cleanup on shutdown"""
    logger.info("CV Snap server shutting down...")
    neo4j_service.close()

@app.get("/")
async def root():
    """Health check endpoint"""
    return {
        "message": "CV Snap - AI-Powered Resume Screening System",
        "status": "running",
        "version": "1.0.0"
    }

@app.get("/health")
async def health_check():
    """Detailed health check"""
    try:
        # Test Neo4j connection
        with neo4j_service.driver.session() as session:# type: ignore
            session.run("RETURN 1")
        
        return {
            "status": "healthy",
            "services": {
                "api": "running",
                "neo4j": "connected",
                "gemini": "configured"
            }
        }
    except Exception as e:
        return JSONResponse(
            status_code=503,
            content={
                "status": "unhealthy", 
                "error": str(e)
            }
        )

@app.post("/analyze")
async def analyze_resumes(
    job_description: str = Form(...),
    resume_files: List[UploadFile] = File(...)
):
    """
    Main endpoint: Analyze job description and rank candidates
    
    Args:
        job_description: Job description text
        resume_files: List of resume files (PDF/DOCX)
        
    Returns:
        JSON with ranked candidates and analysis
    """
    
    # Validate inputs
    if not job_description or not job_description.strip():
        raise HTTPException(status_code=400, detail="Job description is required")
    
    if not resume_files:
        raise HTTPException(status_code=400, detail="At least one resume file is required")
    
    if len(resume_files) > 50:  # Reasonable limit
        raise HTTPException(status_code=400, detail="Too many files. Maximum 50 resumes allowed")
    
    try:
        # Process resumes
        results = await cv_processor.process_resumes(job_description, resume_files)
        return JSONResponse(content=results)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unexpected error in /analyze endpoint: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error occurred")

@app.post("/analyze-sample")
async def analyze_sample():
    """
    Sample endpoint with mock data for testing frontend
    """
    sample_results = {
        "job_id": "sample_job_123",
        "job_info": {
            "title": "Senior Python Developer",
            "total_required_skills": 8,
            "experience_level": "senior"
        },
        "total_resumes": 3,
        "successfully_processed": 3,
        "processing_errors": [],
        "ranked_candidates": [
            {
                "candidate_id": "candidate_1",
                "name": "Alice Johnson",
                "email": "alice.j@email.com",
                "match_score": 92.5,
                "skill_coverage": 87.5,
                "matched_skills": 7,
                "total_required_skills": 8,
                "explanation": "**Strong Match** - Alice has excellent Python and Django experience with 6+ years in backend development. Strong AWS and Docker skills align perfectly with infrastructure requirements. Minor gap in React frontend experience."
            },
            {
                "candidate_id": "candidate_2", 
                "name": "Bob Smith",
                "email": "bob.smith@email.com",
                "match_score": 78.2,
                "skill_coverage": 75.0,
                "matched_skills": 6,
                "total_required_skills": 8,
                "explanation": "**Good Match** - Bob brings solid Python and PostgreSQL expertise with 5 years experience. Has worked with microservices architecture. Could benefit from more AWS cloud experience and Docker containerization skills."
            },
            {
                "candidate_id": "candidate_3",
                "name": "Carol Davis", 
                "email": "carol.d@email.com",
                "match_score": 65.8,
                "skill_coverage": 62.5,
                "matched_skills": 5,
                "total_required_skills": 8,
                "explanation": "**Partial Match** - Carol has good Python fundamentals and some Django experience. Strong analytical skills but limited cloud platform experience. Would need training in AWS and modern deployment practices."
            }
        ],
        "processing_time": "Sample data generated successfully"
    }
    
    return JSONResponse(content=sample_results)

@app.get("/job/{job_id}/candidates")
async def get_job_candidates(job_id: str):
    """Get all candidates for a specific job"""
    try:
        candidates = neo4j_service.get_all_candidates_for_job(job_id)
        return JSONResponse(content={
            "job_id": job_id,
            "candidates": candidates
        })
    except Exception as e:
        logger.error(f"Error retrieving candidates for job {job_id}: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to retrieve candidates")

@app.delete("/clear-database")
async def clear_database():
    """Clear all data from Neo4j (development only)"""
    if os.getenv("DEBUG_MODE") != "True":
        raise HTTPException(status_code=403, detail="Only available in debug mode")
    
    try:
        neo4j_service.clear_database()
        return {"message": "Database cleared successfully"}
    except Exception as e:
        logger.error(f"Error clearing database: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to clear database")

# Run the server
if __name__ == "__main__":
    import uvicorn
    
    host = os.getenv("FASTAPI_HOST", "0.0.0.0")
    port = int(os.getenv("FASTAPI_PORT", 8000))
    debug = os.getenv("DEBUG_MODE", "True").lower() == "true"
    
    uvicorn.run(
        "main:app",
        host=host,
        port=port,
        reload=debug,
        log_level="info"
    )