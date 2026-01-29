# Dashboard Overhaul

> Significantly improve the Claude Memory Dashboard in terms of visibility, usefulness, and interactivity

## Overview

The current dashboard (GitHub Pages) provides a basic kanban board, project roadmap, idea backlog, and activity log. This idea is about taking it to the next level - making it a genuinely useful daily command center rather than a static status page.

---

## Improvement Areas

### 1. Real-Time Project Health

- **Build status indicators**: Show last-run status for each project (pass/fail/stale)
- **Activity heatmap**: Git commit frequency per project (like GitHub's contribution graph but for your projects)
- **Stale project alerts**: Highlight projects with no activity in 7+ days
- **Progress bars**: Visual completion percentage based on TODO items in each project

### 2. Cross-Project Insights

- **Dependency graph**: Visual map of how projects relate (e.g., memory system used by all others)
- **Shared resources**: Track API keys, services, and infrastructure used across projects
- **Timeline view**: Gantt-style view showing project phases and overlaps
- **Effort distribution**: Where time is being spent (based on commit/session frequency)

### 3. Interactive Features

- **Quick actions**: One-click buttons to open project in VS Code, view latest report, open terminal
- **Drag-and-drop kanban**: Move tasks between columns directly on the dashboard
- **Inline notes**: Click to add quick notes to any project or idea without CLI
- **Search/filter**: Filter findings by project, status, priority, date range
- **Dark mode toggle**: Respect system preference + manual override

### 4. Data Visualization

- **Charts**: Use Chart.js or similar for:
  - Decision frequency over time
  - Finding distribution by category (for genome project)
  - Import progress tracking (for finance project)
- **Stats cards**: Key metrics at a glance (total projects, active tasks, decisions this week)
- **Mini-calendars**: Show activity per day in calendar format

### 5. Notification Center

- **Session summaries**: After each Claude Code session, auto-generate a brief summary card
- **Pending actions**: Items requiring user input across all projects
- **Milestones**: Celebrate completed phases/projects

### 6. Mobile-Friendly Design

- **Responsive layout**: Cards stack vertically on mobile
- **Touch-friendly**: Larger tap targets, swipe gestures for kanban
- **PWA support**: Add to home screen as an app-like experience

---

## Technical Approach

### Option A: Enhanced Static HTML (Incremental)
- Keep Python generator + GitHub Pages
- Add Chart.js for visualizations
- Add more JavaScript for interactivity
- Use localStorage for preferences
- Pro: Simple, no infra changes
- Con: Limited real-time capability

### Option B: Lightweight SPA (Next Step)
- Single-page app with vanilla JS or Preact
- Still hosted on GitHub Pages
- Reads data from JSON files in the repo
- Pro: Better UX, smoother interactions
- Con: More complex build

### Option C: Local Dashboard Server (Full Feature)
- Python Flask/FastAPI local server
- WebSocket for real-time updates
- Direct file system access
- Pro: Full feature set, real-time
- Con: Requires running a local server

**Recommended**: Start with Option A (enhance current), migrate to B when complexity warrants it.

---

## Priority Improvements (Quick Wins)

1. **Stats bar at top**: Total projects | Active tasks | Decisions this week | Last session
2. **Color-coded project cards**: Green (active), blue (planned), gray (parked), gold (done)
3. **Session history widget**: Last 5 Claude sessions with brief summary
4. **Better typography**: Improve readability with better font sizes, spacing, hierarchy
5. **Clickable everything**: Every project name, idea, decision should link somewhere useful

---

## Notes

- Captured from session 2026-01-29
- Status: Parked - implement incrementally as the memory system grows
- The dashboard should evolve as more projects and data accumulate
