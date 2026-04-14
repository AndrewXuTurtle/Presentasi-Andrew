#!/usr/bin/env python3
"""Search all memory/notes files for references to a term."""
import sys, os, glob
from pathlib import Path

MEMORY_DIRS = [
    os.path.expanduser("~/.openclaw/workspace/memory"),
    os.path.expanduser("~/.openclaw/workspace/notes"),
]

def search_files(term, max_results=20):
    term_lower = term.lower()
    results = []
    for mem_dir in MEMORY_DIRS:
        if not os.path.exists(mem_dir):
            continue
        for filepath in glob.glob(os.path.join(mem_dir, "**/*.md"), recursive=True):
            # Skip subdirs like dreaming, backups
            if "/dreaming/" in filepath or "/backup" in filepath:
                continue
            try:
                with open(filepath) as f:
                    content = f.read()
                    # Simple case-insensitive search
                    lines = content.split("\n")
                    for i, line in enumerate(lines):
                        if term_lower in line.lower():
                            # Get surrounding context (2 lines before/after)
                            start = max(0, i-2)
                            end = min(len(lines), i+3)
                            context = "\n".join(f"| {l}" for l in lines[start:end])
                            relpath = os.path.relpath(filepath)
                            results.append({
                                "file": relpath,
                                "line_num": i+1,
                                "context": context
                            })
            except Exception:
                pass
    return results[:max_results]

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: linked_refs.py <search_term>")
        sys.exit(1)
    term = " ".join(sys.argv[1:])
    results = search_files(term)
    if not results:
        print(f"No references found for: {term}")
    else:
        print(f"🔍 Found {len(results)} reference(s) for: {term}\n")
        current_file = None
        for r in results:
            if r["file"] != current_file:
                print(f"\n📄 {r['file']}")
                current_file = r["file"]
            print(r["context"])
