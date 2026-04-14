# Linked References Skill

## When to Use
Trigger when Andrew asks about a person, project, or concept — or proactively when starting work on something mentioned in recent sessions.

## Trigger Phrases
- "who mentioned [name]"
- "find all references to [topic]"
- "where have I talked about [X]"
- "linked [name/topic]"
- "backlinks for [X]"
- "what notes mention this"

## What It Does
Searches all memory files for references to a name/person/project/topic and surfaces all mentions with context.

## Usage
```
/linked Anjaly
/linked Barelang
/linked Smart Tourism
/linked keputusan
```

## Output Format
Shows each match with:
- File + date
- The sentence/paragraph containing the mention
- Count of total references

## Script
```bash
python3 ~/openclaw/workspace/skills/linked-refs/scripts/linked_refs.py <search_term>
```
