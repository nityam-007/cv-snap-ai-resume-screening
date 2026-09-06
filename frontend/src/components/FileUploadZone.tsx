import React, { useCallback, useState } from 'react';
import { useDropzone } from 'react-dropzone';
import { UploadSimple, X, FileText, WarningCircle } from '@phosphor-icons/react';
import { formatFileSize, getFileIcon } from '../services/api';

interface FileUploadZoneProps {
  files: File[];
  onFilesChange: (files: File[]) => void;
  disabled?: boolean;
}

const FileUploadZone: React.FC<FileUploadZoneProps> = ({
  files,
  onFilesChange,
  disabled = false,
}) => {
  const [uploadErrors, setUploadErrors] = useState<string[]>([]);

  const onDrop = useCallback(
    (acceptedFiles: File[], rejectedFiles: any[]) => {
      const errors: string[] = [];
      rejectedFiles.forEach(({ file, errors: fileErrors }) => {
        fileErrors.forEach((error: any) => {
          if (error.code === 'file-too-large')         errors.push(`${file.name}: File too large (max 10MB)`);
          else if (error.code === 'file-invalid-type') errors.push(`${file.name}: Only PDF and DOCX accepted`);
          else                                          errors.push(`${file.name}: ${error.message}`);
        });
      });
      const existingNames = new Set(files.map(f => f.name));
      const newFiles = acceptedFiles.filter(file => {
        if (existingNames.has(file.name)) { errors.push(`${file.name}: Already uploaded`); return false; }
        return true;
      });
      if (files.length + newFiles.length > 50) { errors.push('Maximum 50 files allowed'); setUploadErrors(errors); return; }
      setUploadErrors(errors);
      if (newFiles.length > 0) onFilesChange([...files, ...newFiles]);
    },
    [files, onFilesChange]
  );

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: {
      'application/pdf': ['.pdf'],
      'application/vnd.openxmlformats-officedocument.wordprocessingml.document': ['.docx'],
    },
    maxSize: 10 * 1024 * 1024,
    disabled,
    multiple: true,
  });

  const removeFile = (index: number) => {
    onFilesChange(files.filter((_, i) => i !== index));
    if (uploadErrors.length > 0) setUploadErrors([]);
  };

  return (
    <div className="space-y-3">
      {/* Drop Zone */}
      <div
        {...getRootProps()}
        className={[
          'relative border-2 border-dashed rounded-xl p-8 text-center cursor-pointer',
          'transition-all duration-200 select-none',
          isDragActive
            ? 'border-indigo-400 bg-indigo-50 dark:bg-indigo-950/30'
            : 'border-gray-200 dark:border-gray-800 hover:border-indigo-300 dark:hover:border-indigo-700 hover:bg-gray-50 dark:hover:bg-gray-900/40',
          disabled ? 'opacity-50 cursor-not-allowed pointer-events-none' : '',
        ].join(' ')}
      >
        <input {...getInputProps()} />
        <div className="flex flex-col items-center gap-3">
          <div className={`w-12 h-12 rounded-full flex items-center justify-center transition-colors ${isDragActive ? 'bg-indigo-100 dark:bg-indigo-900/50' : 'bg-gray-100 dark:bg-gray-800'}`}>
            <UploadSimple
              size={22}
              weight="bold"
              className={isDragActive ? 'text-indigo-600 dark:text-indigo-400' : 'text-gray-500 dark:text-gray-400'}
            />
          </div>
          <div>
            <p className="text-sm font-medium text-gray-900 dark:text-gray-200">
              {isDragActive ? 'Drop files here' : 'Drag & drop resume files'}
            </p>
            <p className="text-xs text-gray-500 dark:text-gray-400 mt-1">
              or <span className="text-indigo-600 dark:text-indigo-400 font-medium">browse to upload</span>
            </p>
            <p className="text-xs text-gray-400 dark:text-gray-500 mt-2">PDF &amp; DOCX · up to 10MB · max 50 files</p>
          </div>
        </div>
        {disabled && (
          <div className="absolute inset-0 bg-white/70 dark:bg-gray-950/70 rounded-xl flex items-center justify-center">
            <span className="text-sm text-gray-400 dark:text-gray-500">Processing…</span>
          </div>
        )}
      </div>

      {/* Errors */}
      {uploadErrors.length > 0 && (
        <div className="bg-red-50 dark:bg-red-950/30 border border-red-200 dark:border-red-900/50 rounded-xl p-3 flex items-start gap-2">
          <WarningCircle size={16} weight="fill" className="text-red-500 mt-0.5 shrink-0" />
          <div>
            <p className="text-xs font-medium text-red-800 dark:text-red-300 mb-1">Upload errors:</p>
            <ul className="text-xs text-red-700 dark:text-red-400 space-y-0.5">{uploadErrors.map((e, i) => <li key={i}>• {e}</li>)}</ul>
          </div>
        </div>
      )}

      {/* File list */}
      {files.length > 0 && (
        <div className="bg-gray-50 dark:bg-gray-900/60 border border-gray-100 dark:border-gray-800 rounded-xl p-3">
          <div className="flex items-center justify-between mb-2">
            <span className="text-xs font-semibold text-gray-700 dark:text-gray-300 flex items-center gap-1.5">
              <FileText size={14} weight="bold" className="text-indigo-500 dark:text-indigo-400" />
              {files.length} file{files.length !== 1 ? 's' : ''} selected
            </span>
            <button
              onClick={() => { onFilesChange([]); setUploadErrors([]); }}
              disabled={disabled}
              className="text-xs text-red-500 hover:text-red-700 dark:text-red-400 dark:hover:text-red-300 disabled:opacity-50"
            >
              Clear all
            </button>
          </div>
          <div className="space-y-1.5 max-h-44 overflow-y-auto">
            {files.map((file, index) => (
              <div key={`${file.name}-${index}`} className="flex items-center justify-between bg-white dark:bg-gray-950 px-3 py-2 rounded-lg border border-gray-100 dark:border-gray-800">
                <div className="flex items-center gap-2 min-w-0">
                  <span className="text-base shrink-0">{getFileIcon(file.name)}</span>
                  <div className="min-w-0">
                    <p className="text-xs font-medium text-gray-800 dark:text-gray-200 truncate">{file.name}</p>
                    <p className="text-[10px] text-gray-400 dark:text-gray-500">{formatFileSize(file.size)}</p>
                  </div>
                </div>
                <button
                  onClick={() => removeFile(index)}
                  disabled={disabled}
                  className="ml-2 p-1 text-gray-300 dark:text-gray-600 hover:text-red-500 dark:hover:text-red-400 transition-colors disabled:opacity-50 shrink-0"
                >
                  <X size={14} weight="bold" />
                </button>
              </div>
            ))}
          </div>
          <div className="mt-2 flex items-center justify-between">
            <span className="text-[10px] text-gray-400 dark:text-gray-500">
              Total: {formatFileSize(files.reduce((s, f) => s + f.size, 0))}
            </span>
            {files.length >= 50 && (
              <span className="text-[10px] font-semibold text-amber-600 dark:text-amber-400">Max limit reached</span>
            )}
          </div>
        </div>
      )}

      {/* Guidelines */}
      {files.length === 0 && (
        <div className="text-[11px] text-gray-400 dark:text-gray-500 bg-gray-50 dark:bg-gray-900/40 border border-gray-100 dark:border-gray-800/60 rounded-xl p-3 space-y-0.5">
          <p className="font-medium text-gray-500 dark:text-gray-400 mb-1">Accepted formats:</p>
          <p>• PDF and DOCX only · max 10MB per file</p>
          <p>• Up to 50 resumes per batch</p>
          <p>• Text-based files work best (not scanned images)</p>
        </div>
      )}
    </div>
  );
};

export default FileUploadZone;