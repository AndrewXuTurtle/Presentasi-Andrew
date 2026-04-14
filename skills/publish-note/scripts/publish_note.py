#!/usr/bin/env python3
"""Publish a note as a standalone HTML page to GitHub Pages."""
import sys, os, re, subprocess, hashlib
from pathlib import Path
from datetime import datetime

WORKSPACE = os.path.expanduser("~/.openclaw/workspace")
NOTEBOOKS_DIR = os.path.join(WORKSPACE, "published")
GITHUB_REPO = "https://github.com/AndrewXuTurtle/openclaw-oneclick.git"
GITHUB_PAGES = "https://andrewxuturtle.github.io/openclaw-oneclick/published"

HTML_TEMPLATE = """<!DOCTYPE html>
<html lang="id">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{title}</title>
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=JetBrains+Mono:wght@400;500&display=swap" rel="stylesheet">
<style>
  :root {{ --bg:#0a0e1a; --surface:#111827; --primary:#00f0ff; --text:#e2e8f0; --text-dim:#94a3b8; --border:#1e293b; }}
  * {{ margin:0; padding:0; box-sizing:border-box; }}
  body {{ background:var(--bg); color:var(--text); font-family:'Inter',sans-serif; line-height:1.7; padding:60px 40px; }}
  .container {{ max-width:800px; margin:0 auto; }}
  h1 {{ font-family:'JetBrains Mono',monospace; font-size:2.2rem; color:var(--primary); margin-bottom:8px; }}
  .meta {{ font-size:13px; color:var(--text-dim); margin-bottom:32px; }}
  h2 {{ font-size:1.3rem; color:#fff; margin:28px 0 12px; border-bottom:1px solid var(--border); padding-bottom:6px; }}
  h3 {{ font-size:1.1rem; color:var(--primary); margin:20px 0 8px; }}
  p {{ margin:10px 0; color:var(--text); }}
  code {{ background:var(--surface); padding:2px 8px; border-radius:4px; font-family:'JetBrains Mono',monospace; font-size:14px; color:var(--primary); }}
  pre {{ background:var(--surface); border:1px solid var(--border); border-radius:8px; padding:16px; overflow-x:auto; margin:16px 0; }}
  pre code {{ background:none; padding:0; }}
  ul,ol {{ padding-left:24px; color:var(--text); }}
  li {{ margin:6px 0; }}
  a {{ color:var(--primary); text-decoration:none; }}
  a:hover {{ text-decoration:underline; }}
  blockquote {{ border-left:3px solid var(--primary); padding:8px 16px; background:var(--surface); margin:16px 0; color:var(--text-dim); font-style:italic; }}
  table {{ width:100%; border-collapse:collapse; margin:16px 0; }}
  th {{ background:var(--surface); color:var(--primary); padding:10px 14px; text-align:left; border-bottom:2px solid var(--border); font-family:'JetBrains Mono',monospace; font-size:12px; }}
  td {{ padding:10px 14px; border-bottom:1px solid var(--border); color:var(--text); }}
  tr:hover td {{ background:var(--surface); }}
  .footer {{ margin-top:60px; padding-top:20px; border-top:1px solid var(--border); font-size:12px; color:var(--text-dim); text-align:center; }}
</style>
</head>
<body>
<div class="container">
  <h1>{title}</h1>
  <div class="meta">Published {date} · Smart Tourism Workspace</div>
  {content}
  <div class="footer">
    <a href="https://andrewxuturtle.github.io/openclaw-oneclick/">← Back to OpenClaw Workspace</a>
  </div>
</div>
</body>
</html>"""

def md_to_html(text):
    """Very lightweight markdown-to-HTML converter."""
    lines = text.split("\n")
    in_code = False
    in_list = False
    html_lines = []
    in_table = False

    for line in lines:
        # Code blocks
        if line.strip().startswith("```"):
            if not in_code:
                lang = line.strip()[3:]
                html_lines.append(f'<pre><code class="language-{lang}">')
                in_code = True
            else:
                html_lines.append("</code></pre>")
                in_code = False
            continue
        if in_code:
            html_lines.append(line.replace("&","&amp;").replace("<","&lt;").replace(">","&gt;"))
            continue

        # Headers
        if line.startswith("#### "):
            html_lines.append(f"<h4>{line[5:]}</h4>")
        elif line.startswith("### "):
            html_lines.append(f"<h3>{line[4:]}</h3>")
        elif line.startswith("## "):
            html_lines.append(f"<h2>{line[3:]}</h2>")
        elif line.startswith("# "):
            html_lines.append(f"<h1>{line[2:]}</h1>")
        elif line.startswith("| "):
            # Table — collect rows
            cells = [c.strip() for c in line.split("|")[1:-1]]
            if "---" in line:
                continue  # separator
            tag = "th" if not in_table else "td"
            in_table = True
            html_lines.append("<tr>" + "".join(f"<{tag}>{c}</{tag}>" for c in cells) + "</tr>")
        else:
            if in_table:
                html_lines.append("</table>")
                in_table = False
            # Inline formatting
            line = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', line)
            line = re.sub(r'\*(.+?)\*', r'<em>\1</em>', line)
            line = re.sub(r'`(.+?)`', r'<code>\1</code>', line)
            line = re.sub(r'\[(.+?)\]\((.+?)\)', r'<a href="\2">\1</a>', line)
            if line.strip():
                html_lines.append(f"<p>{line}</p>")

    if in_table:
        html_lines.append("</table>")

    return "\n".join(html_lines)

def slugify(name):
    """Create a safe filename slug."""
    name = re.sub(r'[^\w\s-]', '', name)
    return re.sub(r'[-\s]+', '-', name).strip('-')

def main(note_path):
    note_path = os.path.expanduser(note_path)
    if not os.path.exists(note_path):
        print(f"ERROR: File not found: {note_path}")
        sys.exit(1)

    with open(note_path) as f:
        content = f.read()

    # Extract title from first # heading or filename
    title_match = re.search(r'^# (.+)$', content, re.MULTILINE)
    if title_match:
        title = title_match.group(1)
    else:
        title = os.path.splitext(os.path.basename(note_path))[0]

    # Slug for filename
    slug = slugify(title)
    date_str = datetime.now().strftime("%Y-%m-%d")

    # Build HTML
    body_html = md_to_html(content)
    html = HTML_TEMPLATE.format(title=title, date=date_str, content=body_html)

    # Save locally
    os.makedirs(NOTEBOOKS_DIR, exist_ok=True)
    outfile = os.path.join(NOTEBOOKS_DIR, f"{slug}.html")
    with open(outfile, "w") as f:
        f.write(html)
    print(f"Local: {outfile}")

    # Push to GitHub
    repo_dir = os.path.join(WORKSPACE, ".publish-git")
    if not os.path.exists(os.path.join(repo_dir, ".git")):
        subprocess.run(["git", "clone", "-b", "published",
                       "--single-branch", GITHUB_REPO, repo_dir],
                      capture_output=True, check=False)
        # If published branch doesn't exist, clone main and make new branch
        if not os.path.exists(os.path.join(repo_dir, ".git")):
            subprocess.run(["git", "clone", GITHUB_REPO, repo_dir], capture_output=True)
            subprocess.run(["git", "-C", repo_dir, "checkout", "-b", "published"],
                           capture_output=True)

    # Copy HTML
    pub_dir = os.path.join(repo_dir, "published")
    os.makedirs(pub_dir, exist_ok=True)
    shutil.copy(outfile, os.path.join(pub_dir, f"{slug}.html"))

    subprocess.run(["git", "-C", repo_dir, "add", "."], capture_output=True)
    subprocess.run(["git", "-C", repo_dir, "commit", "-m", f"Publish: {title}"], capture_output=True)
    subprocess.run(["git", "-C", repo_dir, "push", "-u", "origin", "published"], capture_output=True)

    url = f"{GITHUB_PAGES}/{slug}.html"
    print(f"\n✅ Published! 🔗 {url}")
    return url

if __name__ == "__main__":
    import shutil
    if len(sys.argv) < 2:
        print("Usage: publish_note.py <note.md>")
        sys.exit(1)
    main(sys.argv[1])
