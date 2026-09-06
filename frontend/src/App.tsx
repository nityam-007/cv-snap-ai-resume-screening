import React, { useState, useEffect } from "react";
import "./App.css";
import { Button } from "@heroui/react";
import {
  MagnifyingGlass,
  Database,
  ArrowCounterClockwise,
  Moon,
  Sun,
} from "@phosphor-icons/react";
import ResultsTable from "./components/ResultsTable";
import FileUploadZone from "./components/FileUploadZone";
import JobDescriptionInput from "./components/JobDescriptionInput";

interface Candidate {
  candidate_id: string;
  name: string;
  email: string;
  match_score: number;
  skill_coverage?: number;
  matched_skills?: number;
  total_required_skills?: number;
  explanation: string;
}

interface Results {
  job_id: string;
  job_info: {
    title: string;
    total_required_skills?: number;
    experience_level?: string;
  };
  total_resumes?: number;
  successfully_processed?: number;
  processing_errors?: { filename: string; error: string }[];
  ranked_candidates: Candidate[];
  processing_time?: string;
}

const App: React.FC = () => {
  const [jobDescription, setJobDescription] = useState("");
  const [files, setFiles] = useState<File[]>([]);
  const [results, setResults] = useState<Results | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // Dark mode state with localStorage persistence and system preference check
  const [darkMode, setDarkMode] = useState<boolean>(() => {
    const saved = localStorage.getItem("cvsnap-theme");
    if (saved) return saved === "dark";
    return window.matchMedia("(prefers-color-scheme: dark)").matches;
  });

  useEffect(() => {
    const root = document.documentElement;
    if (darkMode) {
      root.classList.add("dark");
      localStorage.setItem("cvsnap-theme", "dark");
    } else {
      root.classList.remove("dark");
      localStorage.setItem("cvsnap-theme", "light");
    }
  }, [darkMode]);

  const handleAnalyze = async () => {
    if (!jobDescription.trim()) { setError("Please enter a job description"); return; }
    if (files.length === 0)     { setError("Please upload at least one resume"); return; }
    setLoading(true); setError(null);
    try {
      const formData = new FormData();
      formData.append("job_description", jobDescription);
      files.forEach(f => formData.append("resume_files", f));
      const response = await fetch("http://localhost:8000/analyze", { method: "POST", body: formData });
      if (!response.ok) throw new Error(`Server error: ${response.status}`);
      setResults(await response.json());
    } catch (err) {
      setError(err instanceof Error ? err.message : "Analysis failed");
    } finally { setLoading(false); }
  };

  const handleSampleData = async () => {
    setLoading(true); setError(null);
    try {
      const response = await fetch("http://localhost:8000/analyze-sample", { method: "POST" });
      if (!response.ok) throw new Error(`Server error: ${response.status}`);
      setResults(await response.json());
      setJobDescription("Sample Job: Senior Python Developer with 5+ years experience...");
    } catch (err) {
      setError(err instanceof Error ? err.message : "Sample data failed to load");
    } finally { setLoading(false); }
  };

  const handleReset = () => {
    setJobDescription(""); setFiles([]); setResults(null); setError(null);
  };

  const loadingSteps = [
    "Parsing documents",
    "AI extraction",
    "Building knowledge graph",
    "Calculating scores",
  ];

  return (
    <div className="min-h-screen bg-white dark:bg-[#0b0f19] text-gray-900 dark:text-gray-100 transition-colors duration-200">

      {/* ── Navbar ── */}
      <header className="sticky top-0 z-40 bg-white/80 dark:bg-[#0b0f19]/80 backdrop-blur-md border-b border-gray-100 dark:border-gray-800 transition-colors">
        <div className="max-w-6xl mx-auto px-4 sm:px-6 h-14 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <span className="font-bold text-indigo-600 dark:text-indigo-400 text-xl tracking-tight">CV.Snap</span>
            <span className="text-gray-300 dark:text-gray-700 hidden sm:block">|</span>
            <span className="text-gray-400 dark:text-gray-500 text-sm hidden sm:block">AI-Powered Resume Screening</span>
          </div>

          <div className="flex items-center gap-2">
            {/* Theme Toggle */}
            <button
              onClick={() => setDarkMode(!darkMode)}
              className="p-2 rounded-xl text-gray-500 dark:text-gray-400 hover:text-indigo-600 dark:hover:text-indigo-400 hover:bg-gray-100 dark:hover:bg-gray-800/80 transition-colors"
              title={darkMode ? "Switch to Light Mode" : "Switch to Dark Mode"}
              aria-label="Toggle theme"
            >
              {darkMode ? (
                <Sun size={20} weight="bold" className="text-amber-400" />
              ) : (
                <Moon size={20} weight="bold" />
              )}
            </button>

            {results && !loading && (
              <Button
                variant="flat"
                color="primary"
                size="sm"
                onPress={handleReset}
                startContent={<ArrowCounterClockwise size={15} weight="bold" />}
                className="font-medium dark:bg-indigo-950/50 dark:text-indigo-300 dark:hover:bg-indigo-900/50"
              >
                New Analysis
              </Button>
            )}
          </div>
        </div>
      </header>

      {/* ── Main Content ── */}
      <main className="page-content">

        {/* Error Banner */}
        {error && (
          <div className="mb-6 px-4 py-3 rounded-xl bg-red-50 dark:bg-red-950/40 border border-red-200 dark:border-red-900/60 text-red-700 dark:text-red-300 text-sm fade-in">
            <strong>Error:</strong> {error}
          </div>
        )}

        {/* ── Input Section ── */}
        {!results && !loading && (
          <div className="fade-in">
            <div className="text-center mb-10">
              <h1 className="text-3xl font-bold text-gray-900 dark:text-white mb-2">
                Screen Resumes with AI
              </h1>
              <p className="text-gray-500 dark:text-gray-400 text-base">
                Paste a job description, upload resumes, and get ranked candidates in seconds.
              </p>
            </div>

            <div className="input-grid">
              {/* Job Description */}
              <div className="bg-white dark:bg-gray-900/60 border border-gray-100 dark:border-gray-800/80 rounded-2xl shadow-sm p-6 backdrop-blur-sm">
                <h2 className="text-base font-semibold text-gray-800 dark:text-gray-200 mb-4">Job Description</h2>
                <JobDescriptionInput value={jobDescription} onChange={setJobDescription} disabled={loading} />
              </div>

              {/* File Upload */}
              <div className="bg-white dark:bg-gray-900/60 border border-gray-100 dark:border-gray-800/80 rounded-2xl shadow-sm p-6 backdrop-blur-sm">
                <h2 className="text-base font-semibold text-gray-800 dark:text-gray-200 mb-4">Upload Resumes</h2>
                <FileUploadZone files={files} onFilesChange={setFiles} disabled={loading} />
              </div>
            </div>

            {/* ── Action Buttons ── */}
            <div className="flex gap-4 justify-center flex-wrap">
              <Button
                color="primary"
                size="lg"
                onPress={handleAnalyze}
                isLoading={loading}
                startContent={!loading ? <MagnifyingGlass size={20} weight="bold" /> : undefined}
                className="min-w-[230px] font-semibold bg-indigo-600 hover:bg-indigo-700 text-white shadow-md shadow-indigo-200 dark:shadow-indigo-950"
              >
                Analyze &amp; Rank Candidates
              </Button>

              <Button
                variant="bordered"
                size="lg"
                onPress={handleSampleData}
                isDisabled={loading}
                startContent={<Database size={20} weight="duotone" />}
                className="min-w-[190px] font-semibold border-2 border-indigo-200 dark:border-indigo-800 text-indigo-600 dark:text-indigo-400 hover:bg-indigo-50 dark:hover:bg-indigo-950/40 hover:border-indigo-400 dark:hover:border-indigo-700"
              >
                Try Sample Data
              </Button>
            </div>
          </div>
        )}

        {/* ── Loading Section ── */}
        {loading && (
          <div className="fade-in flex justify-center">
            <div className="bg-white dark:bg-gray-900/80 border border-gray-100 dark:border-gray-800 rounded-2xl shadow-sm w-full max-w-md px-8 py-12 text-center">
              <div className="flex justify-center mb-5">
                <div className="w-12 h-12 rounded-full border-4 border-indigo-100 dark:border-gray-800 border-t-indigo-600 animate-spin" />
              </div>
              <h3 className="text-lg font-semibold text-gray-900 dark:text-white">Analyzing Resumes…</h3>
              <p className="text-sm text-gray-500 dark:text-gray-400 mt-1 mb-8">This may take 30–60 seconds</p>
              <div className="flex flex-col gap-3">
                {loadingSteps.map((step, i) => (
                  <div key={step} className="loading-step justify-center">
                    <span className="step-dot" style={{ animationDelay: `${i * 0.35}s` }} />
                    <span>{step}</span>
                  </div>
                ))}
              </div>
            </div>
          </div>
        )}

        {/* ── Results Section ── */}
        {results && !loading && (
          <div className="fade-in">
            <ResultsTable results={results} onReset={handleReset} />
          </div>
        )}

      </main>
    </div>
  );
};

export default App;
