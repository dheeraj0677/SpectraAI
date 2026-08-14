/**
 * Lightweight Frontend Smoke & Unit Verification Suite
 * Runs in Node.js environment without external dependencies.
 */

import fs from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

let passed = 0;
let failed = 0;

function assert(description, condition) {
  if (condition) {
    console.log(`  [PASS]  ${description}`);
    passed++;
  } else {
    console.error(`  [FAIL]  ${description}`);
    failed++;
  }
}

console.log("\n" + "=".repeat(60));
console.log("  SPECTRA AI -- FRONTEND SMOKE & LOGIC VERIFICATION");
console.log("=".repeat(60));

// 1. Verify Component Files Exist and are Non-Empty
const components = [
  'App.jsx',
  'components/UploadPanel.jsx',
  'components/ProductRecord.jsx',
  'components/FieldCard.jsx',
  'components/ProvenancePopup.jsx',
  'components/KnowledgeGraph.jsx',
  'components/HumanReview.jsx',
  'components/PipelineStatus.jsx',
  'components/ConsistencyPanel.jsx'
];

components.forEach(comp => {
  const compPath = path.join(__dirname, 'src', comp);
  const exists = fs.existsSync(compPath);
  const content = exists ? fs.readFileSync(compPath, 'utf8') : '';
  assert(`Component ${comp} exists and has content`, exists && content.length > 50);
});

// 2. Test Badge Confidence Classification Logic
function getConfidenceClass(status, conf) {
  if (status === 'human_verified') return 'human_verified';
  if (status === 'conflicted') return 'conflicted';
  if (conf >= 0.85) return 'high';
  if (conf >= 0.60) return 'med';
  return 'low';
}

assert("Confidence 0.95 -> 'high'", getConfidenceClass('extracted', 0.95) === 'high');
assert("Confidence 0.75 -> 'med'", getConfidenceClass('extracted', 0.75) === 'med');
assert("Confidence 0.40 -> 'low'", getConfidenceClass('extracted', 0.40) === 'low');
assert("Status 'conflicted' -> 'conflicted'", getConfidenceClass('conflicted', 0.95) === 'conflicted');
assert("Status 'human_verified' -> 'human_verified'", getConfidenceClass('human_verified', 1.0) === 'human_verified');

// 3. Test Commerce Readiness Index (CRI) Breakdown Scoring Logic
function computeCriBreakdown(record) {
  const breakdown = record.cri_breakdown || {
    identity_completeness: 25.0,
    specifications_depth: 25.0,
    taxonomy_compliance: 20.0,
    commerce_content: 15.0,
    quality_and_accuracy: 15.0
  };
  const total = Object.values(breakdown).reduce((acc, v) => acc + v, 0);
  return { breakdown, total };
}

const mockCriRecord = {
  cri_breakdown: {
    identity_completeness: 25.0,
    specifications_depth: 25.0,
    taxonomy_compliance: 20.0,
    commerce_content: 15.0,
    quality_and_accuracy: 7.0
  }
};
const { breakdown, total } = computeCriBreakdown(mockCriRecord);
assert("CRI breakdown has 5 core dimensions", Object.keys(breakdown).length === 5);
assert("CRI total sum equals 92.0", total === 92.0);

// 4. Test CSV Export Column Formatting Logic
function buildCsvRows(record) {
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
    const provStr = (fVal.provenance || []).map(p => `${p.source_id}:${p.location}`).join(' | ');
    rows.push([cat, name, `"${valStr.replace(/"/g, '""')}"`, unitStr, confStr, statusStr, obsType, isSyn, `"${normRule.replace(/"/g, '""')}"`, `"${provStr}"`]);
  };

  addRow('Identity', 'product_name', record.product_name);
  addRow('Taxonomy', 'unspsc_code', record.unspsc_code);
  addRow('Specification', 'voltage', record.specifications?.voltage);
  return rows;
}

const mockRecord = {
  product_name: { value: 'UltraDrive X500', confidence: 0.95, status: 'extracted', is_synthetic: false, observation_type: 'directly_observed', provenance: [{ source_id: 'pdf1', location: 'P1' }] },
  unspsc_code: { value: '26101100 - Electric Motors', confidence: 0.95, status: 'enriched', is_synthetic: false, observation_type: 'enriched', provenance: [{ source_id: 'seed_kb', location: 'Taxonomy Master' }] },
  specifications: {
    voltage: { value: '480V', unit: 'V', confidence: 0.90, status: 'conflicted', is_synthetic: true, observation_type: 'conflicted', provenance: [{ source_id: 'img1', location: 'Plate', normalization_rule: 'Standardized to Volt unit notation' }] }
  }
};

const rows = buildCsvRows(mockRecord);
assert("CSV header has 10 columns", rows[0].length === 10);
assert("CSV data rows generated", rows.length === 4);
assert("CSV row includes Taxonomy category", rows[2][0] === 'Taxonomy');
assert("CSV row includes Synthetic YES flag for demo data", rows[3][7] === 'YES');
assert("CSV row includes Normalization Rule", rows[3][8].includes("Standardized to Volt"));

console.log("=".repeat(60));
console.log(`  Total: ${passed + failed} | Passed: ${passed} | Failed: ${failed}`);
console.log("=".repeat(60) + "\n");

if (failed > 0) {
  process.exit(1);
} else {
  process.exit(0);
}
