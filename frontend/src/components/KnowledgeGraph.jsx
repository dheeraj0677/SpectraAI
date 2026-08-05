import React, { useEffect, useRef, useState } from 'react';
import * as d3 from 'd3';
import { fetchKnowledgeGraph } from '../api';
import { Network } from 'lucide-react';

export default function KnowledgeGraph({ activeProductId }) {
  const svgRef = useRef(null);
  const [graphData, setGraphData] = useState({ nodes: [], links: [] });

  const loadGraph = async () => {
    try {
      const data = await fetchKnowledgeGraph();
      setGraphData(data);
    } catch (e) {
      console.error('Failed to load graph:', e);
    }
  };

  useEffect(() => {
    loadGraph();
  }, [activeProductId]);

  useEffect(() => {
    if (!svgRef.current || !graphData.nodes || graphData.nodes.length === 0) return;

    const width = svgRef.current.clientWidth || 300;
    const height = 240;

    const svg = d3.select(svgRef.current);
    svg.selectAll('*').remove();

    const simulation = d3.forceSimulation(graphData.nodes)
      .force('link', d3.forceLink(graphData.links).id(d => d.id).distance(60))
      .force('charge', d3.forceManyBody().strength(-150))
      .force('center', d3.forceCenter(width / 2, height / 2));

    // Links
    const link = svg.append('g')
      .selectAll('line')
      .data(graphData.links)
      .enter()
      .append('line')
      .attr('stroke', 'rgba(255,255,255,0.15)')
      .attr('stroke-width', 1.5);

    // Nodes
    const node = svg.append('g')
      .selectAll('g')
      .data(graphData.nodes)
      .enter()
      .append('g')
      .call(d3.drag()
        .on('start', dragstarted)
        .on('drag', dragged)
        .on('end', dragended));

    node.append('circle')
      .attr('r', d => d.type === 'category' ? 12 : d.id === activeProductId ? 10 : 7)
      .attr('fill', d => {
        if (d.type === 'category') return '#8b5cf6';
        if (d.type === 'accessory') return '#10b981';
        if (d.id === activeProductId) return '#3b82f6';
        return '#06b6d4';
      })
      .attr('stroke', d => d.id === activeProductId ? '#ffffff' : 'none')
      .attr('stroke-width', 2);

    node.append('text')
      .text(d => d.label)
      .attr('x', 10)
      .attr('y', 4)
      .attr('fill', '#94a3b8')
      .attr('font-size', '9px')
      .attr('font-family', 'Inter, sans-serif');

    simulation.on('tick', () => {
      link
        .attr('x1', d => d.source.x)
        .attr('y1', d => d.source.y)
        .attr('x2', d => d.target.x)
        .attr('y2', d => d.target.y);

      node
        .attr('transform', d => `translate(${d.x},${d.y})`);
    });

    function dragstarted(event, d) {
      if (!event.active) simulation.alphaTarget(0.3).restart();
      d.fx = d.x;
      d.fy = d.y;
    }

    function dragged(event, d) {
      d.fx = event.x;
      d.fy = event.y;
    }

    function dragended(event, d) {
      if (!event.active) simulation.alphaTarget(0);
      d.fx = null;
      d.fy = null;
    }
  }, [graphData, activeProductId]);

  return (
    <div style={{ background: 'rgba(0,0,0,0.3)', borderRadius: 10, padding: 12, border: '1px solid var(--panel-border)' }}>
      <div style={{ display: 'flex', alignItems: 'center', gap: 6, fontSize: '0.8rem', fontWeight: 600, color: '#c084fc', marginBottom: 8 }}>
        <Network size={14} /> NetworkX Product Graph View
      </div>
      <svg ref={svgRef} style={{ width: '100%', height: 240, background: 'transparent' }} />
    </div>
  );
}
