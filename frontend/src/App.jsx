import React, { useState, useEffect } from 'react';
import UploadPanel from './components/UploadPanel';
import PipelineStatus from './components/PipelineStatus';
import ProductRecord from './components/ProductRecord';
import KnowledgeGraph from './components/KnowledgeGraph';
import ConsistencyPanel from './components/ConsistencyPanel';
import HumanReview from './components/HumanReview';
import { fetchProducts, fetchProduct } from './api';
import { Cpu, RefreshCw, Sparkles, Layers } from 'lucide-react';

export default function App() {
  const [activeJobId, setActiveJobId] = useState(null);
  const [productList, setProductList] = useState([]);
  const [selectedProduct, setSelectedProduct] = useState(null);

  const loadProducts = async () => {
    try {
      const data = await fetchProducts();
      setProductList(data.products || []);
      if (data.products && data.products.length > 0 && !selectedProduct) {
        loadSingleProduct(data.products[0].product_id);
      }
    } catch (e) {
      console.error('Failed to load products:', e);
    }
  };

  const loadSingleProduct = async (pid) => {
    try {
      const prod = await fetchProduct(pid);
      setSelectedProduct(prod);
    } catch (e) {
      console.error(`Failed to load product ${pid}:`, e);
    }
  };

  useEffect(() => {
    loadProducts();
  }, []);

  const handlePipelineStarted = (jobId) => {
    setActiveJobId(jobId);
  };

  const handlePipelineComplete = async () => {
    await loadProducts();
  };

  return (
    <div className="app-container">
      {/* Header */}
      <header className="app-header">
        <div className="brand">
          <div className="brand-icon">
            <Cpu size={20} />
          </div>
          <div>
            <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
              <h1 className="brand-title">SpectraAI</h1>
              <span className="brand-badge">Multimodal Intelligence</span>
            </div>
            <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>
              Messy Datasheets → Structured, Validated, Source-Cited Product Intelligence
            </div>
          </div>
        </div>

        <div style={{ display: 'flex', alignItems: 'center', gap: 12 }}>
          {productList.length > 0 && (
            <select 
              value={selectedProduct?.product_id || ''} 
              onChange={(e) => loadSingleProduct(e.target.value)}
              style={{ padding: '6px 12px', borderRadius: 8, background: '#1e293b', color: '#fff', border: '1px solid var(--panel-border)', fontSize: '0.85rem' }}
            >
              {productList.map(p => (
                <option key={p.product_id} value={p.product_id}>
                  {p.product_name} ({p.product_id})
                </option>
              ))}
            </select>
          )}

          <button 
            onClick={loadProducts} 
            style={{ background: 'rgba(255,255,255,0.06)', border: '1px solid var(--panel-border)', color: '#fff', padding: 8, borderRadius: 8, cursor: 'pointer' }}
            title="Refresh Products"
          >
            <RefreshCw size={16} />
          </button>
        </div>
      </header>

      {/* Main 3-Panel Dashboard Grid */}
      <main className="dashboard-grid">
        {/* Left Panel: Ingest & Pipeline Status */}
        <section className="panel">
          <div className="panel-header">
            <span>1. Ingestion & Pipeline</span>
            <Layers size={16} className="text-blue-400" />
          </div>
          <div className="panel-body">
            <UploadPanel onPipelineStarted={handlePipelineStarted} />
            {activeJobId && (
              <PipelineStatus jobId={activeJobId} onComplete={handlePipelineComplete} />
            )}
          </div>
        </section>

        {/* Center Panel: Structured Product Record */}
        <section className="panel">
          <div className="panel-header">
            <span>2. Structured Product Record & Provenance</span>
            <Sparkles size={16} className="text-cyan-400" />
          </div>
          <div className="panel-body">
            <ProductRecord 
              record={selectedProduct} 
              onEditField={(field, val) => {}}
            />
          </div>
        </section>

        {/* Right Panel: Knowledge Graph & Catalog Consistency */}
        <section className="panel">
          <div className="panel-header">
            <span>3. Knowledge Graph & Consistency</span>
            <Cpu size={16} className="text-purple-400" />
          </div>
          <div className="panel-body">
            <KnowledgeGraph activeProductId={selectedProduct?.product_id} />
            <ConsistencyPanel warnings={selectedProduct?.consistency_warnings} />
          </div>
        </section>
      </main>

      {/* Bottom Bar: Human-in-the-Loop Review */}
      <footer style={{ flexShrink: 0 }}>
        <HumanReview 
          record={selectedProduct} 
          onRecordUpdated={(updated) => setSelectedProduct(updated)}
        />
      </footer>
    </div>
  );
}
