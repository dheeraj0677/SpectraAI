import React, { useState } from 'react';
import { CheckCircle2, Edit3, History, ShieldCheck } from 'lucide-react';
import { approveRecord, editField, fetchEditHistory } from '../api';

export default function HumanReview({ record, onRecordUpdated }) {
  const [isEditing, setIsEditing] = useState(false);
  const [editFieldName, setEditFieldName] = useState('');
  const [editValue, setEditValue] = useState('');
  const [editUnit, setEditUnit] = useState('');
  const [history, setHistory] = useState([]);
  const [showHistoryModal, setShowHistoryModal] = useState(false);

  if (!record) return null;

  const handleApprove = async () => {
    try {
      const res = await approveRecord(record.product_id);
      if (res.record) {
        onRecordUpdated(res.record);
      }
    } catch (e) {
      alert('Approval failed: ' + e.message);
    }
  };

  const handleSaveEdit = async () => {
    if (!editFieldName || !editValue) return;
    try {
      const res = await editField(record.product_id, editFieldName, editValue, editUnit || null);
      if (res.record) {
        onRecordUpdated(res.record);
      }
      setIsEditing(false);
      setEditFieldName('');
      setEditValue('');
      setEditUnit('');
    } catch (e) {
      alert('Failed to save edit: ' + e.message);
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
          <ShieldCheck size={20} style={{ color: record.review_status === 'approved' ? '#34d399' : '#fbbf24' }} />
          <div>
            <div style={{ fontSize: '0.85rem', fontWeight: 600 }}>Human-in-the-Loop Review Status</div>
            <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>
              Status: <strong style={{ color: '#fff', textTransform: 'uppercase' }}>{record.review_status}</strong> | Edits Logged: {record.human_edits_log?.length || 0}
            </div>
          </div>
        </div>
      </div>

      <div style={{ display: 'flex', alignItems: 'center', gap: 12 }}>
        <button 
          onClick={handleViewHistory}
          style={{ 
            background: 'rgba(255,255,255,0.06)', 
            border: '1px solid var(--panel-border)', 
            color: 'var(--text-main)', 
            borderRadius: 8, 
            padding: '8px 14px', 
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
            padding: '8px 14px', 
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
          disabled={record.review_status === 'approved'}
          style={{ 
            background: record.review_status === 'approved' ? 'rgba(16, 185, 129, 0.2)' : 'linear-gradient(135deg, #10b981, #059669)', 
            border: 'none', 
            color: 'white', 
            borderRadius: 8, 
            padding: '8px 18px', 
            fontSize: '0.85rem', 
            fontWeight: 600, 
            cursor: record.review_status === 'approved' ? 'default' : 'pointer',
            display: 'flex',
            alignItems: 'center',
            gap: 6
          }}
        >
          <CheckCircle2 size={16} /> {record.review_status === 'approved' ? 'Record Approved' : 'Approve Record'}
        </button>
      </div>

      {/* Human Edit Modal */}
      {isEditing && (
        <div className="modal-overlay" onClick={() => setIsEditing(false)}>
          <div className="modal-content" onClick={(e) => e.stopPropagation()}>
            <h3 style={{ fontSize: '1.1rem', fontWeight: 700, marginBottom: 14 }}>Human Correction / Field Override</h3>
            
            <div style={{ display: 'flex', flexDirection: 'column', gap: 12 }}>
              <div>
                <label style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>Target Field</label>
                <select 
                  value={editFieldName} 
                  onChange={(e) => {
                    setEditFieldName(e.target.value);
                    const fieldVal = record.specifications[e.target.value] || record[e.target.value];
                    if (fieldVal) {
                      setEditValue(fieldVal.value || '');
                      setEditUnit(fieldVal.unit || '');
                    }
                  }}
                  style={{ width: '100%', padding: 8, borderRadius: 6, background: '#1e293b', color: '#fff', border: '1px solid var(--panel-border)', marginTop: 4 }}
                >
                  <option value="">-- Select Field --</option>
                  {allAvailableFields.map(f => (
                    <option key={f} value={f}>{f}</option>
                  ))}
                </select>
              </div>

              <div>
                <label style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>New Value</label>
                <input 
                  type="text" 
                  value={editValue} 
                  onChange={(e) => setEditValue(e.target.value)} 
                  placeholder="Enter corrected value"
                  style={{ width: '100%', padding: 8, borderRadius: 6, background: '#1e293b', color: '#fff', border: '1px solid var(--panel-border)', marginTop: 4 }}
                />
              </div>

              <div>
                <label style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>Unit (Optional)</label>
                <input 
                  type="text" 
                  value={editUnit} 
                  onChange={(e) => setEditUnit(e.target.value)} 
                  placeholder="e.g. V, kg, W"
                  style={{ width: '100%', padding: 8, borderRadius: 6, background: '#1e293b', color: '#fff', border: '1px solid var(--panel-border)', marginTop: 4 }}
                />
              </div>

              <div style={{ display: 'flex', justifyContent: 'flex-end', gap: 8, marginTop: 12 }}>
                <button onClick={() => setIsEditing(false)} style={{ padding: '8px 14px', borderRadius: 6, border: 'none', background: 'rgba(255,255,255,0.1)', color: '#fff', cursor: 'pointer' }}>Cancel</button>
                <button onClick={handleSaveEdit} className="btn-primary" style={{ width: 'auto', margin: 0 }}>Log & Save Correction</button>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* History Audit Log Modal */}
      {showHistoryModal && (
        <div className="modal-overlay" onClick={() => setShowHistoryModal(false)}>
          <div className="modal-content" onClick={(e) => e.stopPropagation()}>
            <h3 style={{ fontSize: '1.1rem', fontWeight: 700, marginBottom: 14 }}>Product Traceability Audit Trail</h3>
            
            {history.length === 0 ? (
              <div style={{ color: 'var(--text-muted)', fontSize: '0.85rem' }}>No human corrections logged yet for this product.</div>
            ) : (
              <div style={{ display: 'flex', flexDirection: 'column', gap: 10 }}>
                {history.map((h, idx) => (
                  <div key={idx} style={{ background: 'rgba(255,255,255,0.03)', border: '1px solid var(--panel-border)', borderRadius: 8, padding: 10 }}>
                    <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.75rem', color: '#60a5fa', marginBottom: 4 }}>
                      <span>Field: <strong>{h.field_name}</strong></span>
                      <span>{new Date(h.timestamp).toLocaleString()}</span>
                    </div>
                    <div style={{ fontSize: '0.8rem' }}>
                      Change: <span style={{ color: '#f87171', textDecoration: 'line-through' }}>{String(h.old_value)}</span> → <span style={{ color: '#34d399', fontWeight: 600 }}>{String(h.new_value)}</span>
                    </div>
                    <div style={{ fontSize: '0.7rem', color: 'var(--text-muted)', marginTop: 4 }}>
                      Reviewer: {h.reviewer} | Reason: {h.reason}
                    </div>
                  </div>
                ))}
              </div>
            )}

            <button onClick={() => setShowHistoryModal(false)} className="btn-primary" style={{ marginTop: 16 }}>Close Audit Log</button>
          </div>
        </div>
      )}
    </div>
  );
}
