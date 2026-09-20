'use client';

import React, { useState, useRef } from 'react';
import { Upload, FileText, Loader2, CheckCircle2, AlertCircle } from 'lucide-react';
import { api } from '../lib/api';

interface FileUploadProps {
  onUploadSuccess: (docId: string) => void;
}

export const FileUpload: React.FC<FileUploadProps> = ({ onUploadSuccess }) => {
  const [isDragging, setIsDragging] = useState(false);
  const [uploading, setUploading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const handleFile = async (file: File) => {
    setError(null);
    setUploading(true);

    try {
      const res = await api.uploadDocument(file);
      onUploadSuccess(res.id);
    } catch (err: any) {
      setError(err.message || 'Upload failed. Please try again.');
    } finally {
      setUploading(false);
    }
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(false);
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      handleFile(e.dataTransfer.files[0]);
    }
  };

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      handleFile(e.target.files[0]);
    }
  };

  return (
    <div className="w-full">
      <div
        onDragOver={(e) => {
          e.preventDefault();
          setIsDragging(true);
        }}
        onDragLeave={() => setIsDragging(false)}
        onDrop={handleDrop}
        onClick={() => fileInputRef.current?.click()}
        className={`relative border-2 border-dashed rounded-2xl p-8 text-center cursor-pointer transition-all duration-300 ${
          isDragging
            ? 'border-indigo-500 bg-indigo-950/30 scale-[1.01]'
            : 'border-slate-800 hover:border-indigo-500/60 bg-slate-900/40 hover:bg-slate-900/80'
        }`}
      >
        <input
          ref={fileInputRef}
          type="file"
          accept=".pdf,.docx,.txt"
          onChange={handleChange}
          className="hidden"
        />

        <div className="flex flex-col items-center justify-center gap-3">
          {uploading ? (
            <>
              <div className="w-12 h-12 rounded-2xl bg-indigo-950 border border-indigo-500/40 flex items-center justify-center">
                <Loader2 className="w-6 h-6 text-indigo-400 animate-spin" />
              </div>
              <div>
                <p className="text-sm font-semibold text-slate-200">Processing & Structuring Document...</p>
                <p className="text-xs text-slate-400 mt-1">Multi-agent analysis, chunking, and vector indexing in progress</p>
              </div>
            </>
          ) : (
            <>
              <div className="w-14 h-14 rounded-2xl bg-slate-800/80 border border-slate-700/60 flex items-center justify-center group-hover:scale-105 transition-transform">
                <Upload className="w-7 h-7 text-indigo-400" />
              </div>
              <div>
                <p className="text-base font-semibold text-slate-100">
                  Drop your legal document here, or <span className="text-indigo-400 underline underline-offset-2">browse</span>
                </p>
                <p className="text-xs text-slate-400 mt-1">
                  Supports PDF, DOCX, TXT (up to 20MB) • Employment contracts, NDAs, Leases, Vendor Agreements, Terms of Service
                </p>
              </div>
            </>
          )}
        </div>
      </div>

      {error && (
        <div className="mt-3 p-3 bg-red-950/50 border border-red-800/50 rounded-xl text-red-300 text-xs flex items-center gap-2">
          <AlertCircle className="w-4 h-4 shrink-0" />
          <span>{error}</span>
        </div>
      )}
    </div>
  );
};
