import React, { useState } from 'react';
import './App.css';

interface Candidate {
  candidate_id: string;
  name: string;
  email: string;
  match_score: number;
  explanation: string;
}

interface Results {
  job_id: string;
  job_info: {
    title: string;
  };
  ranked_candidates: Candidate[];
}

const App: React.FC = () => {
  const [jobDescription, setJobDescription] = useState('');
  const [files, setFiles] = useState<FileList | null>(null);
  const [results, setResults] = useState<Results | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setFiles(e.target.files);
  };

  const handleAnalyze = async () => {
    if (!jobDescription.trim()) {
      setError('Please enter a job description');
      return;
    }
    if (!files || files.length === 0) {
      setError('Please upload at least one resume');
      return;
    }

    setLoading(true);
    setError(null);

    try {
      const formData = new FormData();
      formData.append('job_description', jobDescription);
      
      for (let i = 0; i < files.length; i++) {
        formData.append('resume_files', files[i]);
      }

      const response = await fetch('http://localhost:8000/analyze', {
        method: 'POST',
        body: formData,
      });

      if (!response.ok) {
        throw new Error(`Server error: ${response.status}`);
      }

      const data = await response.json();
      setResults(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Analysis failed');
    } finally {
      setLoading(false);
    }
  };

  const handleSampleData = async () => {
    setLoading(true);
    setError(null);

    try {
      const response = await fetch('http://localhost:8000/analyze-sample', {
        method: 'POST',
      });

      if (!response.ok) {
        throw new Error(`Server error: ${response.status}`);
      }

      const data = await response.json();
      setResults(data);
      setJobDescription('Sample Job: Senior Python Developer with 5+ years experience...');
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Sample data failed to load');
    } finally {
      setLoading(false);
    }
  };

  const handleReset = () => {
    setJobDescription('');
    setFiles(null);
    setResults(null);
    setError(null);
  };

  return (
    <div className="app">
      <header className="app-header">
        <h1>🧠 CV.Snap</h1>
        <p>AI-Powered Resume Screening Assistant</p>
      </header>

      <main className="app-main">
        {error && (
          <div className="error-message">
            <strong>Error:</strong> {error}
          </div>
        )}

        {!results && (
          <div className="input-section">
            <div className="input-group" style={{width:"98%",}}>
              <h2><b>📄 Job Description</b></h2>
              <textarea
                value={jobDescription}
                onChange={(e) => setJobDescription(e.target.value)}
                placeholder="Enter job description here...

Example:
Senior Python Developer - Remote
We are looking for an experienced Python developer with 5+ years of experience.

Required Skills:
• Python (5+ years)
• Django or Flask
• PostgreSQL
• AWS
• Docker"
                rows={10}
                disabled={loading}
              />
            </div>

            <div className="input-group" style={{width:"98%"}}>
              <h2>📁 Upload Resumes</h2>
              <input
                type="file"
                accept=".pdf,.docx"
                multiple
                onChange={handleFileChange}
                disabled={loading}
              />
              {files && (
                <div className="file-list">
                  <p>Selected files: {files.length}</p>
                  {Array.from(files).map((file, index) => (
                    <div key={index} className="file-item">
                      📄 {file.name} ({Math.round(file.size / 1024)}KB)
                    </div>
                  ))}
                </div>
              )}
            </div>

            <div className="button-group">
              <button
                onClick={handleAnalyze}
                disabled={loading}
                className="analyze-button"
              >
                {loading ? 'Analyzing...' : '🎯 Analyze & Rank Candidates'}
              </button>

              <button
                onClick={handleSampleData}
                disabled={loading}
                className="sample-button"
              >
                📊 Try Sample Data
              </button>
            </div>
          </div>
        )}

        {loading && (
          <div className="loading-section">
            <div className="spinner"></div>
            <h3>Processing Your Resumes...</h3>
            <p>This may take 30-60 seconds depending on file size and count</p>
            <div className="loading-steps">
              <div>📄 Parsing documents...</div>
              <div>🧠 Analyzing with AI...</div>
              <div>🎯 Building knowledge graph...</div>
              <div>✅ Calculating match scores...</div>
            </div>
          </div>
        )}

        {results && !loading && (
          <div className="results-section">
            <div className="results-header">
              <h2>📈 Analysis Results</h2>
              <p>Job: {results.job_info.title}</p>
              <button onClick={handleReset} className="reset-button">
                🔄 New Analysis
              </button>
            </div>

            <div className="candidates-table">
              <table>
                <thead>
                  <tr>
                    <th>Rank</th>
                    <th>Candidate</th>
                    <th>Match Score</th>
                    <th>Explanation</th>
                  </tr>
                </thead>
                <tbody>
                  {results.ranked_candidates.map((candidate, index) => (
                    <tr key={candidate.candidate_id}>
                      <td>
                        <span className="rank">#{index + 1}</span>
                      </td>
                      <td>
                        <div className="candidate-info">
                          <div className="name">{candidate.name}</div>
                          <div className="email">{candidate.email}</div>
                        </div>
                      </td>
                      <td>
                        <div className="score-container">
                          <div className={`score ${getScoreClass(candidate.match_score)}`}>
                            {candidate.match_score.toFixed(1)}%
                          </div>
                          <div className="progress-bar">
                            <div
                              className="progress-fill"
                              style={{ width: `${candidate.match_score}%` }}
                            ></div>
                          </div>
                        </div>
                      </td>
                      <td>
                        <div className="explanation">
                          {candidate.explanation.replace(/\*\*(.*?)\*\*/g, '$1')}
                        </div>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        )}
      </main>
    </div>
  );
};

function getScoreClass(score: number): string {
  if (score >= 80) return 'excellent';
  if (score >= 60) return 'good';
  if (score >= 40) return 'fair';
  return 'poor';
}

export default App;