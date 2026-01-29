# Decisions

> Important decisions made and their reasoning

---

### 2026-01-29 22:09
*Context: Finance project - critical bug*
- Notion Finance OS: Property names have trailing/leading spaces (Amount_, Category_, _Record Name) - must use exact names in API calls

### 2026-01-29 22:09
*Context: Finance project*
- Notion Finance OS: Expense Status options are Paid/Pending/Scheduled. Income Status options are Received/Pending/Expected

### 2026-01-29 22:09
*Context: Finance project - database IDs*
- Notion Finance OS: 22 databases found in Backend page. Key IDs - Accounts: 2eecc31f-2839-81f0-af05-eaa513611f84, Expenses: 2eecc31f-2839-81a4-940f-df3784949765, Income: 2eecc31f-2839-81d2-8634-e11419f36578, Categories: 2eecc31f-2839-81e7-9cb2-f4320823185b

### 2026-01-29 22:09
*Context: Finance project*
- Chose safe import speed (0.4 tx/sec with 0.1s delay) for Notion API to avoid rate limiting during bulk import

### 2026-01-29 23:01
- Idea logged: Morning Briefs system - daily voice briefing at 08:00 CET via Telegram. Stack: OpenAI TTS (alloy/nova voice), wttr.in weather API, Google Calendar API, Notion API for tasks. Phases: content design, technical setup, cron automation, 2-week testing cycle. Parked for future implementation. Idea backlog - morning briefs

### 2026-01-29 23:29
*Context: Genome Insight - architecture*
- Genome Insight: 3-layer architecture - Hard layer (ClinVar/PharmGKB raw annotations), Interpretation layer (rules-based conservative translation with evidence tiers), LLM narrative layer (optional, off by default, only restructures facts into prose, never invents biology). Facts stay auditable even if narrative gets poetic.
