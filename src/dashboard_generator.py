"""
Generate an HTML dashboard showing project status, tasks, and memories.
Ideas are loaded from data/ideas.json and rendered with interactive JavaScript.
"""

import os
import json
from datetime import datetime
from pathlib import Path
from src.memory_manager import read_all_memories, read_category, MEMORIES_DIR

GITHUB_REPO_URL = "https://github.com/NaharPT/claude-memory"
GITHUB_BLOB_URL = "https://github.com/NaharPT/claude-memory/blob/main/"

BASE_DIR = Path(__file__).parent.parent
IDEAS_JSON = BASE_DIR / "data" / "ideas.json"


def extract_tasks(projects_content: str) -> dict:
    """Extract active project tasks, grouped by status. Excludes backlog ideas."""
    tasks = {"done": [], "in_progress": [], "todo": []}
    current_context = ""

    for line in projects_content.split("\n"):
        line = line.strip()
        if line.startswith("*Context:") and line.endswith("*"):
            current_context = line[10:-1]
            continue
        if not line.startswith("- "):
            continue
        if "idea backlog" in current_context.lower():
            continue

        text = line[2:]
        if "DONE" in text.upper():
            tasks["done"].append(text)
        elif "IN PROGRESS" in text.upper() or "IN-PROGRESS" in text.upper():
            tasks["in_progress"].append(text)
        elif "TODO" in text.upper():
            tasks["todo"].append(text)

    return tasks


def extract_bullets(content: str) -> list:
    """Extract bullet points from markdown content."""
    bullets = []
    for line in content.split("\n"):
        line = line.strip()
        if line.startswith("- "):
            bullets.append(line[2:])
    return bullets


def extract_project_entries(content: str) -> list:
    """Extract roadmap items (non-backlog project entries)."""
    items = []
    current_context = ""

    for line in content.split("\n"):
        line = line.strip()
        if line.startswith("*Context:") and line.endswith("*"):
            current_context = line[10:-1]
            continue
        if not line.startswith("- "):
            continue
        if "idea backlog" in current_context.lower():
            continue

        text = line[2:]
        if "DONE" in text.upper():
            status = "done"
        elif "IN PROGRESS" in text.upper() or "IN-PROGRESS" in text.upper():
            status = "progress"
        elif "TODO" in text.upper():
            status = "todo"
        else:
            status = "info"

        items.append({"text": text, "status": status})

    return items


def extract_entries_with_context(content: str) -> list:
    """Extract entries with timestamps and context from memory markdown."""
    entries = []
    current_timestamp = ""
    current_context = ""

    for line in content.split("\n"):
        line = line.strip()
        if line.startswith("### "):
            current_timestamp = line[4:]
        elif line.startswith("*Context:") and line.endswith("*"):
            current_context = line[10:-1]
        elif line.startswith("- "):
            entries.append({
                "timestamp": current_timestamp,
                "context": current_context,
                "text": line[2:]
            })

    return entries


def load_ideas() -> list:
    """Load ideas from ideas.json."""
    if IDEAS_JSON.exists():
        with open(IDEAS_JSON, "r", encoding="utf-8") as f:
            data = json.load(f)
        return data.get("ideas", [])
    return []


def generate_dashboard_html() -> str:
    """Generate a full HTML dashboard with interactive idea management."""
    memories = read_all_memories()

    roadmap_items = extract_project_entries(memories.get("projects", ""))
    decision_entries = extract_entries_with_context(memories.get("decisions", ""))
    tasks = extract_tasks(memories.get("projects", ""))
    ideas = load_ideas()

    all_bullets = sum(len(extract_bullets(v)) for v in memories.values())
    total_tasks = len(tasks["done"]) + len(tasks["in_progress"]) + len(tasks["todo"])
    now = datetime.now().strftime("%Y-%m-%d %H:%M")

    # Embed ideas as JSON for JavaScript
    ideas_json = json.dumps(ideas, ensure_ascii=False)

    # --- Build HTML (f-string for Python vars) ---
    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <meta http-equiv="refresh" content="60">
    <meta name="robots" content="noindex, nofollow, noarchive">
    <title>Claude Memory Dashboard</title>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: #0f1117;
            color: #e4e4e7;
            padding: 24px;
            min-height: 100vh;
        }}
        a {{ color: #8b5cf6; text-decoration: none; }}
        a:hover {{ text-decoration: underline; color: #a78bfa; }}

        .header {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 32px;
            padding-bottom: 16px;
            border-bottom: 1px solid #27272a;
        }}
        .header-left {{
            display: flex;
            align-items: center;
            gap: 16px;
        }}
        .header h1 {{ font-size: 28px; font-weight: 700; }}
        .header h1 a {{
            background: linear-gradient(135deg, #8b5cf6, #06b6d4);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            text-decoration: none;
        }}
        .header h1 a:hover {{ opacity: 0.85; text-decoration: none; }}
        .header .repo-link {{
            color: #52525b; font-size: 13px; padding: 4px 10px;
            border: 1px solid #27272a; border-radius: 6px; transition: all 0.15s;
        }}
        .header .repo-link:hover {{ color: #a1a1aa; border-color: #3f3f46; text-decoration: none; }}
        .header .timestamp {{ color: #71717a; font-size: 14px; }}

        .stats-row {{
            display: grid; grid-template-columns: repeat(4, 1fr);
            gap: 16px; margin-bottom: 32px;
        }}
        .stat-card {{
            background: #18181b; border: 1px solid #27272a;
            border-radius: 12px; padding: 20px; text-align: center;
        }}
        .stat-card .number {{ font-size: 36px; font-weight: 700; margin-bottom: 4px; }}
        .stat-card .label {{
            color: #71717a; font-size: 13px;
            text-transform: uppercase; letter-spacing: 1px;
        }}
        .stat-card.purple .number {{ color: #8b5cf6; }}
        .stat-card.cyan .number {{ color: #06b6d4; }}
        .stat-card.green .number {{ color: #22c55e; }}
        .stat-card.orange .number {{ color: #f97316; }}

        .grid {{
            display: grid; grid-template-columns: 1fr 1fr;
            gap: 24px; margin-bottom: 32px;
        }}
        .card {{
            background: #18181b; border: 1px solid #27272a;
            border-radius: 12px; padding: 24px;
        }}
        .card h2 {{
            font-size: 18px; font-weight: 600; margin-bottom: 16px;
            display: flex; align-items: center; gap: 8px;
        }}
        .card h2 .icon {{
            width: 24px; height: 24px; border-radius: 6px;
            display: inline-flex; align-items: center; justify-content: center;
            font-size: 14px;
        }}
        .card.roadmap h2 .icon {{ background: #1e1b4b; color: #8b5cf6; }}
        .card.backlog h2 .icon {{ background: #042f2e; color: #06b6d4; }}
        .card.activity h2 .icon {{ background: #431407; color: #f97316; }}
        .full-width {{ grid-column: 1 / -1; }}

        /* Kanban */
        .kanban {{
            display: grid; grid-template-columns: 1fr 1fr 1fr;
            gap: 16px; margin-bottom: 32px;
        }}
        .kanban-column {{
            background: #18181b; border: 1px solid #27272a;
            border-radius: 12px; padding: 16px; min-height: 200px;
        }}
        .kanban-column h3 {{
            font-size: 14px; font-weight: 600; text-transform: uppercase;
            letter-spacing: 1px; padding-bottom: 12px; margin-bottom: 12px;
            border-bottom: 2px solid; display: flex; align-items: center; gap: 8px;
        }}
        .kanban-column h3 .count {{
            background: #27272a; padding: 2px 8px; border-radius: 10px; font-size: 12px;
        }}
        .kanban-column.todo h3 {{ border-color: #71717a; color: #a1a1aa; }}
        .kanban-column.progress h3 {{ border-color: #8b5cf6; color: #a78bfa; }}
        .kanban-column.done h3 {{ border-color: #22c55e; color: #4ade80; }}
        .kanban-card {{
            background: #27272a; border: 1px solid #3f3f46; border-radius: 8px;
            padding: 12px; margin-bottom: 8px; font-size: 13px; line-height: 1.5;
            color: #d4d4d8; transition: transform 0.1s, box-shadow 0.1s;
        }}
        .kanban-card:hover {{
            transform: translateY(-1px); box-shadow: 0 4px 12px rgba(0,0,0,0.3);
        }}
        .kanban-column.progress .kanban-card {{ border-left: 3px solid #8b5cf6; }}
        .kanban-column.todo .kanban-card {{ border-left: 3px solid #71717a; }}
        .kanban-column.done .kanban-card {{ border-left: 3px solid #22c55e; opacity: 0.7; }}
        .kanban-empty {{
            color: #52525b; font-size: 13px; font-style: italic;
            padding: 20px 0; text-align: center;
        }}

        /* Roadmap */
        .roadmap-list {{ display: flex; flex-direction: column; gap: 10px; }}
        .roadmap-item {{
            padding: 12px 16px; border-radius: 8px; background: #27272a;
            border-left: 3px solid #3f3f46; font-size: 13px; line-height: 1.5; color: #d4d4d8;
        }}
        .roadmap-item.done {{ border-left-color: #22c55e; opacity: 0.7; }}
        .roadmap-item.progress {{ border-left-color: #8b5cf6; }}
        .roadmap-item.todo {{ border-left-color: #71717a; }}
        .roadmap-item.info {{ border-left-color: #06b6d4; }}
        .status-badge {{
            display: inline-block; padding: 2px 8px; border-radius: 4px;
            font-size: 11px; font-weight: 600; text-transform: uppercase;
            letter-spacing: 0.5px; margin-right: 8px;
        }}
        .roadmap-item.done .status-badge {{ background: #052e16; color: #4ade80; }}
        .roadmap-item.progress .status-badge {{ background: #1e1b4b; color: #a78bfa; }}
        .roadmap-item.todo .status-badge {{ background: #18181b; color: #a1a1aa; border: 1px solid #3f3f46; }}

        /* Idea Backlog (interactive) */
        .backlog-list {{ display: flex; flex-direction: column; gap: 10px; }}
        .backlog-item {{
            padding: 12px 16px; border-radius: 8px; background: #27272a;
            border-left: 3px solid #06b6d4; font-size: 13px; line-height: 1.5; color: #d4d4d8;
        }}
        .idea-header {{
            display: flex; align-items: center; gap: 10px; margin-bottom: 4px;
        }}
        .priority-badge {{
            display: inline-flex; align-items: center; justify-content: center;
            min-width: 32px; padding: 2px 8px; border-radius: 4px;
            font-size: 11px; font-weight: 700; letter-spacing: 0.5px;
            cursor: pointer; transition: all 0.15s; user-select: none;
        }}
        .priority-badge:hover {{ transform: scale(1.1); }}
        .idea-title {{ font-weight: 600; color: #e4e4e7; flex: 1; }}
        .idea-status {{
            font-size: 11px; text-transform: uppercase; letter-spacing: 0.5px;
        }}
        .idea-summary {{ color: #a1a1aa; font-size: 12px; margin-top: 4px; line-height: 1.5; }}
        .idea-folder {{
            margin-top: 6px; font-size: 11px; color: #06b6d4;
            padding: 2px 0;
        }}
        .idea-links {{ margin-top: 8px; }}
        .idea-spec-link {{
            font-size: 12px; color: #8b5cf6; text-decoration: none;
            border-bottom: 1px dashed rgba(139,92,246,0.25);
        }}
        .idea-spec-link:hover {{ color: #a78bfa; text-decoration: none; border-bottom-color: rgba(167,139,250,0.25); }}

        /* Activity Log */
        .timeline {{ display: flex; flex-direction: column; }}
        .timeline-entry {{
            padding: 12px 0; border-bottom: 1px solid #27272a;
            display: grid; grid-template-columns: 150px 1fr;
            gap: 16px; font-size: 13px; align-items: start;
        }}
        .timeline-entry:last-child {{ border-bottom: none; }}
        .timeline-meta {{ display: flex; flex-direction: column; gap: 4px; }}
        .timeline-time {{
            color: #52525b; font-size: 12px;
            font-family: 'Cascadia Code', 'Fira Code', monospace;
        }}
        .context-badge {{
            display: inline-block; padding: 1px 6px; background: #1e1b4b;
            color: #a78bfa; border-radius: 4px; font-size: 11px;
            white-space: nowrap; overflow: hidden; text-overflow: ellipsis; max-width: 140px;
        }}
        .timeline-text {{ color: #d4d4d8; line-height: 1.6; }}

        /* Sync banner */
        .sync-banner {{
            display: none; position: fixed; bottom: 24px; left: 50%;
            transform: translateX(-50%); background: #1e1b4b;
            border: 1px solid #8b5cf6; border-radius: 12px;
            padding: 12px 20px; gap: 12px; align-items: center;
            font-size: 13px; color: #e4e4e7;
            box-shadow: 0 8px 32px rgba(0,0,0,0.4); z-index: 100;
        }}
        .sync-banner code {{
            background: #0f1117; padding: 4px 8px; border-radius: 4px;
            font-family: 'Cascadia Code', monospace; font-size: 12px; color: #a78bfa;
        }}
        .sync-dismiss {{
            background: none; border: 1px solid #3f3f46; color: #a1a1aa;
            border-radius: 6px; padding: 4px 10px; cursor: pointer; font-size: 12px;
        }}
        .sync-dismiss:hover {{ border-color: #8b5cf6; color: #e4e4e7; }}

        .footer {{
            text-align: center; color: #52525b; font-size: 12px;
            margin-top: 32px; padding-top: 16px; border-top: 1px solid #27272a;
        }}
        .footer a {{ color: #71717a; }}
        .footer a:hover {{ color: #a1a1aa; }}
    </style>
</head>
<body>
    <div class="header">
        <div class="header-left">
            <h1><a href="{GITHUB_REPO_URL}">Claude Memory Dashboard</a></h1>
            <a class="repo-link" href="{GITHUB_REPO_URL}" target="_blank">GitHub</a>
        </div>
        <span class="timestamp">Last updated: {now}</span>
    </div>

    <div class="stats-row">
        <div class="stat-card purple">
            <div class="number">{total_tasks}</div>
            <div class="label">Active Phases</div>
        </div>
        <div class="stat-card green">
            <div class="number">{len(tasks['done'])}</div>
            <div class="label">Completed</div>
        </div>
        <div class="stat-card cyan">
            <div class="number">{len(tasks['in_progress'])}</div>
            <div class="label">In Progress</div>
        </div>
        <div class="stat-card orange">
            <div class="number">{len(ideas)}</div>
            <div class="label">Ideas Parked</div>
        </div>
    </div>

    <div class="kanban">
        <div class="kanban-column todo">
            <h3>To Do <span class="count">{len(tasks['todo'])}</span></h3>"""

    # --- Kanban: To Do ---
    for task in tasks["todo"]:
        html += f'\n            <div class="kanban-card">{task}</div>'
    if not tasks["todo"]:
        html += '\n            <div class="kanban-empty">No pending tasks</div>'

    html += """
        </div>
        <div class="kanban-column progress">
            <h3>In Progress <span class="count">{len_progress}</span></h3>"""
    html = html.replace("{len_progress}", str(len(tasks["in_progress"])))

    for task in tasks["in_progress"]:
        html += f'\n            <div class="kanban-card">{task}</div>'
    if not tasks["in_progress"]:
        html += '\n            <div class="kanban-empty">Nothing in progress</div>'

    html += """
        </div>
        <div class="kanban-column done">
            <h3>Done <span class="count">{len_done}</span></h3>"""
    html = html.replace("{len_done}", str(len(tasks["done"])))

    for task in tasks["done"]:
        html += f'\n            <div class="kanban-card">{task}</div>'
    if not tasks["done"]:
        html += '\n            <div class="kanban-empty">Nothing completed yet</div>'

    html += """
        </div>
    </div>

    <div class="grid">
        <div class="card roadmap">
            <h2><span class="icon">R</span> Project Roadmap</h2>
            <div class="roadmap-list">"""

    # --- Roadmap ---
    status_labels = {"done": "Done", "progress": "In Progress", "todo": "To Do"}
    for item in roadmap_items:
        status = item["status"]
        label = status_labels.get(status, "")
        badge = f'<span class="status-badge">{label}</span>' if label else ""
        html += f"""
                <div class="roadmap-item {status}">
                    {badge}{item['text']}
                </div>"""

    if not roadmap_items:
        html += '\n                <div class="kanban-empty">No projects tracked yet.</div>'

    html += """
            </div>
        </div>

        <div class="card backlog">
            <h2><span class="icon">?</span> Idea Backlog</h2>
            <div id="idea-backlog-list" class="backlog-list">
                <div class="kanban-empty">Loading ideas...</div>
            </div>
        </div>

        <div class="card activity full-width">
            <h2><span class="icon">A</span> Activity Log</h2>
            <div class="timeline">"""

    # --- Activity Log ---
    reversed_entries = list(reversed(decision_entries))
    for entry in reversed_entries:
        html += f"""
                <div class="timeline-entry">
                    <div class="timeline-meta">
                        <span class="timeline-time">{entry['timestamp']}</span>
                        <span class="context-badge">{entry['context']}</span>
                    </div>
                    <span class="timeline-text">{entry['text']}</span>
                </div>"""

    if not decision_entries:
        html += '\n                <div class="kanban-empty">No activity recorded yet.</div>'

    html += f"""
            </div>
        </div>
    </div>

    <div id="sync-banner" class="sync-banner">
        Priorities changed.
        Tell Claude: <code>python memory.py idea priority &lt;id&gt; &lt;1-3&gt;</code>
        <button class="sync-dismiss" onclick="this.parentElement.style.display='none'">Dismiss</button>
    </div>

    <div class="footer">
        <a href="{GITHUB_REPO_URL}">Claude Memory System</a> | {all_bullets} memories stored
    </div>
"""

    # --- JavaScript (regular string, no f-string escaping needed) ---
    js = """
    <script>
    const IDEAS_DATA = """ + ideas_json + """;
    const GITHUB_BLOB = '""" + GITHUB_BLOB_URL + """';

    const P_LABELS = {0: '--', 1: 'P1', 2: 'P2', 3: 'P3'};
    const P_STYLES = {
        0: {bg: '#27272a', fg: '#71717a', br: '#3f3f46'},
        1: {bg: '#431407', fg: '#fb923c', br: '#f97316'},
        2: {bg: '#422006', fg: '#fbbf24', br: '#eab308'},
        3: {bg: '#18181b', fg: '#a1a1aa', br: '#3f3f46'},
    };
    const S_COLORS = {active: '#8b5cf6', done: '#22c55e', parked: '#52525b'};

    function loadPriorities() {
        try { return JSON.parse(localStorage.getItem('idea_priorities') || '{}'); }
        catch(e) { return {}; }
    }

    function savePriority(id, p) {
        const saved = loadPriorities();
        saved[id] = p;
        localStorage.setItem('idea_priorities', JSON.stringify(saved));
    }

    function renderIdeas() {
        const el = document.getElementById('idea-backlog-list');
        const saved = loadPriorities();

        const ideas = IDEAS_DATA.map(i => ({
            ...i,
            priority: saved[i.id] !== undefined ? saved[i.id] : i.priority
        }));

        ideas.sort((a, b) => (a.priority || 99) - (b.priority || 99));

        if (!ideas.length) {
            el.innerHTML = '<div class="kanban-empty">No ideas parked yet.</div>';
            return;
        }

        el.innerHTML = ideas.map(idea => {
            const ps = P_STYLES[idea.priority] || P_STYLES[0];
            const pl = P_LABELS[idea.priority] || '--';
            const sc = S_COLORS[idea.status] || S_COLORS.parked;

            let h = '<div class="backlog-item">';
            h += '<div class="idea-header">';
            h += '<span class="priority-badge" data-id="' + idea.id + '" ';
            h += 'style="background:' + ps.bg + ';color:' + ps.fg + ';border:1px solid ' + ps.br + '" ';
            h += 'title="Click to change priority">' + pl + '</span>';
            h += '<span class="idea-title">' + idea.title + '</span>';
            h += '<span class="idea-status" style="color:' + sc + '">' + idea.status + '</span>';
            h += '</div>';
            h += '<div class="idea-summary">' + idea.summary + '</div>';

            if (idea.project_folder) {
                var fname = idea.project_folder.replace(/\\\\/g, '/').split('/').pop();
                h += '<div class="idea-folder">Project: ' + fname + '</div>';
            }

            h += '<div class="idea-links">';
            h += '<a href="' + GITHUB_BLOB + idea.detail_file + '" target="_blank" class="idea-spec-link">View full spec</a>';
            h += '</div>';
            h += '</div>';
            return h;
        }).join('');

        el.querySelectorAll('.priority-badge').forEach(badge => {
            badge.addEventListener('click', function(e) {
                e.stopPropagation();
                var id = this.dataset.id;
                var idea = ideas.find(function(i) { return i.id === id; });
                var np = ((idea.priority || 0) + 1) % 4;
                savePriority(id, np);
                renderIdeas();
                document.getElementById('sync-banner').style.display = 'flex';
            });
        });
    }

    document.addEventListener('DOMContentLoaded', renderIdeas);
    </script>
"""

    html += js
    html += "\n</body>\n</html>"

    return html


def save_dashboard(output_path: str = None):
    """Generate and save the dashboard HTML."""
    if output_path is None:
        output_path = str(Path(__file__).parent.parent / "dashboard.html")

    html = generate_dashboard_html()

    with open(output_path, "w", encoding="utf-8") as f:
        f.write(html)

    return output_path


if __name__ == "__main__":
    path = save_dashboard()
    print(f"Dashboard saved to: {path}")
