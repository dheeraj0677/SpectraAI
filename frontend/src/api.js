import { DEMO_PRODUCTS, DEMO_GRAPH } from './demoData';

export const API_BASE = import.meta.env.VITE_API_BASE || 
  ((typeof window !== 'undefined' && (window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1')) 
    ? 'http://localhost:8000/api' 
    : '/api');

// In-memory fallback state for standalone/offline Netlify hosting
let mockProducts = JSON.parse(JSON.stringify(DEMO_PRODUCTS));
let mockEditHistory = {};

export async function uploadFiles(files) {
  try {
    const formData = new FormData();
    for (const file of files) {
      formData.append('files', file);
    }
    const res = await fetch(`${API_BASE}/upload`, {
      method: 'POST',
      body: formData,
    });
    if (!res.ok) throw new Error('Upload failed');
    return await res.json();
  } catch (err) {
    console.warn('Backend unavailable, using simulated upload response:', err);
    return {
      uploaded_sources: Array.from(files).map((f, idx) => ({
        source_id: `src_uploaded_${idx}_${Date.now()}`,
        filename: f.name,
        source_type: f.name.endsWith('.pdf') ? 'datasheet_pdf' : f.name.endsWith('.csv') ? 'erp_csv' : 'nameplate_image',
        size_bytes: f.size
      }))
    };
  }
}

export async function startPipeline(sourceIds, productId = null) {
  try {
    const res = await fetch(`${API_BASE}/pipeline/run`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ source_ids: sourceIds, product_id: productId }),
    });
    if (!res.ok) throw new Error('Pipeline start failed');
    return await res.json();
  } catch (err) {
    console.warn('Backend unavailable, using simulated pipeline start:', err);
    const mockJobId = 'job_mock_' + Math.random().toString(36).substring(2, 9);
    return {
      job_id: mockJobId,
      status: 'started',
      product_id: productId || 'PROD-DEMO-X500',
      message: 'Intelligence pipeline execution simulated in offline mode'
    };
  }
}

export async function loadSampleBatch() {
  try {
    const res = await fetch(`${API_BASE}/demo/load-sample`, {
      method: 'POST',
    });
    if (!res.ok) throw new Error('Sample batch trigger failed');
    return await res.json();
  } catch (err) {
    console.warn('Backend unavailable, loading sample batch locally:', err);
    const mockJobId = 'job_sample_' + Math.random().toString(36).substring(2, 9);
    return {
      job_id: mockJobId,
      status: 'started',
      product_id: 'PROD-DEMO-X500',
      sources_loaded: ['pdf_sample', 'image_sample', 'csv_sample']
    };
  }
}

export async function fetchProducts() {
  try {
    const res = await fetch(`${API_BASE}/products`);
    if (!res.ok) throw new Error('Failed to fetch products');
    return await res.json();
  } catch (err) {
    console.warn('Backend unavailable, returning demo product list:', err);
    return {
      total: mockProducts.length,
      products: mockProducts.map(p => ({
        product_id: p.product_id,
        product_name: p.product_name?.value || p.product_id,
        category: p.category?.value || 'General',
        cri_score: p.commerce_readiness_score || 90.0,
        review_status: p.review_status || 'needs_review'
      }))
    };
  }
}

export async function fetchProduct(productId) {
  try {
    const res = await fetch(`${API_BASE}/products/${productId}`);
    if (!res.ok) throw new Error('Failed to fetch product details');
    return await res.json();
  } catch (err) {
    console.warn(`Backend unavailable, returning local product ${productId}:`, err);
    const found = mockProducts.find(p => p.product_id === productId) || mockProducts[0];
    return JSON.parse(JSON.stringify(found));
  }
}

export async function editField(productId, fieldName, value, unit = null, reviewer = 'human_reviewer', reason = 'Human correction applied') {
  try {
    const res = await fetch(`${API_BASE}/products/${productId}/fields/${fieldName}`, {
      method: 'PUT',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ value, unit, reviewer, reason }),
    });
    if (!res.ok) throw new Error('Failed to update field');
    return await res.json();
  } catch (err) {
    console.warn(`Backend unavailable, applying local edit for ${fieldName}:`, err);
    const prod = mockProducts.find(p => p.product_id === productId) || mockProducts[0];
    
    // Record history
    if (!mockEditHistory[productId]) mockEditHistory[productId] = [];
    const prevVal = prod.specifications?.[fieldName]?.value ?? prod[fieldName]?.value ?? 'N/A';
    mockEditHistory[productId].unshift({
      timestamp: new Date().toISOString(),
      field: fieldName,
      previous_value: prevVal,
      new_value: value,
      unit: unit,
      reviewer: reviewer,
      reason: reason
    });

    const updatedField = {
      value: value,
      unit: unit,
      confidence: 1.0,
      status: 'human_verified',
      provenance: [
        {
          source_id: 'human_review_portal',
          source_type: 'manual_override',
          location: 'Human Review Interface',
          extraction_method: 'human_in_the_loop',
          confidence: 1.0,
          raw_snippet: `Human correction by ${reviewer}: ${reason}`,
          is_synthetic: false,
          raw_value: value,
          raw_unit: unit,
          normalized_value: value,
          normalized_unit: unit,
          normalization_rule: 'Human verification override'
        }
      ],
      conflict_candidates: null,
      is_synthetic: false,
      observation_type: 'directly_observed'
    };

    if (prod.specifications && prod.specifications[fieldName]) {
      prod.specifications[fieldName] = updatedField;
    } else if (prod[fieldName]) {
      prod[fieldName] = updatedField;
    } else {
      if (!prod.specifications) prod.specifications = {};
      prod.specifications[fieldName] = updatedField;
    }

    return {
      status: 'success',
      product_id: productId,
      field: fieldName,
      record: JSON.parse(JSON.stringify(prod))
    };
  }
}

export async function approveRecord(productId, reviewer = 'human_reviewer') {
  try {
    const res = await fetch(`${API_BASE}/products/${productId}/approve?reviewer=${encodeURIComponent(reviewer)}`, {
      method: 'POST',
    });
    if (!res.ok) throw new Error('Failed to approve record');
    return await res.json();
  } catch (err) {
    console.warn(`Backend unavailable, applying local approve for ${productId}:`, err);
    const prod = mockProducts.find(p => p.product_id === productId) || mockProducts[0];
    prod.review_status = 'approved';
    return {
      status: 'approved',
      product_id: productId,
      reviewer: reviewer,
      record: JSON.parse(JSON.stringify(prod))
    };
  }
}

export async function fetchKnowledgeGraph() {
  try {
    const res = await fetch(`${API_BASE}/graph`);
    if (!res.ok) throw new Error('Failed to fetch knowledge graph');
    return await res.json();
  } catch (err) {
    console.warn('Backend unavailable, returning demo knowledge graph:', err);
    return JSON.parse(JSON.stringify(DEMO_GRAPH));
  }
}

export async function fetchEditHistory(productId) {
  try {
    const res = await fetch(`${API_BASE}/products/${productId}/history`);
    if (!res.ok) throw new Error('Failed to fetch edit history');
    return await res.json();
  } catch (err) {
    console.warn(`Backend unavailable, returning local history for ${productId}:`, err);
    return {
      product_id: productId,
      total_edits: (mockEditHistory[productId] || []).length,
      edit_history: mockEditHistory[productId] || []
    };
  }
}
