import axios from 'axios';

// Configure axios defaults
const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

const apiClient = axios.create({
  baseURL: API_BASE_URL,
  timeout: 300000, // 5 minutes for file upload and processing
  headers: {
    'Content-Type': 'multipart/form-data',
  },
});

// Request interceptor for logging
apiClient.interceptors.request.use(
  (config) => {
    console.log(`API Request: ${config.method?.toUpperCase()} ${config.url}`);
    return config;
  },
  (error) => {
    console.error('API Request Error:', error);
    return Promise.reject(error);
  }
);

// Response interceptor for error handling
apiClient.interceptors.response.use(
  (response) => {
    console.log(`API Response: ${response.status} ${response.config.url}`);
    return response;
  },
  (error) => {
    console.error('API Response Error:', error);
    
    if (error.response) {
      // Server responded with error status
      const message = error.response.data?.detail || error.response.data?.message || 'Server error occurred';
      throw new Error(`Server Error (${error.response.status}): ${message}`);
    } else if (error.request) {
      // Request made but no response received
      throw new Error('Network error: Unable to connect to server. Please check your connection.');
    } else {
      // Something else happened
      throw new Error('Request failed: ' + error.message);
    }
  }
);

// Types for API responses
export interface JobInfo {
  title: string;
  total_required_skills: number;
  experience_level: string;
}

export interface RankedCandidate {
  candidate_id: string;
  name: string;
  email: string;
  match_score: number;
  skill_coverage: number;
  matched_skills: number;
  total_required_skills: number;
  explanation: string;
}

export interface ProcessingError {
  filename: string;
  error: string;
}

export interface AnalysisResults {
  job_id: string;
  job_info: JobInfo;
  total_resumes: number;
  successfully_processed: number;
  processing_errors: ProcessingError[];
  ranked_candidates: RankedCandidate[];
  processing_time: string;
}

export interface HealthStatus {
  status: string;
  services?: {
    api: string;
    neo4j: string;
    gemini: string;
  };
  error?: string;
}

// API Functions
export const analyzeResumes = async (
  jobDescription: string,
  resumeFiles: File[]
): Promise<AnalysisResults> => {
  try {
    // Validate inputs
    if (!jobDescription.trim()) {
      throw new Error('Job description is required');
    }

    if (resumeFiles.length === 0) {
      throw new Error('At least one resume file is required');
    }

    if (resumeFiles.length > 50) {
      throw new Error('Maximum 50 resume files allowed');
    }

    // Validate file types and sizes
    const allowedTypes = ['application/pdf', 'application/vnd.openxmlformats-officedocument.wordprocessingml.document'];
    const maxSize = 10 * 1024 * 1024; // 10MB

    for (const file of resumeFiles) {
      if (!allowedTypes.includes(file.type)) {
        throw new Error(`Invalid file type: ${file.name}. Only PDF and DOCX files are allowed.`);
      }
      if (file.size > maxSize) {
        throw new Error(`File too large: ${file.name}. Maximum size is 10MB.`);
      }
    }

    // Prepare form data
    const formData = new FormData();
    formData.append('job_description', jobDescription);
    
    resumeFiles.forEach((file) => {
      formData.append('resume_files', file);
    });

    console.log(`Uploading ${resumeFiles.length} files for analysis...`);

    // Make API request
    const response = await apiClient.post<AnalysisResults>('/analyze', formData);
    
    console.log('Analysis completed successfully');
    return response.data;

  } catch (error) {
    console.error('Analysis failed:', error);
    throw error;
  }
};

export const getSampleAnalysis = async (): Promise<AnalysisResults> => {
  try {
    console.log('Requesting sample analysis...');
    
    const response = await apiClient.post<AnalysisResults>('/analyze-sample');
    
    console.log('Sample analysis loaded successfully');
    return response.data;

  } catch (error) {
    console.error('Sample analysis failed:', error);
    throw error;
  }
};

export const getHealthStatus = async (): Promise<HealthStatus> => {
  try {
    const response = await apiClient.get<HealthStatus>('/health');
    return response.data;
  } catch (error) {
    console.error('Health check failed:', error);
    throw error;
  }
};

export const getJobCandidates = async (jobId: string): Promise<{
  job_id: string;
  candidates: RankedCandidate[];
}> => {
  try {
    const response = await apiClient.get(`/job/${jobId}/candidates`);
    return response.data;
  } catch (error) {
    console.error(`Failed to get candidates for job ${jobId}:`, error);
    throw error;
  }
};

export const clearDatabase = async (): Promise<{ message: string }> => {
  try {
    console.log('Clearing database...');
    const response = await apiClient.delete('/clear-database');
    console.log('Database cleared successfully');
    return response.data;
  } catch (error) {
    console.error('Failed to clear database:', error);
    throw error;
  }
};

// Utility functions
export const formatFileSize = (bytes: number): string => {
  if (bytes === 0) return '0 Bytes';
  
  const k = 1024;
  const sizes = ['Bytes', 'KB', 'MB', 'GB'];
  const i = Math.floor(Math.log(bytes) / Math.log(k));
  
  return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
};

export const getFileIcon = (filename: string): string => {
  const extension = filename.split('.').pop()?.toLowerCase();
  switch (extension) {
    case 'pdf':
      return '📄';
    case 'docx':
    case 'doc':
      return '📝';
    default:
      return '📄';
  }
};

export const getMatchScoreColor = (score: number): string => {
  if (score >= 80) return 'text-green-600 bg-green-50';
  if (score >= 60) return 'text-blue-600 bg-blue-50';
  if (score >= 40) return 'text-yellow-600 bg-yellow-50';
  return 'text-red-600 bg-red-50';
};

export const getMatchScoreBadgeColor = (score: number): string => {
  if (score >= 80) return 'bg-green-100 text-green-800';
  if (score >= 60) return 'bg-blue-100 text-blue-800';
  if (score >= 40) return 'bg-yellow-100 text-yellow-800';
  return 'bg-red-100 text-red-800';
};

export const getMatchLabel = (score: number): string => {
  if (score >= 80) return 'Strong Match';
  if (score >= 60) return 'Good Match';
  if (score >= 40) return 'Partial Match';
  return 'Poor Match';
};