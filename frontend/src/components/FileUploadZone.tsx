import React, { useCallback, useState } from 'react';
import { useDropzone } from 'react-dropzone';
import { Upload, X, FileText, AlertCircle } from 'lucide-react';
import { formatFileSize, getFileIcon } from '../services/api';

interface FileUploadZoneProps {
  files: File[];
  onFilesChange: (files: File[]) => void;
  disabled?: boolean;
}

const FileUploadZone: React.FC<FileUploadZoneProps> = ({ 
  files, 
  onFilesChange, 
  disabled = false 
}) => {
  const [uploadErrors, setUploadErrors] = useState<string[]>([]);

  const onDrop = useCallback((acceptedFiles: File[], rejectedFiles: any[]) => {
    const errors: string[] = [];

    // Handle rejected files
    rejectedFiles.forEach(({ file, errors: fileErrors }) => {
      fileErrors.forEach((error: any) => {
        if (error.code === 'file-too-large') {
          errors.push(`${file.name}: File is too large (max 10MB)`);
        } else if (error.code === 'file-invalid-type') {
          errors.push(`${file.name}: Invalid file type (only PDF and DOCX allowed)`);
        } else {
          errors.push(`${file.name}: ${error.message}`);
        }
      });
    });

    // Check for duplicate files
    const existingFileNames = new Set(files.map(f => f.name));
    const newFiles = acceptedFiles.filter(file => {
      if (existingFileNames.has(file.name)) {
        errors.push(`${file.name}: File already uploaded`);
        return false;
      }
      return true;
    });

    // Check total file count
    if (files.length + newFiles.length > 50) {
      errors.push('Maximum 50 files allowed');
      setUploadErrors(errors);
      return;
    }

    setUploadErrors(errors);
    
    if (newFiles.length > 0) {
      onFilesChange([...files, ...newFiles]);
    }
  }, [files, onFilesChange]);

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: {
      'application/pdf': ['.pdf'],
      'application/vnd.openxmlformats-officedocument.wordprocessingml.document': ['.docx']
    },
    maxSize: 10 * 1024 * 1024, // 10MB
    disabled,
    multiple: true
  });

  const removeFile = (indexToRemove: number) => {
    const newFiles = files.filter((_, index) => index !== indexToRemove);
    onFilesChange(newFiles);
    
    // Clear errors when files are removed
    if (uploadErrors.length > 0) {
      setUploadErrors([]);
    }
  };

  const clearAllFiles = () => {
    onFilesChange([]);
    setUploadErrors([]);
  };

  return (
    <div className="space-y-4">
      {/* Drop Zone */}
      <div
        {...getRootProps()}
        className={`
          relative border-2 border-dashed rounded-lg p-8 text-center cursor-pointer
          transition-all duration-200 ease-in-out
          ${isDragActive 
            ? 'border-blue-400 bg-blue-50 scale-102' 
            : 'border-gray-300 hover:border-gray-400'
          }
          ${disabled ? 'opacity-50 cursor-not-allowed' : 'hover:bg-gray-50'}
        `}
      >
        <input {...getInputProps()} />
        
        <div className="flex flex-col items-center space-y-3">
          <div className={`
            w-12 h-12 rounded-full flex items-center justify-center
            ${isDragActive ? 'bg-blue-100' : 'bg-gray-100'}
          `}>
            <Upload className={`w-6 h-6 ${isDragActive ? 'text-blue-600' : 'text-gray-600'}`} />
          </div>
          
          <div>
            <p className="text-lg font-medium text-gray-900">
              {isDragActive ? 'Drop files here' : 'Upload Resume Files'}
            </p>
            <p className="text-sm text-gray-600 mt-1">
              Drag and drop files here, or click to select files
            </p>
            <p className="text-xs text-gray-500 mt-2">
              Supports PDF and DOCX files up to 10MB each (Max 50 files)
            </p>
          </div>
        </div>

        {/* Loading overlay */}
        {disabled && (
          <div className="absolute inset-0 bg-white bg-opacity-75 rounded-lg flex items-center justify-center">
            <div className="text-gray-500">Processing...</div>
          </div>
        )}
      </div>

      {/* Upload Errors */}
      {uploadErrors.length > 0 && (
        <div className="bg-red-50 border border-red-200 rounded-lg p-4">
          <div className="flex items-start">
            <AlertCircle className="w-5 h-5 text-red-600 mt-0.5 mr-2 flex-shrink-0" />
            <div className="flex-1">
              <h4 className="text-sm font-medium text-red-800">Upload Errors:</h4>
              <ul className="mt-2 text-sm text-red-700 space-y-1">
                {uploadErrors.map((error, index) => (
                  <li key={index}>• {error}</li>
                ))}
              </ul>
            </div>
          </div>
        </div>
      )}

      {/* Uploaded Files */}
      {files.length > 0 && (
        <div className="bg-gray-50 rounded-lg p-4">
          <div className="flex items-center justify-between mb-3">
            <h4 className="font-medium text-gray-900 flex items-center">
              <FileText className="w-4 h-4 mr-2" />
              Uploaded Files ({files.length})
            </h4>
            <button
              onClick={clearAllFiles}
              disabled={disabled}
              className="text-sm text-red-600 hover:text-red-700 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              Clear All
            </button>
          </div>
          
          <div className="grid gap-2 max-h-48 overflow-y-auto">
            {files.map((file, index) => (
              <div
                key={`${file.name}-${index}`}
                className="flex items-center justify-between bg-white rounded-lg p-3 border border-gray-200"
              >
                <div className="flex items-center space-x-3 flex-1 min-w-0">
                  <span className="text-lg flex-shrink-0">
                    {getFileIcon(file.name)}
                  </span>
                  <div className="flex-1 min-w-0">
                    <p className="text-sm font-medium text-gray-900 truncate">
                      {file.name}
                    </p>
                    <p className="text-xs text-gray-500">
                      {formatFileSize(file.size)}
                    </p>
                  </div>
                </div>
                
                <button
                  onClick={() => removeFile(index)}
                  disabled={disabled}
                  className="ml-2 p-1 text-gray-400 hover:text-red-600 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
                  title="Remove file"
                >
                  <X className="w-4 h-4" />
                </button>
              </div>
            ))}
          </div>

          {/* File Count Summary */}
          <div className="mt-3 text-xs text-gray-600 flex items-center justify-between">
            <span>
              Total: {files.length} files ({formatFileSize(files.reduce((sum, file) => sum + file.size, 0))})
            </span>
            {files.length >= 50 && (
              <span className="text-amber-600 font-medium">
                Maximum file limit reached
              </span>
            )}
          </div>
        </div>
      )}

      {/* File Guidelines */}
      {files.length === 0 && (
        <div className="text-xs text-gray-500 bg-gray-50 rounded-lg p-3">
          <p className="font-medium mb-1">Guidelines:</p>
          <ul className="space-y-1">
            <li>• Only PDF and DOCX files are accepted</li>
            <li>• Maximum file size: 10MB per file</li>
            <li>• Maximum total files: 50</li>
            <li>• Ensure resumes contain text (scanned images may not work well)</li>
            <li>• Best results with standard resume formats</li>
          </ul>
        </div>
      )}
    </div>
  );
};

export default FileUploadZone;