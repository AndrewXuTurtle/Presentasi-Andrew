# Atomic Notes Refactor Skill

## When to Use
Trigger when notes become too bloated or when Andrew says "refactor my notes", "clean up notes", "make notes atomic".

## Trigger Phrases
- "refactor notes"
- "make notes atomic"
- "clean up memory"
- "organize notes"
- "compact notes"

## What It Does
Scans existing `.md` notes and refactors them into atomic units:
- **One idea per note** — no note should be longer than ~20 lines
- **Titled clearly** — filename = atomic topic name
- **Linked** — notes that relate get `[[linked-note-name]]` references
- **Tagged** — each note has top-level `#topic` tags

## Rules for Atomic Notes
1. **F A C T S** — notes = facts, decisions, context — not raw dumps
2. **Named for search** — title should contain the key concept
3. **Max 20 lines** — if longer, split
4. **Link to related** — end each note with `See also: [[related-note]]`
5. **Date-stamped** — each note has date of creation

## Script
```bash
python3 ~/openclaw/workspace/skills/atomic-notes/scripts/refactor_notes.py [--dry-run]
```

## Output
- Refactored notes saved alongside originals (old ones moved to `memory/archive/`)
- Summary of: created, linked, archived counts
- List of orphaned notes (no links → consider deleting or linking)
