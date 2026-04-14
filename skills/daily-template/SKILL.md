# Daily Template Skill

## When to Use
Automatically on every new daily note creation. Also trigger by: "new daily note", "create today log", "start session log".

## Trigger Phrases
- "new daily note"
- "create today log"
- "start session log"
- "daily log"

## What It Does
Creates today's daily memory note from a structured template. Place in `memory/YYYY-MM-DD.md`.

## Template Fields
```markdown
# 📅 YYYY-MM-DD — Daily Log

## 🌤️ Context
- **Day**: Monday, Week W of YYYY
- **Location**: Jakarta
- **Weather**: (fill in)
- **Energy Level**: 🔴🟡🟢 (pick one)
- **Priority Today**: (1-3 bullet max)

## 📋 Pending Carryovers
<!-- What was left unfinished yesterday -->
- (from yesterday:)

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
```

## Script
```bash
python3 ~/openclaw/workspace/skills/daily-template/scripts/generate_daily_template.py
```
