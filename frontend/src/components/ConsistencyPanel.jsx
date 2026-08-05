import React from 'react';
import { AlertTriangle, CheckCircle } from 'lucide-react';

export default function ConsistencyPanel({ warnings }) {
  return (
    <div style={{ background: 'rgba(0,0,0,0.3)', borderRadius: 10, padding: 12, border: '1px solid var(--panel-border)', marginTop: 12 }}>
      <div style={{ display: 'flex', alignItems: 'center', gap: 6, fontSize: '0.8rem', fontWeight: 600, color: '#fbbf24', marginBottom: 8 }}>
        <AlertTriangle size={14} /> Catalog Consistency Checks
      </div>

      {!warnings || warnings.length === 0 ? (
        <div style={{ display: 'flex', alignItems: 'center', gap: 6, fontSize: '0.75rem', color: '#34d399' }}>
          <CheckCircle size={14} /> All extracted specs align within normal bounds for sibling products in this category.
        </div>
      ) : (
        <div style={{ display: 'flex', flexDirection: 'column', gap: 8 }}>
          {warnings.map((w, idx) => (
            <div key={idx} style={{ background: 'rgba(245,158,11,0.1)', border: '1px solid rgba(245,158,11,0.3)', padding: 8, borderRadius: 6, fontSize: '0.75rem' }}>
              <div style={{ fontWeight: 600, color: '#fbbf24', marginBottom: 2 }}>
                ⚠️ Outlier Flag: {w.field}
              </div>
              <div style={{ color: 'var(--text-muted)' }}>
                {w.message}
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
