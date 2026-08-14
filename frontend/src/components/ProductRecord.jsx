import React, { useState } from 'react';
import FieldCard from './FieldCard';
import ProvenancePopup from './ProvenancePopup';
import { 
  ShieldCheck, 
  Layers, 
  Cpu, 
  Award, 
  Download, 
  FileSpreadsheet, 
  AlertTriangle, 
  Tag, 
  Sparkles, 
  ArrowRightLeft, 
  Info,
  CheckCircle2,
  SlidersHorizontal
} from 'lucide-react';

export default function ProductRecord({ record, onEditField }) {
  const [selectedField, setSelectedField] = useState(null);

  if (!record) {
    return (
      <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', height: '100%', minHeight: 300, color: 'var(--text-muted)' }}>
        <Layers size={48} style={{ opacity: 0.3, marginBottom: 12 }} />
        <div style={{ fontWeight: 600, fontSize: '1rem' }}>No product intelligence record loaded</div>
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
      ["Field Category", "Field Name", "Extracted Value", "Unit", "Confidence", "Status", "Observation Type", "Synthetic Demo?", "Normalization Rule", "Source Citations"]
    ];

    const addRow = (cat, name, fVal) => {
      if (!fVal) return;
      const valStr = String(fVal.value ?? '');
      const unitStr = String(fVal.unit ?? '');
      const confStr = fVal.confidence !== undefined ? (fVal.confidence * 100).toFixed(0) + '%' : '';
      const statusStr = String(fVal.status ?? '');
      const obsType = String(fVal.observation_type ?? 'directly_observed');
      const isSyn = fVal.is_synthetic ? 'YES' : 'NO';
      const normRule = (fVal.provenance || []).map(p => p.normalization_rule).filter(Boolean).join('; ') || 'None';
      const provStr = (fVal.provenance || []).map(p => `${p.source_id}:${p.location || 'N/A'}`).join(' | ');
      rows.push([cat, name, `"${valStr.replace(/"/g, '""')}"`, unitStr, confStr, statusStr, obsType, isSyn, `"${normRule.replace(/"/g, '""')}"`, `"${provStr}"`]);
    };

    addRow('Identity', 'product_name', record.product_name);
    addRow('Identity', 'manufacturer', record.manufacturer);
    addRow('Identity', 'model_number', record.model_number);
    addRow('Identity', 'sku', record.sku);
    addRow('Identity', 'category', record.category);
    addRow('Taxonomy', 'unspsc_code', record.unspsc_code);
    addRow('Taxonomy', 'etim_class', record.etim_class);
    addRow('SEO', 'seo_title', record.seo_title);
    addRow('Commercial', 'warranty', record.warranty);

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

  // Find all conflicted fields
  const conflictedFields = Object.entries(record.specifications || {})
    .filter(([_, fv]) => fv.status === 'conflicted');

  const criBreakdown = record.cri_breakdown || {};
  const criScore = record.commerce_readiness_score || 0.0;

  return (
    <div className="flex flex-col gap-4">
      {/* Product Hero Banner */}
      <div style={{ 
        background: 'linear-gradient(135deg, rgba(30, 58, 138, 0.4), rgba(15, 23, 42, 0.6))', 
        border: '1px solid rgba(59, 130, 246, 0.3)', 
        borderRadius: 12, 
        padding: 16 
      }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', flexWrap: 'wrap', gap: 12 }}>
          <div>
            <div style={{ display: 'flex', alignItems: 'center', gap: 8, flexWrap: 'wrap' }}>
              <span style={{ fontSize: '0.75rem', padding: '2px 8px', borderRadius: 4, background: 'rgba(59, 130, 246, 0.2)', color: '#93c5fd', fontWeight: 600 }}>
                ID: {record.product_id}
              </span>
              <span style={{ 
                fontSize: '0.7rem', 
                padding: '2px 6px', 
                borderRadius: 4, 
                background: record.review_status === 'approved' ? 'rgba(16, 185, 129, 0.2)' : 'rgba(245, 158, 11, 0.2)', 
                color: record.review_status === 'approved' ? '#34d399' : '#fbbf24',
                fontWeight: 600
              }}>
                {record.review_status.toUpperCase()}
              </span>
            </div>

            <h2 style={{ fontSize: '1.3rem', fontWeight: 700, marginTop: 6, color: '#ffffff' }}>
              {record.product_name?.value || 'Unnamed Product'}
            </h2>
            <div style={{ fontSize: '0.85rem', color: 'var(--text-muted)', marginTop: 2 }}>
              {record.manufacturer?.value || 'Unknown Manufacturer'} | {record.category?.value || 'Uncategorized'}
            </div>

            {/* Export Actions */}
            <div style={{ display: 'flex', gap: 8, marginTop: 12 }}>
              <button
                onClick={handleExportJSON}
                style={{
                  background: 'rgba(59, 130, 246, 0.15)',
                  border: '1px solid rgba(59, 130, 246, 0.4)',
                  color: '#60a5fa',
                  padding: '5px 12px',
                  borderRadius: 6,
                  fontSize: '0.75rem',
                  fontWeight: 600,
                  cursor: 'pointer',
                  display: 'flex',
                  alignItems: 'center',
                  gap: 6
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
                  padding: '5px 12px',
                  borderRadius: 6,
                  fontSize: '0.75rem',
                  fontWeight: 600,
                  cursor: 'pointer',
                  display: 'flex',
                  alignItems: 'center',
                  gap: 6
                }}
              >
                <FileSpreadsheet size={14} /> Export CSV (Full Provenance)
              </button>
            </div>
          </div>

          <div style={{ textAlign: 'right', minWidth: 120 }}>
            <div style={{ fontSize: '0.7rem', color: 'var(--text-muted)', textTransform: 'uppercase' }}>Overall Confidence</div>
            <div style={{ fontSize: '1.5rem', fontWeight: 700, color: record.overall_confidence >= 0.75 ? '#34d399' : '#fbbf24' }}>
              {(record.overall_confidence * 100).toFixed(0)}%
            </div>
          </div>
        </div>
      </div>

      {/* Conflicted Fields Alert Banner */}
      {conflictedFields.length > 0 && (
        <div style={{
          background: 'rgba(244, 63, 94, 0.1)',
          border: '1px solid rgba(244, 63, 94, 0.3)',
          borderRadius: 8,
          padding: 12,
          display: 'flex',
          flexDirection: 'column',
          gap: 6
        }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: 6, color: '#f87171', fontWeight: 700, fontSize: '0.85rem' }}>
            <AlertTriangle size={16} /> Multi-Source Conflict Detected ({conflictedFields.length} field(s))
          </div>
          <div style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>
            Extraction sources produced conflicting values. A 0.7x confidence penalty is applied until resolved via the review bar below.
          </div>
          <div style={{ display: 'flex', gap: 8, flexWrap: 'wrap', marginTop: 4 }}>
            {conflictedFields.map(([name, fv]) => (
              <span 
                key={name} 
                onClick={() => handleFieldClick(name, fv)}
                style={{ 
                  background: 'rgba(0,0,0,0.3)', 
                  border: '1px solid rgba(244,63,94,0.4)', 
                  padding: '4px 8px', 
                  borderRadius: 4, 
                  fontSize: '0.75rem', 
                  cursor: 'pointer',
                  color: '#fbbf24'
                }}
              >
                ⚠️ <strong>{name}:</strong> {String(fv.value)} ({fv.conflict_candidates?.length || 2} candidates) — Click to view
              </span>
            ))}
          </div>
        </div>
      )}

      {/* Commerce Readiness Index (CRI) 5-Dimension Scorecard */}
      <div style={{
        background: 'rgba(0,0,0,0.25)',
        border: '1px solid var(--panel-border)',
        borderRadius: 10,
        padding: 14
      }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 10 }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: 6, fontSize: '0.85rem', fontWeight: 600, color: '#a78bfa' }}>
            <Award size={16} /> Commerce Readiness Index (CRI) Scorecard
          </div>
          <div style={{ fontSize: '1.1rem', fontWeight: 700, color: criScore >= 80 ? '#34d399' : '#fbbf24' }}>
            {criScore.toFixed(1)} / 100
          </div>
        </div>

        {/* 5-Dimension Progress Bars */}
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(130px, 1fr))', gap: 10 }}>
          {[
            { label: 'Identity', score: criBreakdown.identity_completeness || 0, max: 25 },
            { label: 'Specs Depth', score: criBreakdown.specifications_depth || 0, max: 25 },
            { label: 'Taxonomy', score: criBreakdown.taxonomy_compliance || 0, max: 20 },
            { label: 'Commerce Content', score: criBreakdown.commerce_content || 0, max: 15 },
            { label: 'Quality & Accuracy', score: criBreakdown.quality_and_accuracy || 0, max: 15 }
          ].map(dim => (
            <div key={dim.label} style={{ background: 'rgba(255,255,255,0.03)', padding: 8, borderRadius: 6, border: '1px solid rgba(255,255,255,0.05)' }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.7rem', color: 'var(--text-muted)', marginBottom: 4 }}>
                <span>{dim.label}</span>
                <span style={{ fontWeight: 600, color: '#fff' }}>{dim.score}/{dim.max}</span>
              </div>
              <div style={{ height: 4, width: '100%', background: 'rgba(255,255,255,0.1)', borderRadius: 2, overflow: 'hidden' }}>
                <div style={{ height: '100%', width: `${Math.min(100, (dim.score / dim.max) * 100)}%`, background: '#8b5cf6' }} />
              </div>
            </div>
          ))}
        </div>

        <div style={{ fontSize: '0.7rem', color: 'var(--text-muted)', marginTop: 8, display: 'flex', alignItems: 'center', gap: 4 }}>
          <Info size={12} /> Note: CRI reflects catalog completeness & rule conformance, not an engineering performance guarantee.
        </div>
      </div>

      {/* Industrial Taxonomy & E-Commerce Standards */}
      <div style={{
        background: 'rgba(0,0,0,0.2)',
        border: '1px solid var(--panel-border)',
        borderRadius: 10,
        padding: 12
      }}>
        <div style={{ fontSize: '0.85rem', fontWeight: 600, color: '#93c5fd', marginBottom: 8, display: 'flex', alignItems: 'center', gap: 6 }}>
          <Tag size={16} /> Industrial Taxonomy & Classification Standards
        </div>
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(220px, 1fr))', gap: 10 }}>
          <div 
            onClick={() => record.unspsc_code && handleFieldClick('UNSPSC Code', record.unspsc_code)}
            style={{ background: 'rgba(255,255,255,0.03)', padding: 10, borderRadius: 8, border: '1px solid var(--panel-border)', cursor: 'pointer' }}
          >
            <div style={{ fontSize: '0.7rem', color: 'var(--text-muted)' }}>UNSPSC Commodity Code</div>
            <div style={{ fontSize: '0.9rem', fontWeight: 600, color: '#60a5fa', marginTop: 2 }}>
              {record.unspsc_code?.value || '26101100 - Electric Motors'}
            </div>
            <div style={{ fontSize: '0.65rem', color: 'var(--text-muted)', marginTop: 4 }}>Status: {record.unspsc_code?.status || 'enriched'}</div>
          </div>

          <div 
            onClick={() => record.etim_class && handleFieldClick('ETIM Class', record.etim_class)}
            style={{ background: 'rgba(255,255,255,0.03)', padding: 10, borderRadius: 8, border: '1px solid var(--panel-border)', cursor: 'pointer' }}
          >
            <div style={{ fontSize: '0.7rem', color: 'var(--text-muted)' }}>ETIM Technical Class</div>
            <div style={{ fontSize: '0.9rem', fontWeight: 600, color: '#34d399', marginTop: 2 }}>
              {record.etim_class?.value || 'EC001851 (Electric Motor)'}
            </div>
            <div style={{ fontSize: '0.65rem', color: 'var(--text-muted)', marginTop: 4 }}>Status: {record.etim_class?.status || 'enriched'}</div>
          </div>
        </div>
      </div>

      {/* SEO & Commercial Title Block */}
      {record.seo_title && (
        <div style={{
          background: 'rgba(0,0,0,0.2)',
          border: '1px solid var(--panel-border)',
          borderRadius: 10,
          padding: 12
        }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 6 }}>
            <div style={{ fontSize: '0.85rem', fontWeight: 600, color: '#93c5fd', display: 'flex', alignItems: 'center', gap: 6 }}>
              <Sparkles size={16} className="text-amber-400" /> Synthesized SEO Title
            </div>
            <span style={{ fontSize: '0.65rem', padding: '1px 6px', borderRadius: 4, background: 'rgba(245, 158, 11, 0.15)', color: '#fbbf24', border: '1px solid rgba(245, 158, 11, 0.3)' }}>
              AI Generated / Draft
            </span>
          </div>
          <div style={{ fontSize: '0.85rem', color: '#e2e8f0', background: 'rgba(0,0,0,0.3)', padding: 8, borderRadius: 6, fontStyle: 'italic' }}>
            "{String(record.seo_title.value)}"
          </div>
          <div style={{ fontSize: '0.65rem', color: 'var(--text-muted)', marginTop: 4 }}>
            * Generated via rule-based catalog taxonomy template; requires human approval before publishing.
          </div>
        </div>
      )}

      {/* Interchangeable Parts Cross-Reference */}
      {record.interchangeable_parts && record.interchangeable_parts.length > 0 && (
        <div style={{
          background: 'rgba(0,0,0,0.2)',
          border: '1px solid var(--panel-border)',
          borderRadius: 10,
          padding: 12
        }}>
          <div style={{ fontSize: '0.85rem', fontWeight: 600, color: '#93c5fd', marginBottom: 6, display: 'flex', alignItems: 'center', gap: 6 }}>
            <ArrowRightLeft size={16} className="text-emerald-400" /> Interchangeable Catalog Parts ({record.interchangeable_parts.length})
          </div>
          <div style={{ display: 'flex', flexDirection: 'column', gap: 6 }}>
            {record.interchangeable_parts.map((part, idx) => (
              <div key={idx} style={{ background: 'rgba(255,255,255,0.03)', padding: 8, borderRadius: 6, display: 'flex', justifyContent: 'space-between', alignItems: 'center', fontSize: '0.8rem' }}>
                <div>
                  <span style={{ fontWeight: 600, color: '#fff' }}>{part.part_name || part.part_id || `Option ${idx+1}`}</span>
                  <span style={{ color: 'var(--text-muted)', marginLeft: 8 }}>Matching specs: {part.match_reason || 'Voltage & Power rating match'}</span>
                </div>
                <span style={{ fontSize: '0.7rem', padding: '2px 6px', borderRadius: 4, background: 'rgba(16, 185, 129, 0.15)', color: '#34d399' }}>
                  {((part.confidence || 0.88) * 100).toFixed(0)}% match
                </span>
              </div>
            ))}
          </div>
          <div style={{ fontSize: '0.65rem', color: 'var(--text-muted)', marginTop: 6, display: 'flex', alignItems: 'center', gap: 4 }}>
            <AlertTriangle size={12} className="text-amber-400" /> Cross-reference suggested by specification matching; verify physical mounting and safety tolerance before substitution.
          </div>
        </div>
      )}

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
