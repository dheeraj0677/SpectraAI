import React from 'react';
import { AlertTriangle, CheckCircle2, TrendingUp, Info } from 'lucide-react';

export default function ConsistencyPanel({ warnings }) {
  return (
    <div style={{ background: 'rgba(0,0,0,0.3)', borderRadius: 10, padding: 12, border: '1px solid var(--panel-border)', marginTop: 12 }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 8 }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: 6, fontSize: '0.8rem', fontWeight: 600, color: '#fbbf24' }}>
          <AlertTriangle size={14} /> Knowledge Graph Consistency Checks
        </div>
        {warnings && warnings.length > 0 && (
          <span style={{ fontSize: '0.65rem', padding: '1px 6px', borderRadius: 4, background: 'rgba(245, 158, 11, 0.2)', color: '#fbbf24', fontWeight: 600 }}>
            {warnings.length} Outlier Flag{warnings.length > 1 ? 's' : ''}
          </span>
        )}
      </div>

      {!warnings || warnings.length === 0 ? (
        <div style={{ display: 'flex', alignItems: 'center', gap: 8, fontSize: '0.75rem', color: '#34d399', background: 'rgba(16, 185, 129, 0.08)', padding: 10, borderRadius: 6, border: '1px solid rgba(16, 185, 129, 0.2)' }}>
          <CheckCircle2 size={16} />
          <div>
            <div>All specs align within category bounds.</div>
            <div style={{ fontSize: '0.68rem', color: 'var(--text-muted)', marginTop: 2 }}>
              Compared against category sibling nodes (±2.5x variance threshold).
            </div>
          </div>
        </div>
      ) : (
        <div style={{ display: 'flex', flexDirection: 'column', gap: 8 }}>
          {warnings.map((w, idx) => (
            <div key={idx} style={{ background: 'rgba(245,158,11,0.1)', border: '1px solid rgba(245,158,11,0.3)', padding: 10, borderRadius: 6, fontSize: '0.75rem' }}>
              <div style={{ fontWeight: 600, color: '#fbbf24', display: 'flex', alignItems: 'center', gap: 4, marginBottom: 4 }}>
                <TrendingUp size={13} /> Sibling Anomaly: {w.field}
              </div>
              <div style={{ color: '#e2e8f0', lineHeight: 1.4 }}>
                {w.message}
              </div>
              <div style={{ fontSize: '0.65rem', color: 'var(--text-muted)', marginTop: 6, display: 'flex', alignItems: 'center', gap: 4 }}>
                <Info size={11} /> Flagged because value deviates &gt;2.5x or &lt;0.3x from category average.
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
