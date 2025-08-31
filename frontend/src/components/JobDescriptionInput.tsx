import React, { useState, useCallback } from 'react';
import { FileText, Sparkles, Copy, Check } from 'lucide-react';

interface JobDescriptionInputProps {
  value: string;
  onChange: (value: string) => void;
  disabled?: boolean;
}

const JobDescriptionInput: React.FC<JobDescriptionInputProps> = ({ 
  value, 
  onChange, 
  disabled = false 
}) => {
  const [copied, setCopied] = useState(false);
  const [wordCount, setWordCount] = useState(0);

  const handleInputChange = useCallback((e: React.ChangeEvent<HTMLTextAreaElement>) => {
    const newValue = e.target.value;
    onChange(newValue);
    
    // Calculate word count
    const words = newValue.trim().split(/\s+/).filter(word => word.length > 0);
    setWordCount(words.length);
  }, [onChange]);

  const handleCopyTemplate = () => {
    const template = `Senior Software Engineer - Remote

We are seeking an experienced Senior Software Engineer to join our dynamic engineering team. The ideal candidate will have 5+ years of experience building scalable web applications and a passion for clean, maintainable code.

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
• Machine Learning or Data Science background

**Responsibilities:**
• Design and develop robust, scalable software solutions
• Collaborate with cross-functional teams to define and implement new features
• Code reviews and mentor junior developers
• Optimize application performance and troubleshoot issues
• Participate in architectural decisions and technical planning

**Requirements:**
• Bachelor's degree in Computer Science or related field
• 5+ years of professional development experience
• Strong problem-solving and analytical thinking skills
• Excellent communication and teamwork abilities
• Self-motivated with ability to work independently

**What We Offer:**
• Competitive salary and equity package
• Flexible remote work arrangements
• Professional development budget
• Health, dental, and vision insurance
• 401k with company matching`;

    navigator.clipboard.writeText(template).then(() => {
      onChange(template);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    });
  };

  // Calculate character count for validation
  const charCount = value.length;
  const minChars = 100;
  const maxChars = 10000;
  const isValidLength = charCount >= minChars && charCount <= maxChars;

  return (
    <div className="space-y-4">
      {/* Header with template button */}
      <div className="flex items-center justify-between">
        <div>
          <label htmlFor="job-description" className="block text-sm font-medium text-gray-700 mb-1">
            Job Description *
          </label>
          <p className="text-xs text-gray-500">
            Provide a detailed job description including required skills, experience level, and responsibilities
          </p>
        </div>
        
        <button
          type="button"
          onClick={handleCopyTemplate}
          disabled={disabled}
          className="flex items-center space-x-2 px-3 py-2 text-sm text-blue-600 hover:text-blue-700 hover:bg-blue-50 rounded-lg transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
          title="Use sample job description"
        >
          {copied ? (
            <>
              <Check className="w-4 h-4" />
              <span>Copied!</span>
            </>
          ) : (
            <>
              <Sparkles className="w-4 h-4" />
              <span>Use Template</span>
            </>
          )}
        </button>
      </div>

      {/* Text Area */}
      <div className="relative">
        <textarea
          id="job-description"
          value={value}
          onChange={handleInputChange}
          disabled={disabled}
          placeholder="Enter job description here...

Example:
Senior Python Developer - Remote

We are looking for an experienced Python developer with 5+ years of experience.

Required Skills:
• Python (5+ years)
• Django or Flask
• PostgreSQL
• AWS
• Docker

Responsibilities:
• Build scalable web applications
• Design APIs
• Mentor junior developers..."
          className={`
            w-full min-h-[300px] px-4 py-3 border rounded-lg resize-y
            focus:ring-2 focus:ring-blue-500 focus:border-blue-500
            disabled:bg-gray-50 disabled:cursor-not-allowed
            transition-colors duration-200
            ${!isValidLength && charCount > 0 
              ? 'border-red-300 focus:ring-red-500 focus:border-red-500' 
              : 'border-gray-300'
            }
          `}
          style={{ maxHeight: '500px' }}
        />
        
        {/* Character/Word count */}
        <div className="absolute bottom-3 right-3 text-xs text-gray-500 bg-white px-2 py-1 rounded border">
          <div className="flex items-center space-x-2">
            <span>{wordCount} words</span>
            <span>•</span>
            <span className={charCount < minChars ? 'text-red-500' : charCount > maxChars ? 'text-red-500' : ''}>
              {charCount}/{maxChars} chars
            </span>
          </div>
        </div>
      </div>

      {/* Validation Messages */}
      {charCount > 0 && !isValidLength && (
        <div className="text-sm">
          {charCount < minChars ? (
            <p className="text-red-600">
              Job description too short. Please add at least {minChars - charCount} more characters.
            </p>
          ) : (
            <p className="text-red-600">
              Job description too long. Please remove {charCount - maxChars} characters.
            </p>
          )}
        </div>
      )}

      {/* Guidelines */}
      <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
        <div className="flex items-start">
          <FileText className="w-5 h-5 text-blue-600 mt-0.5 mr-3 flex-shrink-0" />
          <div className="text-sm text-blue-800">
            <p className="font-medium mb-2">For best results, include:</p>
            <ul className="space-y-1">
              <li>• <strong>Job title</strong> and level (Junior, Mid, Senior, Lead)</li>
              <li>• <strong>Required skills</strong> with experience levels</li>
              <li>• <strong>Preferred skills</strong> or nice-to-have technologies</li>
              <li>• <strong>Key responsibilities</strong> and day-to-day tasks</li>
              <li>• <strong>Experience requirements</strong> (years, specific domains)</li>
              <li>• <strong>Education</strong> or certification requirements</li>
            </ul>
            <p className="mt-2 text-xs text-blue-600">
              💡 The more detailed your job description, the more accurate the matching will be!
            </p>
          </div>
        </div>
      </div>

      {/* AI Enhancement Notice */}
      {value.trim() && isValidLength && (
        <div className="bg-green-50 border border-green-200 rounded-lg p-3">
          <div className="flex items-center text-sm text-green-800">
            <Sparkles className="w-4 h-4 mr-2" />
            <span>
              Great! Our AI will extract skills, requirements, and preferences from your job description automatically.
            </span>
          </div>
        </div>
      )}
    </div>
  );
};

export default JobDescriptionInput;