#!/usr/bin/env python3
"""Generate memory graph JSON data from all memory/notes files."""
import os, re, json, glob
from pathlib import Path
from collections import defaultdict
from datetime import datetime

WORKSPACE = os.path.expanduser("~/.openclaw/workspace")
GRAPH_DIR = os.path.join(WORKSPACE, "skills/memory-graph/www")
GRAPH_DATA = os.path.join(GRAPH_DIR, "graph-data.json")

# Known entities to track
PEOPLE = ["Andrew", "Anjaly", "Zenius", "Kesya", "Sidik", "Rusdiana", "Angeline",
          "Suhe", "Darren", "Leydea", "Ley"]
PROJECTS = ["Smart Tourism", "Barelang", "INFOVG", "BRU", "Coretax", "WhatsApp",
            "Telegram", "GitHub", "OpenClaw", "MiniMax", "Mac mini"]

COLOR_MAP = {
    "person": "#f59e0b",    # amber
    "project": "#10b981",   # green
    "date": "#7c3aed",     # purple
    "topic": "#00f0ff",    # cyan
    "default": "#94a3b8",  # gray
}

def extract_entities(content):
    """Extract named entities from content."""
    entities = {"person": [], "project": [], "date": [], "topic": []}

    # People
    for name in PEOPLE:
        if name in content:
            entities["person"].append(name)

    # Projects
    for proj in PROJECTS:
        if proj.lower() in content.lower():
            entities["project"].append(proj)

    # Dates (YYYY-MM-DD or Month YYYY)
    dates = re.findall(r'\d{4}-\d{2}-\d{2}', content)
    for d in set(dates):
        entities["date"].append(d)

    # Topics (capitalized hashtags)
    topics = re.findall(r'#([a-zA-Z][a-zA-Z0-9-]{2,20})', content)
    for t in set(topics):
        if t.lower() not in ["atomic", "note", "memory", "openclaw"]:
            entities["topic"].append(t.lower())

    return entities

def build_graph():
    nodes = []
    links = []
    node_ids = {}
    entity_counts = defaultdict(int)
    all_entities = defaultdict(list)  # entity -> note_ids

    search_dirs = [
        os.path.join(WORKSPACE, "memory"),
        os.path.join(WORKSPACE, "notes"),
    ]

    # First pass: collect all entities per note
    note_entities = {}
    note_id = 0

    for search_dir in search_dirs:
        if not os.path.exists(search_dir):
            continue
        for fpath in glob.glob(os.path.join(search_dir, "**/*.md"), recursive=True):
            if "/dreaming/" in fpath or "/archive/" in fpath:
                continue
            try:
                with open(fpath) as f:
                    content = f.read()
            except:
                continue

            fname = Path(fpath).stem
            entities = extract_entities(content)
            note_id_str = f"note_{note_id}"
            note_entities[note_id_str] = {
                "id": note_id_str,
                "name": fname,
                "file": os.path.relpath(fpath, WORKSPACE),
                "entities": entities
            }
            node_ids[note_id_str] = len(nodes)
            nodes.append({
                "id": note_id_str,
                "name": fname,
                "file": os.path.relpath(fpath, WORKSPACE),
                "type": "note",
                "color": "#1e293b",
                "size": 8,
                "entities": {k: len(v) for k, v in entities.items()}
            })

            for etype, elist in entities.items():
                for e in set(elist):
                    all_entities[f"{etype}:{e}"].append(note_id_str)
                    entity_counts[f"{etype}:{e}"] += 1

            note_id += 1

    # Second pass: create links between notes that share entities
    link_set = set()
    for entity_key, note_ids in all_entities.items():
        if len(note_ids) < 2:
            continue
        etype, ename = entity_key.split(":", 1)
        for i in range(len(note_ids)):
            for j in range(i+1, len(note_ids)):
                n1, n2 = note_ids[i], note_ids[j]
                link_key = tuple(sorted([n1, n2]))
                if link_key not in link_set:
                    link_set.add(link_key)
                    links.append({
                        "source": n1,
                        "target": n2,
                        "entity": ename,
                        "type": etype,
                        "color": COLOR_MAP.get(etype, COLOR_MAP["default"])
                    })

    # Add entity nodes
    entity_node_id = {}
    for entity_key, count in entity_counts.items():
        if count < 1:
            continue
        etype, ename = entity_key.split(":", 1)
        eid = f"entity:{ename}"
        if eid in entity_node_id:
            continue
        entity_node_id[eid] = len(nodes)
        nodes.append({
            "id": eid,
            "name": ename,
            "type": etype,
            "color": COLOR_MAP.get(etype, COLOR_MAP["default"]),
            "size": min(6 + count * 2, 28),
            "isEntity": True
        })

    # Update links to use entity node IDs
    for link in links:
        sid = link["source"]
        tid = link["target"]
        # Don't create links between entity nodes and notes through this path
        # Keep as note-to-note

    # Update node sizes based on link count
    link_counts = defaultdict(int)
    for link in links:
        link_counts[link["source"]] += 1
        link_counts[link["target"]] += 1
    for node in nodes:
        if not node.get("isEntity"):
            node["size"] = max(6, min(24, 6 + link_counts[node["id"]] * 3))

    graph = {"nodes": nodes, "links": links}
    os.makedirs(GRAPH_DIR, exist_ok=True)
    with open(GRAPH_DATA, "w") as f:
        json.dump(graph, f, indent=2)
    print(f"Graph data: {len(nodes)} nodes, {len(links)} links")
    print(f"Saved to: {GRAPH_DATA}")
    return graph

if __name__ == "__main__":
    build_graph()
