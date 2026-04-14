#!/usr/bin/env python3
"""Refactor memory notes into atomic units — one idea per note, linked."""
import os, re, shutil
from pathlib import Path
from datetime import datetime

WORKSPACE = os.path.expanduser("~/.openclaw/workspace")
MEMORY_DIR = os.path.join(WORKSPACE, "memory")
ARCHIVE_DIR = os.path.join(MEMORY_DIR, "archive")
ATOMIC_DIR = os.path.join(WORKSPACE, "atomic")
os.makedirs(ARCHIVE_DIR, exist_ok=True)
os.makedirs(ATOMIC_DIR, exist_ok=True)

MAX_LINES = 20

def extract_concepts(text):
    """Extract key concepts from text to form a title."""
    # Remove markdown syntax
    text = re.sub(r'#{1,6} ', '', text)
    text = re.sub(r'\[([^\]]+)\]\([^\)]+\)', r'\1', text)
    text = re.sub(r'[*_`>-]', '', text)
    # Take first meaningful phrase
    words = text.split()[:6]
    title = " ".join(w for w in words if len(w) > 2).strip()
    return title or "Untitled"

def split_into_atomic_notes(filepath):
    """Split a large note into atomic chunks."""
    with open(filepath) as f:
        content = f.read()

    lines = content.split("\n")
    basename = Path(filepath).stem  # filename without extension

    # If it's short enough, keep as one atomic note
    non_empty = [l for l in lines if l.strip() and not l.strip().startswith("#"))]
    if len(non_empty) <= MAX_LINES:
        return [("single", content, filepath)]

    # Split by major sections (## headers)
    chunks = []
    current_chunk = []
    current_title = basename

    for line in lines:
        if line.startswith("## "):
            if current_chunk:
                chunks.append((current_title, "\n".join(current_chunk)))
            current_title = line[3:].strip()
            current_chunk = [line]
        else:
            current_chunk.append(line)

    if current_chunk:
        chunks.append((current_title, "\n".join(current_chunk)))

    return chunks

def slugify(title):
    title = re.sub(r'[^\w\s-]', '', title)
    title = re.sub(r'[-\s]+', '-', title).strip('-')[:50]
    return title or "note"

def refactor_all(dry_run=False):
    created, archived = 0, 0
    note_map = {}  # slug -> filepath

    for root, dirs, files in os.walk(MEMORY_DIR):
        if "/archive/" in root or "/dreaming/" in root:
            continue
        for fname in files:
            if not fname.endswith(".md"):
                continue
            fpath = os.path.join(root, fname)
            rel = os.path.relpath(fpath, MEMORY_DIR)
            note_map[slugify(Path(fname).stem)] = fpath

            chunks = split_into_atomic_notes(fpath)
            if len(chunks) == 1 and chunks[0][0] == "single":
                continue  # already atomic, skip

            # Archive original
            archive_path = os.path.join(ARCHIVE_DIR, fname)
            shutil.copy2(fpath, archive_path)
            os.remove(fpath)
            archived += 1

            # Write atomic chunks
            for i, (title, body) in enumerate(chunks):
                slug = slugify(title)
                if len(chunks) > 1:
                    slug = f"{slug}-{i+1}"
                outfile = os.path.join(ATOMIC_DIR, f"{slug}.md")

                # Add header with tags and see-also
                tags = "#atomic "
                see_also = ""
                if i > 0:
                    see_also = f"\n\nSee also: [[{slugify(chunks[i-1][0])}]]"
                if i < len(chunks) - 1:
                    see_also += f"\nSee also: [[{slugify(chunks[i+1][0])}]]"

                new_content = f"# {title}\n{tags}\n\n{body}{see_also}\n"
                if dry_run:
                    print(f"[DRY] Would create: {outfile}")
                else:
                    with open(outfile, "w") as f:
                        f.write(new_content)
                    created += 1
                print(f"  → {slug}.md")

    print(f"\n{'[DRY RUN] ' if dry_run else ''}Archived: {archived} | Created: {created}")
    if not dry_run:
        print(f"Archive: {ARCHIVE_DIR}")
        print(f"Atomic notes: {ATOMIC_DIR}")
    return created, archived

if __name__ == "__main__":
    dry = "--dry-run" in sys.argv
    print("🔄 Atomic Notes Refactor")
    print(f"Memory dir: {MEMORY_DIR}")
    print(f"{'[DRY RUN MODE]' if dry else ''}\n")
    refactor_all(dry_run=dry)
