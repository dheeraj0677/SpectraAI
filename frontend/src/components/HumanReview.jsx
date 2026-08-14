import React, { useState } from 'react';
import { CheckCircle2, Edit3, History, ShieldCheck, UserCheck, AlertCircle, Clock, FileText } from 'lucide-react';
import { approveRecord, editField, fetchEditHistory } from '../api';

const REASON_PRESETS = [
  'Confirmed correct spec from physical nameplate photo',
  'Datasheet erratum / vendor specification update',
  'Resolved multi-source extraction conflict',
  'Customer RFQ compliance alignment',
  'Manual catalog normalization'
];

export default function HumanReview({ record, onRecordUpdated }) {
  const [isEditing, setIsEditing] = useState(false);
  const [editFieldName, setEditFieldName] = useState('');
  const [editValue, setEditValue] = useState('');
  const [editUnit, setEditUnit] = useState('');
  const [reviewer, setReviewer] = useState('quality_engineer');
  const [reason, setReason] = useState(REASON_PRESETS[0]);
  const [customReason, setCustomReason] = useState('');
  const [history, setHistory] = useState([]);
  const [showHistoryModal, setShowHistoryModal] = useState(false);
  const [isLoading, setIsLoading] = useState(false);

  if (!record) return null;

  const handleApprove = async () => {
    try {
      setIsLoading(true);
      const res = await approveRecord(record.product_id, reviewer);
      if (res.record) {
        onRecordUpdated(res.record);
      }
    } catch (e) {
      alert('Approval failed: ' + e.message);
    } finally {
      setIsLoading(false);
    }
  };

  const handleSaveEdit = async () => {
    if (!editFieldName || !editValue) return;
    const finalReason = reason === 'Other' ? (customReason || 'Manual correction') : reason;
    try {
      setIsLoading(true);
      const res = await editField(
        record.product_id, 
        editFieldName, 
        editValue, 
        editUnit || null, 
        reviewer, 
        finalReason
      );
      if (res.record) {
        onRecordUpdated(res.record);
      }
      setIsEditing(false);
      setEditFieldName('');
      setEditValue('');
      setEditUnit('');
    } catch (e) {
      alert('Failed to save edit: ' + e.message);
    } finally {
      setIsLoading(false);
    }
  };

  const handleViewHistory = async () => {
    try {
      const data = await fetchEditHistory(record.product_id);
      setHistory(data.edit_history || []);
      setShowHistoryModal(true);
    } catch (e) {
      alert('Failed to load history: ' + e.message);
    }
  };

  const allAvailableFields = [
    'product_name',
    'manufacturer',
    'model_number',
    'sku',
    'category',
    ...Object.keys(record.specifications || {})
  ];

  return (
    <div className="bottom-bar">
      <div style={{ display: 'flex', alignItems: 'center', gap: 16 }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
          <ShieldCheck size={22} style={{ color: record.review_status === 'approved' ? '#34d399' : '#fbbf24' }} />
          <div>
            <div style={{ fontSize: '0.85rem', fontWeight: 600, display: 'flex', alignItems: 'center', gap: 6 }}>
              Human-in-the-Loop Review
              <span style={{ 
                fontSize: '0.65rem', 
                padding: '1px 6px', 
                borderRadius: 4, 
                background: record.review_status === 'approved' ? 'rgba(16, 185, 129, 0.2)' : 'rgba(245, 158, 11, 0.2)',
                color: record.review_status === 'approved' ? '#34d399' : '#fbbf24',
                fontWeight: 600
              }}>
                {record.review_status.toUpperCase()}
              </span>
            </div>
            <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)', marginTop: 2 }}>
              Edits Appended: <strong>{record.human_edits_log?.length || 0}</strong> | Active Reviewer: <strong style={{ color: '#93c5fd' }}>{reviewer}</strong>
            </div>
          </div>
        </div>
      </div>

      <div style={{ display: 'flex', alignItems: 'center', gap: 10 }}>
        {/* Reviewer Badge / Selector */}
        <div style={{ display: 'flex', alignItems: 'center', gap: 6, fontSize: '0.75rem', color: 'var(--text-muted)' }}>
          <UserCheck size={14} />
          <select
            value={reviewer}
            onChange={(e) => setReviewer(e.target.value)}
            style={{
              background: '#1e293b',
              color: '#fff',
              border: '1px solid var(--panel-border)',
              borderRadius: 6,
              padding: '4px 8px',
              fontSize: '0.75rem'
            }}
          >
            <option value="quality_engineer">quality_engineer</option>
            <option value="lead_cataloger">lead_cataloger</option>
            <option value="compliance_auditor">compliance_auditor</option>
            <option value="domain_specialist">domain_specialist</option>
          </select>
        </div>

        <button 
          onClick={handleViewHistory}
          style={{ 
            background: 'rgba(255,255,255,0.06)', 
            border: '1px solid var(--panel-border)', 
            color: 'var(--text-main)', 
            borderRadius: 8, 
            padding: '7px 12px', 
            fontSize: '0.8rem', 
            cursor: 'pointer',
            display: 'flex',
            alignItems: 'center',
            gap: 6
          }}
        >
          <History size={14} /> Audit Trail ({record.human_edits_log?.length || 0})
        </button>

        <button 
          onClick={() => setIsEditing(true)}
          style={{ 
            background: 'rgba(59, 130, 246, 0.15)', 
            border: '1px solid rgba(59, 130, 246, 0.4)', 
            color: '#60a5fa', 
            borderRadius: 8, 
            padding: '7px 14px', 
            fontSize: '0.8rem', 
            fontWeight: 600, 
            cursor: 'pointer',
            display: 'flex',
            alignItems: 'center',
            gap: 6
          }}
        >
          <Edit3 size={14} /> Correct / Override Field
        </button>

        <button 
          onClick={handleApprove}
          disabled={record.review_status === 'approved' || isLoading}
          style={{ 
            background: record.review_status === 'approved' ? 'rgba(16, 185, 129, 0.2)' : 'linear-gradient(135deg, #10b981, #059669)', 
            border: 'none', 
            color: 'white', 
            borderRadius: 8, 
            padding: '7px 16px', 
            fontSize: '0.85rem', 
            fontWeight: 600, 
            cursor: record.review_status === 'approved' ? 'default' : 'pointer',
            display: 'flex',
            alignItems: 'center',
            gap: 6,
            opacity: isLoading ? 0.7 : 1
          }}
        >
          <CheckCircle2 size={16} /> {record.review_status === 'approved' ? 'Record Approved' : 'Approve Record'}
        </button>
      </div>

      {/* Human Edit Modal */}
      {isEditing && (
        <div className="modal-overlay" onClick={() => setIsEditing(false)}>
          <div className="modal-content" onClick={(e) => e.stopPropagation()}>
            <h3 style={{ fontSize: '1.1rem', fontWeight: 700, marginBottom: 12 }}>Human Correction / Immutable Field Override</h3>
            
            <div style={{ display: 'flex', flexDirection: 'column', gap: 12 }}>
              <div>
                <label style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>Target Field</label>
                <select 
                  value={editFieldName} 
                  onChange={(e) => {
                    setEditFieldName(e.target.value);
                    const fieldVal = record.specifications?.[e.target.value] || record[e.target.value];
                    if (fieldVal) {
                      setEditValue(fieldVal.value || '');
                      setEditUnit(fieldVal.unit || '');
                    }
                  }}
                  style={{ width: '100%', padding: 8, borderRadius: 6, background: '#1e293b', color: '#fff', border: '1px solid var(--panel-border)', marginTop: 4 }}
                >
                  <option value="">-- Select Field to Correct --</option>
                  {allAvailableFields.map(f => (
                    <option key={f} value={f}>{f}</option>
                  ))}
                </select>
              </div>

              <div style={{ display: 'grid', gridTemplateColumns: '2fr 1fr', gap: 8 }}>
                <div>
                  <label style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>Corrected Value</label>
                  <input 
                    type="text" 
                    value={editValue} 
                    onChange={(e) => setEditValue(e.target.value)} 
                    placeholder="e.g. 480V"
                    style={{ width: '100%', padding: 8, borderRadius: 6, background: '#1e293b', color: '#fff', border: '1px solid var(--panel-border)', marginTop: 4 }}
                  />
                </div>
                <div>
                  <label style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>Unit (Optional)</label>
                  <input 
                    type="text" 
                    value={editUnit} 
                    onChange={(e) => setEditUnit(e.target.value)} 
                    placeholder="e.g. V, W, kg"
                    style={{ width: '100%', padding: 8, borderRadius: 6, background: '#1e293b', color: '#fff', border: '1px solid var(--panel-border)', marginTop: 4 }}
                  />
                </div>
              </div>

              <div>
                <label style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>Correction Reason / Justification</label>
                <select
                  value={reason}
                  onChange={(e) => setReason(e.target.value)}
                  style={{ width: '100%', padding: 8, borderRadius: 6, background: '#1e293b', color: '#fff', border: '1px solid var(--panel-border)', marginTop: 4 }}
                >
                  {REASON_PRESETS.map(r => (
                    <option key={r} value={r}>{r}</option>
                  ))}
                  <option value="Other">Other (custom explanation)...</option>
                </select>
                {reason === 'Other' && (
                  <input
                    type="text"
                    value={customReason}
                    onChange={(e) => setCustomReason(e.target.value)}
                    placeholder="Enter detailed reason"
                    style={{ width: '100%', padding: 8, borderRadius: 6, background: '#1e293b', color: '#fff', border: '1px solid var(--panel-border)', marginTop: 6 }}
                  />
                )}
              </div>

              <div style={{ fontSize: '0.7rem', color: 'var(--text-muted)', background: 'rgba(255,255,255,0.02)', padding: 8, borderRadius: 6 }}>
                💡 Note: This edit appends an immutable record with observation type <code>human_verified</code> without erasing original source citations.
              </div>

              <div style={{ display: 'flex', justifyContent: 'flex-end', gap: 8, marginTop: 8 }}>
                <button onClick={() => setIsEditing(false)} style={{ padding: '8px 14px', borderRadius: 6, border: 'none', background: 'rgba(255,255,255,0.1)', color: '#fff', cursor: 'pointer' }}>Cancel</button>
                <button onClick={handleSaveEdit} className="btn-primary" style={{ width: 'auto', margin: 0 }}>Append Correction Receipt</button>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* History Audit Log Modal */}
      {showHistoryModal && (
        <div className="modal-overlay" onClick={() => setShowHistoryModal(false)}>
          <div className="modal-content" onClick={(e) => e.stopPropagation()} style={{ maxWidth: 600 }}>
            <h3 style={{ fontSize: '1.1rem', fontWeight: 700, marginBottom: 12, display: 'flex', alignItems: 'center', gap: 8 }}>
              <History size={18} className="text-blue-400" /> Immutable Product Audit Trail
            </h3>
            
            {history.length === 0 ? (
              <div style={{ color: 'var(--text-muted)', fontSize: '0.85rem', padding: '20px 0', textAlign: 'center' }}>
                No human corrections logged yet for this product record.
              </div>
            ) : (
              <div style={{ display: 'flex', flexDirection: 'column', gap: 10, maxHeight: 350, overflowY: 'auto' }}>
                {history.map((h, idx) => (
                  <div key={idx} style={{ background: 'rgba(255,255,255,0.03)', border: '1px solid var(--panel-border)', borderRadius: 8, padding: 12 }}>
                    <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.75rem', color: '#60a5fa', marginBottom: 4 }}>
                      <span style={{ fontWeight: 600 }}>Field: {h.field_name}</span>
                      <span style={{ display: 'flex', alignItems: 'center', gap: 4, color: 'var(--text-muted)' }}>
                        <Clock size={12} /> {new Date(h.timestamp).toLocaleString()}
                      </span>
                    </div>
                    <div style={{ fontSize: '0.85rem', marginTop: 4 }}>
                      Change: <span style={{ color: '#f87171', textDecoration: 'line-through' }}>{String(h.old_value)}</span> → <span style={{ color: '#34d399', fontWeight: 700 }}>{String(h.new_value)}</span>
                    </div>
                    <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)', marginTop: 6, display: 'flex', justifyContent: 'space-between' }}>
                      <span>Reviewer: <strong style={{ color: '#e2e8f0' }}>{h.reviewer}</strong></span>
                      <span>Reason: <em style={{ color: '#93c5fd' }}>{h.reason}</em></span>
                    </div>
                  </div>
                ))}
              </div>
            )}

            <button onClick={() => setShowHistoryModal(false)} className="btn-primary" style={{ marginTop: 16 }}>Close Audit Trail</button>
          </div>
        </div>
      )}
    </div>
  );
}
