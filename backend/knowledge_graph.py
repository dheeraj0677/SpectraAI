import networkx as nx
from typing import Dict, Any, List, Optional
from models import ProductRecord

# Global NetworkX directed graph
G = nx.DiGraph()

# Seed default graph nodes & relationships for demo catalog consistency checks
def init_seed_graph():
    # Pre-seed some reference products in category for sibling comparison
    G.add_node("prod_ref_101", label="Ref-Drive X400", type="product", category="Industrial Motors & Drives", weight_kg=45.0, voltage="480V")
    G.add_node("prod_ref_102", label="Ref-Drive X450", type="product", category="Industrial Motors & Drives", weight_kg=46.2, voltage="480V")
    G.add_node("Industrial Motors & Drives", label="Industrial Motors & Drives", type="category")
    G.add_edge("prod_ref_101", "Industrial Motors & Drives", relation="belongs_to")
    G.add_edge("prod_ref_102", "Industrial Motors & Drives", relation="belongs_to")

    # Add accessories & compatibility nodes
    G.add_node("acc_resistor_mod", label="Braking Resistor Module", type="accessory")
    G.add_node("acc_flange_kit", label="Mounting Flange Kit", type="accessory")
    G.add_edge("prod_ref_101", "acc_resistor_mod", relation="has_accessory")
    G.add_edge("prod_ref_102", "acc_flange_kit", relation="has_accessory")

init_seed_graph()

def add_product_to_graph(record: ProductRecord):
    pid = record.product_id
    pname = str(record.product_name.value) if record.product_name.value else pid
    cat = str(record.category.value) if record.category.value else "Uncategorized"
    
    # Extract weight for stat calculations if available
    weight_val = None
    if "weight_kg" in record.specifications and record.specifications["weight_kg"].value:
        try:
            weight_val = float(record.specifications["weight_kg"].value)
        except (ValueError, TypeError):
            pass

    voltage_val = None
    if "voltage" in record.specifications and record.specifications["voltage"].value:
        voltage_val = str(record.specifications["voltage"].value)

    G.add_node(pid, label=pname, type="product", category=cat, weight_kg=weight_val, voltage=voltage_val)
    G.add_node(cat, label=cat, type="category")
    G.add_edge(pid, cat, relation="belongs_to")

    for acc in record.accessories:
        acc_id = f"acc_{acc.lower().replace(' ', '_')}"
        G.add_node(acc_id, label=acc, type="accessory")
        G.add_edge(pid, acc_id, relation="has_accessory")

    for comp in record.compatible_with:
        comp_id = f"prod_{comp.lower().replace(' ', '_')}"
        G.add_node(comp_id, label=comp, type="product", category=cat)
        G.add_edge(pid, comp_id, relation="compatible_with")

    if record.replaces:
        rep_id = f"prod_{record.replaces.lower().replace(' ', '_')}"
        G.add_node(rep_id, label=record.replaces, type="product", category=cat)
        G.add_edge(pid, rep_id, relation="replaces")

def find_category_siblings(record: ProductRecord) -> List[str]:
    cat = str(record.category.value) if record.category.value else "Uncategorized"
    if cat not in G:
        return []
    siblings = [n for n in G.predecessors(cat) if n != record.product_id]
    return siblings

def check_consistency(record: ProductRecord) -> List[Dict[str, Any]]:
    warnings = []
    siblings = find_category_siblings(record)
    
    # Weight outlier check vs category siblings
    if "weight_kg" in record.specifications and record.specifications["weight_kg"].value:
        try:
            current_weight = float(record.specifications["weight_kg"].value)
            sibling_weights = [G.nodes[s]["weight_kg"] for s in siblings if "weight_kg" in G.nodes[s] and G.nodes[s]["weight_kg"] is not None]
            if sibling_weights:
                avg_weight = sum(sibling_weights) / len(sibling_weights)
                if current_weight > avg_weight * 2.5 or current_weight < avg_weight * 0.3:
                    warnings.append({
                        "field": "weight_kg",
                        "severity": "warning",
                        "message": f"Weight ({current_weight} kg) deviates significantly from category average ({avg_weight:.1f} kg) across {len(sibling_weights)} sibling products.",
                        "category_avg": round(avg_weight, 1),
                        "current_value": current_weight
                    })
        except (ValueError, TypeError):
            pass

    return warnings

def export_graph_json() -> Dict[str, Any]:
    """Export graph for D3 force-directed visualization in React."""
    nodes = []
    for n, data in G.nodes(data=True):
        node_info = {
            "id": n,
            "label": data.get("label", n),
            "type": data.get("type", "product"),
            "category": data.get("category", "")
        }
        nodes.append(node_info)

    links = []
    for u, v, data in G.edges(data=True):
        links.append({
            "source": u,
            "target": v,
            "relation": data.get("relation", "connected_to")
        })

    return {"nodes": nodes, "links": links}
