import React, { useState, useCallback } from 'react';
import { FileText, Sparkle, Check } from '@phosphor-icons/react';

interface JobDescriptionInputProps {
  value: string;
  onChange: (value: string) => void;
  disabled?: boolean;
}

const SAMPLE_TEMPLATE = `Senior Software Engineer - Remote

We are seeking an experienced Senior Software Engineer to join our engineering team. The ideal candidate will have 5+ years of experience building scalable web applications.

**Required Skills:**
• 5+ years of professional software development experience
• Strong proficiency in Python or Java
• Experience with web frameworks (Django, Flask, Spring Boot)
• Database experience (PostgreSQL, MySQL)
• RESTful API design and development
• Git version control
• Agile/Scrum methodologies

**Preferred Skills:**
• Frontend experience with React or Vue.js
• Cloud platforms (AWS, GCP, Azure)
• Containerization (Docker, Kubernetes)
• CI/CD pipeline experience
• Test-driven development

**Responsibilities:**
• Design and develop robust, scalable software solutions
• Collaborate with cross-functional teams
• Code reviews and mentor junior developers
• Optimize application performance

**Requirements:**
• Bachelor's degree in Computer Science or related field
• 5+ years of professional development experience
• Strong problem-solving and communication skills`;

const MIN_CHARS = 100;
const MAX_CHARS = 10000;

const JobDescriptionInput: React.FC<JobDescriptionInputProps> = ({
  value,
  onChange,
  disabled = false,
}) => {
  const [copied, setCopied] = useState(false);
  const [wordCount, setWordCount] = useState(0);

  const handleChange = useCallback(
    (e: React.ChangeEvent<HTMLTextAreaElement>) => {
      const v = e.target.value;
      onChange(v);
      setWordCount(v.trim().split(/\s+/).filter(w => w.length > 0).length);
    },
    [onChange]
  );

  const loadTemplate = () => {
    onChange(SAMPLE_TEMPLATE);
    setWordCount(SAMPLE_TEMPLATE.trim().split(/\s+/).filter(w => w.length > 0).length);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  const charCount = value.length;
  const isValid   = charCount >= MIN_CHARS && charCount <= MAX_CHARS;
  const isInvalid = charCount > 0 && !isValid;

  return (
    <div className="space-y-3">
      {/* Header */}
      <div className="flex items-center justify-between">
        <p className="text-xs text-gray-500 dark:text-gray-400">
          Include skills, experience level, and responsibilities.
        </p>
        <button
          type="button"
          onClick={loadTemplate}
          disabled={disabled}
          className="flex items-center gap-1.5 px-2.5 py-1.5 rounded-lg text-xs font-medium text-indigo-600 dark:text-indigo-400 hover:bg-indigo-50 dark:hover:bg-indigo-950/50 transition-colors disabled:opacity-50"
        >
          {copied
            ? <Check size={14} weight="bold" />
            : <Sparkle size={14} weight="duotone" />}
          {copied ? 'Loaded!' : 'Use Template'}
        </button>
      </div>

      {/* Textarea */}
      <div className="relative">
        <textarea
          value={value}
          onChange={handleChange}
          disabled={disabled}
          rows={12}
          placeholder={`Enter job description here…\n\nExample:\nSenior Python Developer - Remote\n\nRequired Skills:\n• Python (5+ years)\n• Django or Flask\n• PostgreSQL\n• AWS\n• Docker`}
          className={[
            'w-full px-4 py-3 rounded-xl border text-sm leading-relaxed',
            'text-black dark:text-white placeholder:text-gray-400 dark:placeholder:text-gray-500',
            'bg-white dark:bg-gray-950/60 resize-y focus:outline-none transition-all',
            'disabled:bg-gray-50 dark:disabled:bg-gray-900 disabled:cursor-not-allowed',
            isInvalid
              ? 'border-red-300 dark:border-red-800 focus:border-red-400 focus:ring-2 focus:ring-red-100 dark:focus:ring-red-950'
              : 'border-gray-200 dark:border-gray-800 focus:border-indigo-400 dark:focus:border-indigo-500 focus:ring-2 focus:ring-indigo-100 dark:focus:ring-indigo-950/40',
          ].join(' ')}
          style={{ minHeight: '260px', maxHeight: '480px' }}
        />
        {/* Counter badge */}
        <div className="absolute bottom-3 right-3 bg-white dark:bg-gray-900 border border-gray-100 dark:border-gray-800 rounded-lg px-2 py-1 text-[10px] text-gray-400 dark:text-gray-500 flex items-center gap-1.5 shadow-sm pointer-events-none">
          <span className={charCount > 0 && (charCount < MIN_CHARS || charCount > MAX_CHARS) ? 'text-red-500 dark:text-red-400' : ''}>
            {charCount}/{MAX_CHARS}
          </span>
          <span className="text-gray-200 dark:text-gray-700">·</span>
          <span>{wordCount}w</span>
        </div>
      </div>

      {/* Validation */}
      {isInvalid && (
        <p className="text-xs text-red-600 dark:text-red-400">
          {charCount < MIN_CHARS
            ? `Add at least ${MIN_CHARS - charCount} more characters`
            : `Remove ${charCount - MAX_CHARS} characters`}
        </p>
      )}

      {/* Guidelines */}
      <div className="bg-indigo-50/70 dark:bg-indigo-950/30 border border-indigo-100 dark:border-indigo-900/50 rounded-xl p-3 flex items-start gap-2">
        <FileText size={16} weight="duotone" className="text-indigo-500 dark:text-indigo-400 mt-0.5 shrink-0" />
        <div className="text-xs text-indigo-900 dark:text-indigo-300">
          <p className="font-semibold mb-1">For best results, include:</p>
          <ul className="space-y-0.5 text-indigo-700 dark:text-indigo-400/90">
            <li>• <strong>Job title</strong> and level (Junior, Senior, Lead)</li>
            <li>• <strong>Required skills</strong> with experience levels</li>
            <li>• <strong>Preferred skills</strong> / nice-to-haves</li>
            <li>• <strong>Key responsibilities</strong></li>
            <li>• <strong>Education</strong> or certification requirements</li>
          </ul>
        </div>
      </div>

      {/* Ready indicator */}
      {value.trim() && isValid && (
        <div className="flex items-center gap-2 text-xs text-emerald-700 dark:text-emerald-300 bg-emerald-50 dark:bg-emerald-950/30 border border-emerald-100 dark:border-emerald-900/50 rounded-xl px-3 py-2">
          <Sparkle size={14} weight="fill" className="text-emerald-500" />
          AI will automatically extract skills and requirements from your description.
        </div>
      )}
    </div>
  );
};

export default JobDescriptionInput;