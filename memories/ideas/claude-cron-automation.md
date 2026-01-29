# Claude Cron Automation

> Scheduled autonomous Claude tasks that accumulate data and do background work without user presence

## Overview

Build infrastructure so Claude can run on a schedule (cron / Task Scheduler), executing predefined tasks autonomously. Tasks accumulate results over time, build databases from scratch, and prepare outputs for when the user needs them.

The key insight: most of what Claude does today is reactive (user asks, Claude responds). This flips it - Claude works in the background, and the user consumes the results.

---

## What This Enables

### Immediate Use Cases (Things We Already Need)

1. **ClinVar database builder** - Download and index ClinVar (~90MB) overnight, so genome analysis is instant when user runs it
2. **PharmGKB cache warmer** - Pre-fetch pharmacogenomics data for all priority gene variants, build local cache
3. **Notion finance reconciliation** - Nightly pull from Notion, compare against bank exports, flag discrepancies
4. **Dashboard auto-publish** - After any scheduled task completes, regenerate and push dashboard to GitHub Pages
5. **Morning Briefs delivery** - The 08:00 CET briefing is literally a cron job

### Accumulation Tasks (Build Over Time)

6. **Memory consolidation** - Weekly: review all session memories, merge duplicates, archive stale entries
7. **Project health checks** - Daily: git status of all project folders, flag stale repos, track commit frequency
8. **Data freshness monitor** - Check if cached databases (ClinVar, PharmGKB) are outdated, auto-update monthly
9. **Idea progress tracker** - Weekly scan of active project folders, update idea statuses based on file changes

---

## Architecture

### Option A: Simple Script Runner (MVP)

```
scheduled_tasks/
├── config.yaml          # Task definitions + schedules
├── runner.py            # Main scheduler / task executor
├── tasks/
│   ├── build_clinvar_index.py
│   ├── warm_pharmgkb_cache.py
│   ├── reconcile_finance.py
│   ├── publish_dashboard.py
│   ├── health_check.py
│   └── consolidate_memories.py
├── logs/
│   └── YYYY-MM-DD_taskname.log
└── state/
    └── last_run.json    # Track last execution per task
```

**Runner logic:**
1. Read config.yaml for task definitions
2. Check last_run.json to see what's due
3. Execute due tasks sequentially (or parallel if safe)
4. Log results
5. Update last_run.json
6. Trigger dashboard regeneration if any task modified data

**Scheduling:**
- Windows: Task Scheduler calls `python runner.py` every N hours
- Linux: cron entry
- Fallback: runner.py has its own sleep loop

### Option B: Claude SDK Agent (Advanced)

Use the Claude Agent SDK to create a persistent agent that:
- Runs as a background service
- Has access to all project tools
- Executes scheduled tasks using Claude's reasoning
- Can adapt tasks based on context (skip finance reconciliation on weekends, etc.)
- Reports results via Telegram or dashboard

**Pro:** More intelligent task execution, can handle edge cases
**Con:** Costs API credits per run, more complex setup

### Recommended: Start with Option A, upgrade to B for tasks that benefit from reasoning

---

## Task Configuration Format

```yaml
tasks:
  - id: build_clinvar_index
    script: tasks/build_clinvar_index.py
    schedule: weekly          # daily, weekly, monthly, on_demand
    day: sunday               # for weekly
    time: "03:00"             # CET
    timeout_minutes: 30
    depends_on: []
    notify: false             # send Telegram notification on completion

  - id: publish_dashboard
    script: tasks/publish_dashboard.py
    schedule: after_any       # runs after any other task completes
    timeout_minutes: 2
    depends_on: []
    notify: false

  - id: morning_brief
    script: tasks/morning_brief.py
    schedule: daily
    time: "07:45"             # generate before 08:00 delivery
    days: [mon, tue, wed, thu, fri]
    timeout_minutes: 5
    notify: true              # this IS the notification
```

---

## Database Accumulation Strategy

Some tasks need to build databases from scratch and grow them over time:

### Approach: Incremental + Full Rebuild

- **Incremental:** Each run adds new data since last run (e.g., new PharmGKB lookups)
- **Full rebuild:** Periodic complete refresh (e.g., re-download ClinVar monthly)
- **State tracking:** `state/last_run.json` tracks what was processed
- **Idempotent:** Re-running a task should be safe (upsert, not duplicate)

### Storage

- SQLite for structured accumulated data (lightweight, no server needed)
- JSON files for simple caches (current approach)
- Upgrade path: PostgreSQL if data grows beyond SQLite comfort zone

---

## Implementation Phases

### Phase 1: Runner Infrastructure
- Create `scheduled_tasks/` directory structure
- Implement `runner.py` with config parsing and execution
- Implement `state/last_run.json` tracking
- Set up Windows Task Scheduler entry
- First task: `publish_dashboard.py` (simplest, already works)

### Phase 2: Data Tasks
- `build_clinvar_index.py` - Overnight ClinVar download + index build
- `warm_pharmgkb_cache.py` - Pre-fetch priority variants
- `health_check.py` - Scan all project folders for git status

### Phase 3: Intelligence Tasks
- `consolidate_memories.py` - Memory cleanup and consolidation
- `reconcile_finance.py` - Nightly Notion vs bank comparison
- Morning Briefs integration (when that project starts)

### Phase 4: Monitoring
- Simple web dashboard showing task history (or add to existing dashboard)
- Telegram alerts for failures
- Weekly summary of what ran and what it produced

---

## Dependencies

- Python 3.10+
- PyYAML (config parsing)
- SQLite3 (built-in)
- Windows Task Scheduler or cron
- Existing project tools (clinvar.py, pharmgkb.py, dashboard_generator.py, etc.)

---

## Notes

- Captured from session 2026-01-29
- Status: Parked - implement after genome pipeline MVP is testable
- This is the infrastructure layer that makes all other projects more powerful
- Key principle: tasks must be idempotent and safe to re-run
- All tasks must log clearly and never fail silently
