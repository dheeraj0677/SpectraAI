import React, { useState } from 'react';
import FieldCard from './FieldCard';
import ProvenancePopup from './ProvenancePopup';
import { ShieldCheck, Layers, Cpu, Award } from 'lucide-react';

export default function ProductRecord({ record, onEditField }) {
  const [selectedField, setSelectedField] = useState(null);

  if (!record) {
    return (
      <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', height: '100%', color: 'var(--text-muted)' }}>
        <Layers size={48} style={{ opacity: 0.3, marginBottom: 12 }} />
        <div>No product intelligence record loaded.</div>
        <div style={{ fontSize: '0.8rem', marginTop: 4 }}>Upload sources on the left or select a pre-processed record.</div>
      </div>
    );
  }

  const handleFieldClick = (name, val) => {
    setSelectedField({ name, value: val });
  };

  const coreFields = [
    { key: 'product_name', label: 'Product Name', val: record.product_name },
    { key: 'manufacturer', label: 'Manufacturer', val: record.manufacturer },
    { key: 'model_number', label: 'Model Number', val: record.model_number },
    { key: 'sku', label: 'SKU Code', val: record.sku },
    { key: 'category', label: 'Product Category', val: record.category },
  ];

  return (
    <div className="flex flex-col gap-4">
      {/* Product Hero Banner */}
      <div style={{ 
        background: 'linear-gradient(135deg, rgba(30, 58, 138, 0.4), rgba(15, 23, 42, 0.6))', 
        border: '1px solid rgba(59, 130, 246, 0.3)', 
        borderRadius: 12, 
        padding: 16 
      }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
          <div>
            <span style={{ fontSize: '0.75rem', padding: '2px 8px', borderRadius: 4, background: 'rgba(59, 130, 246, 0.2)', color: '#93c5fd', fontWeight: 600 }}>
              ID: {record.product_id}
            </span>
            <h2 style={{ fontSize: '1.3rem', fontWeight: 700, marginTop: 6, color: '#ffffff' }}>
              {record.product_name?.value || 'Unnamed Product'}
            </h2>
            <div style={{ fontSize: '0.85rem', color: 'var(--text-muted)', marginTop: 2 }}>
              {record.manufacturer?.value || 'Unknown Manufacturer'} | {record.category?.value || 'Uncategorized'}
            </div>
          </div>

          <div style={{ textAlign: 'right' }}>
            <div style={{ fontSize: '0.7rem', color: 'var(--text-muted)', textTransform: 'uppercase' }}>Overall Score</div>
            <div style={{ fontSize: '1.4rem', fontWeight: 700, color: record.overall_confidence >= 0.75 ? '#34d399' : '#fbbf24' }}>
              {(record.overall_confidence * 100).toFixed(0)}%
            </div>
            <span style={{ fontSize: '0.7rem', padding: '2px 6px', borderRadius: 4, background: record.review_status === 'approved' ? 'rgba(16, 185, 129, 0.2)' : 'rgba(245, 158, 11, 0.2)', color: record.review_status === 'approved' ? '#34d399' : '#fbbf24' }}>
              {record.review_status.toUpperCase()}
            </span>
          </div>
        </div>
      </div>

      {/* Identity Fields Grid */}
      <div>
        <div style={{ fontSize: '0.85rem', fontWeight: 600, color: '#93c5fd', marginBottom: 8, display: 'flex', alignItems: 'center', gap: 6 }}>
          <Layers size={16} /> Core Identity Attributes
        </div>
        <div className="fields-grid">
          {coreFields.map(f => (
            <FieldCard 
              key={f.key} 
              fieldName={f.label} 
              fieldValue={f.val} 
              onClick={() => handleFieldClick(f.label, f.val)} 
            />
          ))}
        </div>
      </div>

      {/* Technical Specs Grid */}
      <div>
        <div style={{ fontSize: '0.85rem', fontWeight: 600, color: '#93c5fd', marginBottom: 8, display: 'flex', alignItems: 'center', gap: 6 }}>
          <Cpu size={16} /> Technical & Electrical Specifications ({Object.keys(record.specifications || {}).length})
        </div>
        <div className="fields-grid">
          {Object.entries(record.specifications || {}).map(([key, fieldVal]) => (
            <FieldCard 
              key={key} 
              fieldName={key} 
              fieldValue={fieldVal} 
              onClick={() => handleFieldClick(key, fieldVal)} 
            />
          ))}
        </div>
      </div>

      {/* Provenance Inspection Modal */}
      {selectedField && (
        <ProvenancePopup 
          fieldName={selectedField.name} 
          fieldValue={selectedField.value} 
          onClose={() => setSelectedField(null)} 
        />
      )}
    </div>
  );
}
