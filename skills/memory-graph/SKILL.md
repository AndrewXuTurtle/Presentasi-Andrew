# Memory Graph Skill

## When to Use
Trigger when Andrew wants to see a visual map of his knowledge — "show me my memory", "open memory graph", "knowledge map", "show connections".

## Trigger Phrases
- "show memory graph"
- "open knowledge graph"
- "knowledge map"
- "show connections"
- "memory web"
- "graph view"

## What It Does
Generates an interactive D3.js force-directed graph showing all memory notes as nodes, connected by shared concepts (people, topics, dates).

## Visual Design
- **Nodes** = notes (sized by number of connections)
- **Lines** = shared concepts/people
- **Colors** = by type (person, project, topic, date cluster)
- **Hover** = shows note title and date
- **Click** = opens the note
- **Scroll** = zoom in/out
- **Drag** = rearrange nodes

## Output
Opens in browser: `http://localhost:8765/memory-graph/`

## Script
```bash
python3 ~/openclaw/workspace/skills/memory-graph/scripts/generate_graph.py
# Then open http://localhost:8765/memory-graph/index.html
```

## Ports
- If port 8765 busy, tries 8766, 8767
- Also saves static HTML to: `~/openclaw/workspace/memory-graph/index.html`
