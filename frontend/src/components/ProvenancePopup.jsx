import React from 'react';
import { X, FileText, Sparkles, AlertTriangle, ShieldCheck, Tag, ArrowRight, CheckCircle2, SlidersHorizontal } from 'lucide-react';

export default function ProvenancePopup({ fieldName, fieldValue, onClose }) {
  if (!fieldValue) return null;

  const confClass = fieldValue.status === 'human_verified' ? 'human_verified' :
                    fieldValue.status === 'conflicted' ? 'conflicted' :
                    fieldValue.confidence >= 0.85 ? 'high' :
                    fieldValue.confidence >= 0.6 ? 'med' : 'low';

  const isSynthetic = fieldValue.is_synthetic || false;
  const obsType = fieldValue.observation_type || 'directly_observed';

  return (
    <div className="modal-overlay" onClick={onClose}>
      <div className="modal-content" onClick={(e) => e.stopPropagation()}>
        {/* Header */}
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 16, borderBottom: '1px solid var(--panel-border)', paddingBottom: 12 }}>
          <div>
            <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)', textTransform: 'uppercase', letterSpacing: '0.05em' }}>Field Provenance & Audit Trail</div>
            <div style={{ fontSize: '1.2rem', fontWeight: 700, color: '#ffffff' }}>{fieldName.replace(/_/g, ' ')}</div>
          </div>
          <button onClick={onClose} style={{ background: 'none', border: 'none', color: 'var(--text-muted)', cursor: 'pointer' }}>
            <X size={20} />
          </button>
        </div>

        {/* Value and Status Tags */}
        <div style={{ display: 'flex', gap: 10, alignItems: 'center', marginBottom: 16, flexWrap: 'wrap' }}>
          <div style={{ fontSize: '1.4rem', fontWeight: 700 }} className="font-mono">
            {String(fieldValue.value ?? 'N/A')} {fieldValue.unit || ''}
          </div>
          <span className={`badge-conf ${confClass}`}>
            Confidence: {(fieldValue.confidence * 100).toFixed(0)}%
          </span>
          <span style={{ fontSize: '0.75rem', padding: '3px 8px', borderRadius: 4, background: 'rgba(255,255,255,0.06)', textTransform: 'uppercase' }}>
            Status: {fieldValue.status}
          </span>
          {isSynthetic ? (
            <span style={{ fontSize: '0.75rem', padding: '3px 8px', borderRadius: 4, background: 'rgba(245, 158, 11, 0.15)', color: '#fbbf24', border: '1px solid rgba(245, 158, 11, 0.3)' }}>
              Synthetic Demo Data
            </span>
          ) : (
            <span style={{ fontSize: '0.75rem', padding: '3px 8px', borderRadius: 4, background: 'rgba(16, 185, 129, 0.15)', color: '#34d399', border: '1px solid rgba(16, 185, 129, 0.3)' }}>
              Real Source Extraction
            </span>
          )}
          <span style={{ fontSize: '0.75rem', padding: '3px 8px', borderRadius: 4, background: 'rgba(99, 102, 241, 0.15)', color: '#a5b4fc' }}>
            {obsType.replace(/_/g, ' ')}
          </span>
        </div>

        {/* Conflict Resolution Block */}
        {fieldValue.conflict_candidates && fieldValue.conflict_candidates.length > 0 && (
          <div style={{ background: 'rgba(244,63,94,0.1)', border: '1px solid rgba(244,63,94,0.3)', padding: 12, borderRadius: 8, marginBottom: 16 }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: 6, color: '#f87171', fontWeight: 600, fontSize: '0.85rem', marginBottom: 6 }}>
              <AlertTriangle size={16} /> Disagreeing Sources (Conflict Resolution Triggered)
            </div>
            <div style={{ fontSize: '0.8rem', color: 'var(--text-muted)', marginBottom: 8 }}>
              Multiple extraction sources yielded different values. Primary recommendation was scored with a 0.7x confidence penalty until resolved by human review.
            </div>
            {fieldValue.conflict_candidates.map((cand, idx) => (
              <div key={idx} style={{ background: 'rgba(0,0,0,0.3)', padding: 8, borderRadius: 6, marginTop: 6, fontSize: '0.8rem' }}>
                <span style={{ fontWeight: 600, color: '#fff' }}>Candidate {idx + 1}: {cand.value} {cand.unit || ''}</span>
                <span style={{ marginLeft: 8, color: '#fbbf24' }}>({(cand.confidence * 100).toFixed(0)}% conf)</span>
              </div>
            ))}
          </div>
        )}

        {/* Evidence Receipts */}
        <div style={{ fontWeight: 600, fontSize: '0.85rem', marginBottom: 8, display: 'flex', alignItems: 'center', gap: 6 }}>
          <FileText size={16} className="text-blue-400" /> Evidence Receipts ({fieldValue.provenance?.length || 0})
        </div>

        <div style={{ display: 'flex', flexDirection: 'column', gap: 10 }}>
          {fieldValue.provenance && fieldValue.provenance.map((prov, i) => (
            <div key={i} style={{ background: 'rgba(255,255,255,0.03)', border: '1px solid var(--panel-border)', borderRadius: 8, padding: 12 }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.75rem', marginBottom: 4, flexWrap: 'wrap', gap: 4 }}>
                <span style={{ fontWeight: 600, color: '#60a5fa' }}>Source ID: {prov.source_id}</span>
                <div style={{ display: 'flex', gap: 6 }}>
                  {prov.is_synthetic && (
                    <span style={{ color: '#fbbf24', background: 'rgba(245, 158, 11, 0.1)', padding: '1px 4px', borderRadius: 3 }}>Synthetic</span>
                  )}
                  <span style={{ color: 'var(--text-muted)' }}>Type: {prov.source_type}</span>
                </div>
              </div>

              <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)', marginBottom: 6 }}>
                Location: <strong style={{ color: '#fff' }}>{prov.location || 'N/A'}</strong> | Method: <code>{prov.extraction_method}</code>
              </div>

              {/* Normalization rule receipt if present */}
              {prov.normalization_rule && (
                <div style={{ background: 'rgba(59, 130, 246, 0.1)', border: '1px solid rgba(59, 130, 246, 0.2)', padding: '6px 8px', borderRadius: 6, marginBottom: 6, fontSize: '0.75rem', display: 'flex', alignItems: 'center', gap: 6, color: '#93c5fd' }}>
                  <SlidersHorizontal size={14} />
                  <span>
                    <strong>Normalization:</strong> {String(prov.raw_value)} {prov.raw_unit || ''} <ArrowRight size={12} style={{ display: 'inline', margin: '0 2px' }} /> {String(prov.normalized_value)} {prov.normalized_unit || ''} ({prov.normalization_rule})
                  </span>
                </div>
              )}

              {prov.raw_snippet && (
                <div style={{ background: 'rgba(0,0,0,0.4)', padding: 8, borderRadius: 6, fontSize: '0.8rem', fontStyle: 'italic', borderLeft: '3px solid #3b82f6' }}>
                  "{prov.raw_snippet}"
                </div>
              )}
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
