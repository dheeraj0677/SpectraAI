import React, { useEffect, useState } from 'react';
import { Loader2, CheckCircle2, AlertCircle } from 'lucide-react';

const STAGES = [
  { id: 'ingestion', label: '1. Ingestion & Hashes' },
  { id: 'extraction', label: '2. Claude Multimodal Extract' },
  { id: 'merging', label: '3. Merge & Conflict Scoring' },
  { id: 'enrichment', label: '4. Chroma RAG Enrichment' },
  { id: 'knowledge_graph', label: '5. NetworkX Graph Expansion' },
  { id: 'validation', label: '6. Rule Validation & Scoring' },
];

export default function PipelineStatus({ jobId, onComplete }) {
  const [status, setStatus] = useState({ stage: 'starting', percent: 0, message: 'Connecting to pipeline SSE stream...' });

  useEffect(() => {
    if (!jobId) return;

    const eventSource = new EventSource(`http://localhost:8000/api/pipeline/status/${jobId}`);

    eventSource.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data);
        if (data.ping) return;

        setStatus(data);

        if (data.stage === 'complete') {
          eventSource.close();
          if (onComplete) onComplete();
        }
      } catch (e) {
        console.error('Error parsing SSE event', e);
      }
    };

    eventSource.onerror = (err) => {
      console.error('SSE connection error:', err);
      eventSource.close();
    };

    return () => {
      eventSource.close();
    };
  }, [jobId, onComplete]);

  return (
    <div style={{ background: 'rgba(0,0,0,0.2)', padding: 12, borderRadius: 8, marginTop: 12 }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 8 }}>
        <span style={{ fontSize: '0.8rem', fontWeight: 600, color: 'var(--accent-cyan)' }}>Live Pipeline Engine</span>
        <span style={{ fontSize: '0.75rem', fontWeight: 600 }}>{status.percent}%</span>
      </div>

      <div style={{ height: 6, width: '100%', background: 'rgba(255,255,255,0.08)', borderRadius: 3, overflow: 'hidden', marginBottom: 12 }}>
        <div 
          style={{ 
            height: '100%', 
            width: `${status.percent}%`, 
            background: 'linear-gradient(90deg, #3b82f6, #06b6d4)', 
            transition: 'width 0.3s ease' 
          }} 
        />
      </div>

      <div style={{ display: 'flex', flexDirection: 'column', gap: 6 }}>
        {STAGES.map((stg) => {
          const isDone = status.percent === 100 || getStageRank(status.stage) > getStageRank(stg.id);
          const isCurrent = status.stage === stg.id;

          return (
            <div key={stg.id} style={{ display: 'flex', alignItems: 'center', gap: 8, fontSize: '0.75rem' }}>
              {isDone ? (
                <CheckCircle2 size={14} style={{ color: '#10b981' }} />
              ) : isCurrent ? (
                <Loader2 size={14} className="animate-spin" style={{ color: '#3b82f6' }} />
              ) : (
                <div style={{ width: 14, height: 14, borderRadius: '50%', border: '1px solid rgba(255,255,255,0.2)' }} />
              )}
              <span style={{ color: isCurrent ? '#ffffff' : isDone ? 'var(--text-muted)' : 'rgba(255,255,255,0.3)', fontWeight: isCurrent ? 600 : 400 }}>
                {stg.label}
              </span>
            </div>
          );
        })}
      </div>

      <div style={{ marginTop: 10, fontSize: '0.7rem', color: '#93c5fd', fontStyle: 'italic' }}>
        {status.message}
      </div>
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
    complete: 7
  };
  return map[stage] || 0;
}
