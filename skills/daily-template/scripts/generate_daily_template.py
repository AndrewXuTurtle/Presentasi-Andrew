#!/usr/bin/env python3
"""Generate today's daily memory note from template."""
import os
from datetime import datetime

MEMORY_DIR = os.path.expanduser("~/.openclaw/workspace/memory")
TEMPLATE = """# 📅 {date} — Daily Log

## 🌤️ Context
- **Day**: {day}, Week {week} of {year}
- **Location**: Jakarta
- **Energy Level**: 🟡 (pick one: 🔴 Low / 🟡 Medium / 🟢 High)
- **Priority Today**: (1-3 bullet max)

## 📋 Pending Carryovers
<!-- What was left unfinished yesterday -->
-

## 🎯 Today's Agenda
- [ ]

## 📝 Session Notes
<!-- Raw notes during the day -->

## 💡 Decisions Made
<!-- Important choices and why -->

## 🔗 People Mentioned
<!-- @name — context -->

## 📌 Tasks Done
- [ ]

## ⚠️ Loose Ends
<!-- Things to follow up, open threads -->

## 📊 End-of-Day Review
- **What went well**:
- **What to improve**:
- **Tomorrow's first action**:
"""

def get_week(date):
    return date.isocalendar()[1]

def day_name(date):
    return date.strftime("%A")

now = datetime.now()
filename = os.path.join(MEMORY_DIR, f"{now.strftime('%Y-%m-%d')}.md")

os.makedirs(MEMORY_DIR, exist_ok=True)

if os.path.exists(filename):
    print(f"ALREADY EXISTS: {filename}")
else:
    content = TEMPLATE.format(
        date=now.strftime("%Y-%m-%d"),
        day=day_name(now),
        week=get_week(now),
        year=now.year
    )
    with open(filename, "w") as f:
        f.write(content)
    print(f"CREATED: {filename}")

# Also copy to today's memory dir at workspace level
WORKSPACE_MEM = os.path.expanduser("~/.openclaw/workspace/memory")
os.makedirs(WORKSPACE_MEM, exist_ok=True)
ws_file = os.path.join(WORKSPACE_MEM, f"{now.strftime('%Y-%m-%d')}.md")
if not os.path.exists(ws_file):
    with open(ws_file, "w") as f:
        f.write(content)
    print(f"CREATED WORKSPACE: {ws_file}")
