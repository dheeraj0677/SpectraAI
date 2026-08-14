import React, { useEffect, useState } from 'react';
import { Loader2, CheckCircle2, AlertCircle, RefreshCw, XCircle } from 'lucide-react';

const STAGES = [
  { id: 'ingestion', label: '1. Ingestion & SHA-256 Hashes' },
  { id: 'extraction', label: '2. Multimodal Extraction (VLM/OCR/PDF)' },
  { id: 'merging', label: '3. Concordance & Conflict Scoring' },
  { id: 'enrichment', label: '4. Seed KB & Taxonomy Classification' },
  { id: 'knowledge_graph', label: '5. NetworkX Graph Expansion' },
  { id: 'validation', label: '6. Business Rules & CRI Scoring' },
];

export default function PipelineStatus({ jobId, onComplete, onRetry }) {
  const [status, setStatus] = useState({ 
    stage: 'starting', 
    percent: 0, 
    message: 'Connecting to pipeline SSE stream...', 
    error: null 
  });
  const [hasFailed, setHasFailed] = useState(false);

  useEffect(() => {
    if (!jobId) return;

    setHasFailed(false);
    const eventSource = new EventSource(`http://localhost:8000/api/pipeline/status/${jobId}`);

    eventSource.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data);
        if (data.ping) return;

        setStatus(data);

        if (data.stage === 'failed') {
          setHasFailed(true);
          eventSource.close();
        } else if (data.stage === 'complete') {
          eventSource.close();
          if (onComplete) onComplete();
        }
      } catch (e) {
        console.error('Error parsing SSE event', e);
      }
    };

    eventSource.onerror = (err) => {
      console.error('SSE connection error:', err);
      // Don't auto-fail immediately on network blip, but log it
    };

    return () => {
      eventSource.close();
    };
  }, [jobId, onComplete]);

  const isFailed = status.stage === 'failed' || hasFailed;

  return (
    <div style={{ background: 'rgba(0,0,0,0.25)', padding: 14, borderRadius: 10, marginTop: 12, border: '1px solid var(--panel-border)' }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 8 }}>
        <span style={{ fontSize: '0.85rem', fontWeight: 600, color: isFailed ? '#f87171' : 'var(--accent-cyan)', display: 'flex', alignItems: 'center', gap: 6 }}>
          {isFailed ? <XCircle size={15} /> : <Loader2 size={15} className={status.percent < 100 ? "animate-spin" : ""} />}
          {isFailed ? 'Pipeline Execution Error' : 'Live Pipeline Engine'}
        </span>
        <span style={{ fontSize: '0.75rem', fontWeight: 700, color: isFailed ? '#f87171' : '#fff' }}>
          {isFailed ? 'FAILED' : `${status.percent}%`}
        </span>
      </div>

      {/* Progress Bar */}
      <div style={{ height: 6, width: '100%', background: 'rgba(255,255,255,0.08)', borderRadius: 3, overflow: 'hidden', marginBottom: 12 }}>
        <div 
          style={{ 
            height: '100%', 
            width: `${status.percent}%`, 
            background: isFailed ? 'linear-gradient(90deg, #ef4444, #f87171)' : 'linear-gradient(90deg, #3b82f6, #06b6d4)', 
            transition: 'width 0.3s ease' 
          }} 
        />
      </div>

      {/* Stages List */}
      <div style={{ display: 'flex', flexDirection: 'column', gap: 6 }}>
        {STAGES.map((stg) => {
          const isDone = status.percent === 100 || getStageRank(status.stage) > getStageRank(stg.id);
          const isCurrent = status.stage === stg.id;
          const isCurrentFailed = isFailed && isCurrent;

          return (
            <div key={stg.id} style={{ display: 'flex', alignItems: 'center', gap: 8, fontSize: '0.75rem' }}>
              {isCurrentFailed ? (
                <AlertCircle size={14} style={{ color: '#ef4444' }} />
              ) : isDone ? (
                <CheckCircle2 size={14} style={{ color: '#10b981' }} />
              ) : isCurrent ? (
                <Loader2 size={14} className="animate-spin" style={{ color: '#3b82f6' }} />
              ) : (
                <div style={{ width: 14, height: 14, borderRadius: '50%', border: '1px solid rgba(255,255,255,0.2)' }} />
              )}
              <span style={{ 
                color: isCurrentFailed ? '#f87171' : isCurrent ? '#ffffff' : isDone ? 'var(--text-muted)' : 'rgba(255,255,255,0.3)', 
                fontWeight: isCurrent ? 600 : 400 
              }}>
                {stg.label}
              </span>
            </div>
          );
        })}
      </div>

      {/* Status Message / Error Banner */}
      {isFailed ? (
        <div style={{ marginTop: 10, padding: 8, borderRadius: 6, background: 'rgba(239, 68, 68, 0.15)', border: '1px solid rgba(239, 68, 68, 0.3)', fontSize: '0.75rem', color: '#fca5a5' }}>
          <div><strong>Error:</strong> {status.error || status.message || 'Pipeline encountered an unexpected execution error.'}</div>
          {onRetry && (
            <button 
              onClick={onRetry}
              style={{
                marginTop: 8,
                background: 'rgba(239, 68, 68, 0.25)',
                border: '1px solid rgba(239, 68, 68, 0.5)',
                color: '#fff',
                padding: '4px 10px',
                borderRadius: 4,
                fontSize: '0.7rem',
                fontWeight: 600,
                cursor: 'pointer',
                display: 'flex',
                alignItems: 'center',
                gap: 4
              }}
            >
              <RefreshCw size={12} /> Retry Pipeline
            </button>
          )}
        </div>
      ) : (
        <div style={{ marginTop: 10, fontSize: '0.7rem', color: '#93c5fd', fontStyle: 'italic' }}>
          {status.message}
        </div>
      )}
    </div>
  );
}

function getStageRank(stage) {
  const map = {
    ingestion: 1,
    extraction: 2,
    merging: 3,
    enrichment: 4,
    knowledge_graph: 5,
    validation: 6,
    complete: 7,
    failed: -1
  };
  return map[stage] || 0;
}
