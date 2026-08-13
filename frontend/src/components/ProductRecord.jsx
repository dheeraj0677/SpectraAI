import React, { useState } from 'react';
import FieldCard from './FieldCard';
import ProvenancePopup from './ProvenancePopup';
import { ShieldCheck, Layers, Cpu, Award, Download, FileSpreadsheet } from 'lucide-react';

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

  const handleExportJSON = () => {
    const dataStr = "data:text/json;charset=utf-8," + encodeURIComponent(JSON.stringify(record, null, 2));
    const downloadAnchor = document.createElement('a');
    downloadAnchor.setAttribute("href", dataStr);
    downloadAnchor.setAttribute("download", `spectra_record_${record.product_id}.json`);
    document.body.appendChild(downloadAnchor);
    downloadAnchor.click();
    downloadAnchor.remove();
  };

  const handleExportCSV = () => {
    const rows = [
      ["Field Category", "Field Name", "Extracted Value", "Unit", "Confidence", "Status", "Source Citations"]
    ];

    const addRow = (cat, name, fVal) => {
      if (!fVal) return;
      const valStr = String(fVal.value ?? '');
      const unitStr = String(fVal.unit ?? '');
      const confStr = fVal.confidence !== undefined ? (fVal.confidence * 100).toFixed(0) + '%' : '';
      const statusStr = String(fVal.status ?? '');
      const provStr = (fVal.provenance || []).map(p => `${p.source_id}:${p.location}`).join(' | ');
      rows.push([cat, name, `"${valStr.replace(/"/g, '""')}"`, unitStr, confStr, statusStr, `"${provStr}"`]);
    };

    addRow('Identity', 'product_name', record.product_name);
    addRow('Identity', 'manufacturer', record.manufacturer);
    addRow('Identity', 'model_number', record.model_number);
    addRow('Identity', 'sku', record.sku);
    addRow('Identity', 'category', record.category);

    Object.entries(record.specifications || {}).forEach(([k, fv]) => {
      addRow('Specification', k, fv);
    });

    const csvContent = "data:text/csv;charset=utf-8," + rows.map(e => e.join(",")).join("\n");
    const downloadAnchor = document.createElement('a');
    downloadAnchor.setAttribute("href", encodeURI(csvContent));
    downloadAnchor.setAttribute("download", `spectra_record_${record.product_id}.csv`);
    document.body.appendChild(downloadAnchor);
    downloadAnchor.click();
    downloadAnchor.remove();
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
            <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
              <span style={{ fontSize: '0.75rem', padding: '2px 8px', borderRadius: 4, background: 'rgba(59, 130, 246, 0.2)', color: '#93c5fd', fontWeight: 600 }}>
                ID: {record.product_id}
              </span>
              <span style={{ fontSize: '0.7rem', padding: '2px 6px', borderRadius: 4, background: record.review_status === 'approved' ? 'rgba(16, 185, 129, 0.2)' : 'rgba(245, 158, 11, 0.2)', color: record.review_status === 'approved' ? '#34d399' : '#fbbf24' }}>
                {record.review_status.toUpperCase()}
              </span>
            </div>

            <h2 style={{ fontSize: '1.3rem', fontWeight: 700, marginTop: 6, color: '#ffffff' }}>
              {record.product_name?.value || 'Unnamed Product'}
            </h2>
            <div style={{ fontSize: '0.85rem', color: 'var(--text-muted)', marginTop: 2 }}>
              {record.manufacturer?.value || 'Unknown Manufacturer'} | {record.category?.value || 'Uncategorized'}
            </div>

            {/* Export Buttons */}
            <div style={{ display: 'flex', gap: 8, marginTop: 12 }}>
              <button
                onClick={handleExportJSON}
                style={{
                  background: 'rgba(59, 130, 246, 0.15)',
                  border: '1px solid rgba(59, 130, 246, 0.4)',
                  color: '#60a5fa',
                  padding: '4px 10px',
                  borderRadius: 6,
                  fontSize: '0.75rem',
                  fontWeight: 600,
                  cursor: 'pointer',
                  display: 'flex',
                  alignItems: 'center',
                  gap: 4
                }}
              >
                <Download size={14} /> Export JSON
              </button>
              <button
                onClick={handleExportCSV}
                style={{
                  background: 'rgba(16, 185, 129, 0.15)',
                  border: '1px solid rgba(16, 185, 129, 0.4)',
                  color: '#34d399',
                  padding: '4px 10px',
                  borderRadius: 6,
                  fontSize: '0.75rem',
                  fontWeight: 600,
                  cursor: 'pointer',
                  display: 'flex',
                  alignItems: 'center',
                  gap: 4
                }}
              >
                <FileSpreadsheet size={14} /> Export CSV
              </button>
            </div>
          </div>

          <div style={{ textAlign: 'right' }}>
            <div style={{ fontSize: '0.7rem', color: 'var(--text-muted)', textTransform: 'uppercase' }}>Overall Score</div>
            <div style={{ fontSize: '1.4rem', fontWeight: 700, color: record.overall_confidence >= 0.75 ? '#34d399' : '#fbbf24' }}>
              {(record.overall_confidence * 100).toFixed(0)}%
            </div>
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
