const API_BASE = 'http://localhost:8000/api';

export async function uploadFiles(files) {
  const formData = new FormData();
  for (const file of files) {
    formData.append('files', file);
  }
  const res = await fetch(`${API_BASE}/upload`, {
    method: 'POST',
    body: formData,
  });
  if (!res.ok) throw new Error('Upload failed');
  return res.json();
}

export async function startPipeline(sourceIds, productId = null) {
  const res = await fetch(`${API_BASE}/pipeline/run`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ source_ids: sourceIds, product_id: productId }),
  });
  if (!res.ok) throw new Error('Pipeline start failed');
  return res.json();
}

export async function loadSampleBatch() {
  const res = await fetch(`${API_BASE}/demo/load-sample`, {
    method: 'POST',
  });
  if (!res.ok) throw new Error('Sample batch trigger failed');
  return res.json();
}

export async function fetchProducts() {
  const res = await fetch(`${API_BASE}/products`);
  if (!res.ok) throw new Error('Failed to fetch products');
  return res.json();
}

export async function fetchProduct(productId) {
  const res = await fetch(`${API_BASE}/products/${productId}`);
  if (!res.ok) throw new Error('Failed to fetch product details');
  return res.json();
}

export async function editField(productId, fieldName, value, unit = null, reviewer = 'human_reviewer', reason = 'Human correction applied') {
  const res = await fetch(`${API_BASE}/products/${productId}/fields/${fieldName}`, {
    method: 'PUT',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ value, unit, reviewer, reason }),
  });
  if (!res.ok) throw new Error('Failed to update field');
  return res.json();
}

export async function approveRecord(productId, reviewer = 'human_reviewer') {
  const res = await fetch(`${API_BASE}/products/${productId}/approve?reviewer=${encodeURIComponent(reviewer)}`, {
    method: 'POST',
  });
  if (!res.ok) throw new Error('Failed to approve record');
  return res.json();
}

export async function fetchKnowledgeGraph() {
  const res = await fetch(`${API_BASE}/graph`);
  if (!res.ok) throw new Error('Failed to fetch knowledge graph');
  return res.json();
}

export async function fetchEditHistory(productId) {
  const res = await fetch(`${API_BASE}/products/${productId}/history`);
  if (!res.ok) throw new Error('Failed to fetch edit history');
  return res.json();
}
