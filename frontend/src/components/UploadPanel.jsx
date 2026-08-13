import React, { useState } from 'react';
import { Upload, FileText, Image, Table, Play, CheckCircle2, Sparkles } from 'lucide-react';
import { uploadFiles, startPipeline, loadSampleBatch } from '../api';

export default function UploadPanel({ onPipelineStarted }) {
  const [selectedFiles, setSelectedFiles] = useState([]);
  const [isUploading, setIsUploading] = useState(false);
  const [uploadedSources, setUploadedSources] = useState([]);

  const handleFileChange = (e) => {
    if (e.target.files && e.target.files.length > 0) {
      setSelectedFiles(Array.from(e.target.files));
    }
  };

  const handleUploadAndRun = async () => {
    if (selectedFiles.length === 0) {
      handleLoadSample();
      return;
    }

    setIsUploading(true);
    try {
      const uploadRes = await uploadFiles(selectedFiles);
      setUploadedSources(uploadRes.uploaded_sources);
      const sourceIds = uploadRes.uploaded_sources.map(s => s.source_id);
      
      const pipelineRes = await startPipeline(sourceIds);
      onPipelineStarted(pipelineRes.job_id);
    } catch (err) {
      console.error('Error starting pipeline:', err);
      alert('Failed to run pipeline: ' + err.message);
    } finally {
      setIsUploading(false);
    }
  };

  const handleLoadSample = async () => {
    setIsUploading(true);
    try {
      const sampleRes = await loadSampleBatch();
      onPipelineStarted(sampleRes.job_id);
    } catch (err) {
      console.error('Error loading sample batch:', err);
      alert('Failed to load sample batch: ' + err.message);
    } finally {
      setIsUploading(false);
    }
  };

  const getIconForType = (name) => {
    const ext = name.split('.').pop().toLowerCase();
    if (ext === 'pdf') return <FileText size={18} className="text-red-400" />;
    if (['png', 'jpg', 'jpeg'].includes(ext)) return <Image size={18} className="text-blue-400" />;
    if (ext === 'csv') return <Table size={18} className="text-green-400" />;
    return <FileText size={18} />;
  };

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
      {/* Sample Batch Quick Button */}
      <button
        onClick={handleLoadSample}
        disabled={isUploading}
        style={{
          background: 'linear-gradient(135deg, rgba(6, 182, 212, 0.2), rgba(59, 130, 246, 0.2))',
          border: '1px solid rgba(6, 182, 212, 0.5)',
          color: '#38bdf8',
          borderRadius: '8px',
          padding: '10px 14px',
          fontWeight: 600,
          fontSize: '0.85rem',
          cursor: isUploading ? 'not-allowed' : 'pointer',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          gap: '8px',
          boxShadow: '0 0 15px rgba(6, 182, 212, 0.15)',
          transition: 'all 0.2s ease'
        }}
      >
        <Sparkles size={16} />
        {isUploading ? 'Ingesting Sample Batch...' : 'Load Sample Batch (PDF + Image + CSV)'}
      </button>

      <div 
        className="upload-dropzone"
        onClick={() => document.getElementById('file-input').click()}
      >
        <Upload size={32} style={{ margin: '0 auto 8px', color: '#60a5fa' }} />
        <div style={{ fontSize: '0.9rem', fontWeight: 600 }}>
          {selectedFiles.length > 0 ? `${selectedFiles.length} file(s) selected` : 'Drop Datasheets, Nameplates or CSV'}
        </div>
        <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)', marginTop: 4 }}>
          Supports PDF, JPG/PNG, CSV
        </div>
        <input 
          id="file-input"
          type="file" 
          multiple 
          accept=".pdf,.png,.jpg,.jpeg,.csv" 
          onChange={handleFileChange}
          style={{ display: 'none' }}
        />
      </div>

      {selectedFiles.length > 0 && (
        <div style={{ display: 'flex', flexDirection: 'column', gap: 6 }}>
          {selectedFiles.map((f, i) => (
            <div key={i} style={{ 
              display: 'flex', 
              alignItems: 'center', 
              gap: 8, 
              padding: '6px 10px', 
              background: 'rgba(255,255,255,0.03)', 
              borderRadius: 6,
              fontSize: '0.8rem'
            }}>
              {getIconForType(f.name)}
              <span style={{ flex: 1, overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>{f.name}</span>
              <CheckCircle2 size={14} style={{ color: '#10b981' }} />
            </div>
          ))}
        </div>
      )}

      <button 
        className="btn-primary"
        onClick={handleUploadAndRun}
        disabled={isUploading}
      >
        <Play size={16} />
        {isUploading ? 'Uploading Sources...' : selectedFiles.length > 0 ? 'Run Intelligence Pipeline' : 'Run Pipeline on Selected Files'}
      </button>
    </div>
  );
}
