# Publish Note Skill

## When to Use
Trigger when Andrew wants to share a note publicly as a URL.

## Trigger Phrases
- "publish this note"
- "share this as a link"
- "make this public"
- "publish [filename]"
- "share note [name]"

## What It Does
1. Takes a note from workspace (`.md`)
2. Converts it to a standalone HTML page with nice styling
3. Pushes to a `published/` branch on GitHub
4. Returns a public GitHub Pages URL

## Setup
Requires:
- GitHub Pages enabled on `AndrewXuTurtle/openclaw-oneclick`
- `published/` branch exists (skill creates it on first run)

## Usage
```
/publish notes/my-idea.md
/publish memory/2026-04-14
```

## Output
Posts back: "Published! 🔗 https://andrewxuturtle.github.io/openclaw-oneclick/published/my-idea.html"

## Script
```bash
python3 ~/openclaw/workspace/skills/publish-note/scripts/publish_note.py <note_path>
```
