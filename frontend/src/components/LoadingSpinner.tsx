import React, { useState, useEffect } from 'react';
import { Brain, FileText, Target, CheckCircle, Clock } from 'lucide-react';

const LoadingSpinner: React.FC = () => {
  const [currentStep, setCurrentStep] = useState(0);
  const [progress, setProgress] = useState(0);

  const steps = [
    { icon: FileText, label: 'Parsing documents...', description: 'Extracting text from PDF and DOCX files' },
    { icon: Brain, label: 'Analyzing with AI...', description: 'Using Gemini AI to understand skills and experience' },
    { icon: Target, label: 'Building knowledge graph...', description: 'Creating relationships between candidates and job requirements' },
    { icon: CheckCircle, label: 'Calculating match scores...', description: 'Ranking candidates based on semantic similarity' }
  ];

  useEffect(() => {
    const stepInterval = setInterval(() => {
      setCurrentStep(prev => {
        if (prev < steps.length - 1) {
          return prev + 1;
        }
        return 0; // Loop back to start
      });
    }, 3000); // Change step every 3 seconds

    const progressInterval = setInterval(() => {
      setProgress(prev => {
        if (prev >= 100) {
          return 0; // Reset progress
        }
        return prev + 1;
      });
    }, 100); // Update progress every 100ms

    return () => {
      clearInterval(stepInterval);
      clearInterval(progressInterval);
    };
  }, []);

  return (
    <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-8">
      <div className="max-w-md mx-auto text-center">
        {/* Main spinner */}
        <div className="relative w-24 h-24 mx-auto mb-6">
          {/* Outer rotating ring */}
          <div className="absolute inset-0 border-4 border-gray-200 rounded-full"></div>
          <div className="absolute inset-0 border-4 border-t-blue-600 border-r-transparent border-b-transparent border-l-transparent rounded-full animate-spin"></div>
          
          {/* Inner icon */}
          <div className="absolute inset-0 flex items-center justify-center">
            <div className="w-10 h-10 bg-blue-100 rounded-full flex items-center justify-center">
              <Brain className="w-5 h-5 text-blue-600" />
            </div>
          </div>
        </div>

        {/* Current step */}
        <h3 className="text-xl font-semibold text-gray-900 mb-2">
          Processing Your Resumes
        </h3>
        
        <div className="mb-6">
          <div className="flex items-center justify-center space-x-2 mb-2">
            {React.createElement(steps[currentStep].icon, { 
              className: "w-5 h-5 text-blue-600" 
            })}
            <span className="font-medium text-gray-900">
              {steps[currentStep].label}
            </span>
          </div>
          <p className="text-sm text-gray-600">
            {steps[currentStep].description}
          </p>
        </div>

        {/* Progress bar */}
        <div className="mb-6">
          <div className="w-full bg-gray-200 rounded-full h-2">
            <div 
              className="bg-gradient-to-r from-blue-600 to-indigo-600 h-2 rounded-full transition-all duration-100 ease-out"
              style={{ width: `${progress}%` }}
            ></div>
          </div>
          <div className="flex justify-between text-xs text-gray-500 mt-1">
            <span>Processing...</span>
            <span>{progress}%</span>
          </div>
        </div>

        {/* Step indicators */}
        <div className="flex justify-center space-x-4 mb-6">
          {steps.map((step, index) => {
            const StepIcon = step.icon;
            const isActive = index === currentStep;
            const isCompleted = index < currentStep;
            
            return (
              <div key={index} className="flex flex-col items-center space-y-1">
                <div className={`
                  w-8 h-8 rounded-full flex items-center justify-center transition-all duration-300
                  ${isActive 
                    ? 'bg-blue-600 text-white scale-110' 
                    : isCompleted 
                    ? 'bg-green-100 text-green-600' 
                    : 'bg-gray-100 text-gray-400'
                  }
                `}>
                  {isCompleted ? (
                    <CheckCircle className="w-4 h-4" />
                  ) : (
                    <StepIcon className="w-4 h-4" />
                  )}
                </div>
                <div className={`
                  text-xs font-medium transition-colors duration-300
                  ${isActive ? 'text-blue-600' : isCompleted ? 'text-green-600' : 'text-gray-400'}
                `}>
                  Step {index + 1}
                </div>
              </div>
            );
          })}
        </div>

        {/* Processing tips */}
        <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
          <div className="flex items-start">
            <Clock className="w-5 h-5 text-blue-600 mt-0.5 mr-3 flex-shrink-0" />
            <div className="text-left">
              <h4 className="text-sm font-medium text-blue-900 mb-1">
                What's happening?
              </h4>
              <ul className="text-xs text-blue-800 space-y-1">
                <li>• Extracting text and structure from your resumes</li>
                <li>• AI is analyzing skills, experience, and qualifications</li>
                <li>• Building a knowledge graph of candidate relationships</li>
                <li>• Computing semantic match scores with job requirements</li>
              </ul>
            </div>
          </div>
        </div>

        {/* Estimated time */}
        <div className="mt-4 text-xs text-gray-500">
          <p>This usually takes 30-60 seconds depending on file size and count</p>
          <p className="mt-1">Please keep this tab open while processing...</p>
        </div>
      </div>
    </div>
  );
};

export default LoadingSpinner;