import React from 'react';
import { AlertCircle, CheckCircle2, Eye, ShieldAlert, Sparkles, UserCheck, Cpu } from 'lucide-react';

export default function FieldCard({ fieldName, fieldValue, onClick }) {
  if (!fieldValue) {
    return (
      <div className="field-card" style={{ opacity: 0.5 }}>
        <div className="field-name">{fieldName.replace(/_/g, ' ')}</div>
        <div className="field-val" style={{ color: 'var(--text-muted)', fontSize: '0.85rem' }}>Missing / Not Specified</div>
      </div>
    );
  }

  const conf = fieldValue.confidence || 0.0;
  const status = fieldValue.status || 'extracted';
  const isSynthetic = fieldValue.is_synthetic || false;
  const obsType = fieldValue.observation_type || 'directly_observed';

  const confClass = status === 'human_verified' ? 'human_verified' :
                    status === 'conflicted' ? 'conflicted' :
                    conf >= 0.85 ? 'high' :
                    conf >= 0.6 ? 'med' : 'low';

  return (
    <div className="field-card" onClick={onClick}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 6, flexWrap: 'wrap', gap: 4 }}>
        <div className="field-name">{fieldName.replace(/_/g, ' ')}</div>
        <div style={{ display: 'flex', gap: 4, alignItems: 'center' }}>
          {isSynthetic && (
            <span style={{ fontSize: '0.65rem', padding: '1px 5px', borderRadius: 4, background: 'rgba(217, 119, 6, 0.2)', color: '#fbbf24', border: '1px solid rgba(217, 119, 6, 0.4)' }}>
              Demo Fixture
            </span>
          )}
          <span className={`badge-conf ${confClass}`}>
            {status === 'conflicted' && <ShieldAlert size={12} />}
            {status === 'human_verified' ? 'Human Verified' : `${(conf * 100).toFixed(0)}%`}
          </span>
        </div>
      </div>

      <div className="field-val">
        {String(fieldValue.value ?? 'N/A')} {fieldValue.unit || ''}
      </div>

      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginTop: 8, fontSize: '0.7rem', color: 'var(--text-muted)' }}>
        <span style={{ display: 'flex', alignItems: 'center', gap: 4 }}>
          {status === 'human_verified' && <UserCheck size={12} className="text-emerald-400" />}
          {status === 'enriched' && <Sparkles size={12} className="text-purple-400" />}
          {fieldValue.provenance?.length || 0} citation(s)
        </span>
        <span style={{ display: 'flex', alignItems: 'center', gap: 4, color: '#60a5fa' }}>
          <Eye size={12} /> Inspect receipt
        </span>
      </div>
    </div>
  );
}
