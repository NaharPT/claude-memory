"""
Generate an HTML dashboard showing project status, tasks, and memories.
"""

import os
from datetime import datetime
from pathlib import Path
from src.memory_manager import read_all_memories, read_category, MEMORIES_DIR


def extract_tasks(projects_content: str) -> dict:
    """Extract tasks from projects memory, grouped by status."""
    tasks = {"done": [], "in_progress": [], "todo": []}

    for line in projects_content.split("\n"):
        line = line.strip()
        if not line.startswith("- "):
            continue

        text = line[2:]  # Remove "- "

        if "DONE" in text.upper():
            tasks["done"].append(text)
        elif "IN PROGRESS" in text.upper() or "IN-PROGRESS" in text.upper():
            tasks["in_progress"].append(text)
        elif "TODO" in text.upper():
            tasks["todo"].append(text)
        else:
            # General project info, not a task
            pass

    return tasks


def extract_bullets(content: str) -> list:
    """Extract bullet points from markdown content."""
    bullets = []
    for line in content.split("\n"):
        line = line.strip()
        if line.startswith("- "):
            bullets.append(line[2:])
    return bullets


def generate_dashboard_html() -> str:
    """Generate a full HTML dashboard."""
    memories = read_all_memories()

    # Extract structured data
    user_bullets = extract_bullets(memories.get("user", ""))
    project_bullets = extract_bullets(memories.get("projects", ""))
    pref_bullets = extract_bullets(memories.get("preferences", ""))
    decision_bullets = extract_bullets(memories.get("decisions", ""))

    tasks = extract_tasks(memories.get("projects", ""))

    # Count stats
    total_memories = len(user_bullets) + len(project_bullets) + len(pref_bullets) + len(decision_bullets)
    total_tasks = len(tasks["done"]) + len(tasks["in_progress"]) + len(tasks["todo"])

    now = datetime.now().strftime("%Y-%m-%d %H:%M")

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <meta http-equiv="refresh" content="60">
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
        .header {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 32px;
            padding-bottom: 16px;
            border-bottom: 1px solid #27272a;
        }}
        .header h1 {{
            font-size: 28px;
            font-weight: 700;
            background: linear-gradient(135deg, #8b5cf6, #06b6d4);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
        }}
        .header .timestamp {{
            color: #71717a;
            font-size: 14px;
        }}
        .stats-row {{
            display: grid;
            grid-template-columns: repeat(4, 1fr);
            gap: 16px;
            margin-bottom: 32px;
        }}
        .stat-card {{
            background: #18181b;
            border: 1px solid #27272a;
            border-radius: 12px;
            padding: 20px;
            text-align: center;
        }}
        .stat-card .number {{
            font-size: 36px;
            font-weight: 700;
            margin-bottom: 4px;
        }}
        .stat-card .label {{
            color: #71717a;
            font-size: 13px;
            text-transform: uppercase;
            letter-spacing: 1px;
        }}
        .stat-card.purple .number {{ color: #8b5cf6; }}
        .stat-card.blue .number {{ color: #06b6d4; }}
        .stat-card.green .number {{ color: #22c55e; }}
        .stat-card.orange .number {{ color: #f97316; }}

        .grid {{
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 24px;
            margin-bottom: 32px;
        }}
        .card {{
            background: #18181b;
            border: 1px solid #27272a;
            border-radius: 12px;
            padding: 24px;
        }}
        .card h2 {{
            font-size: 18px;
            font-weight: 600;
            margin-bottom: 16px;
            display: flex;
            align-items: center;
            gap: 8px;
        }}
        .card h2 .icon {{
            width: 24px;
            height: 24px;
            border-radius: 6px;
            display: inline-flex;
            align-items: center;
            justify-content: center;
            font-size: 14px;
        }}
        .card.tasks h2 .icon {{ background: #1e1b4b; color: #8b5cf6; }}
        .card.user h2 .icon {{ background: #042f2e; color: #06b6d4; }}
        .card.prefs h2 .icon {{ background: #052e16; color: #22c55e; }}
        .card.decisions h2 .icon {{ background: #431407; color: #f97316; }}

        .task-list {{ list-style: none; }}
        .task-list li {{
            padding: 10px 12px;
            border-radius: 8px;
            margin-bottom: 8px;
            font-size: 14px;
            line-height: 1.5;
            display: flex;
            align-items: flex-start;
            gap: 10px;
        }}
        .task-list li .badge {{
            display: inline-block;
            padding: 2px 8px;
            border-radius: 4px;
            font-size: 11px;
            font-weight: 600;
            text-transform: uppercase;
            letter-spacing: 0.5px;
            white-space: nowrap;
            flex-shrink: 0;
        }}
        .task-list li.done {{ background: #052e16; }}
        .task-list li.done .badge {{ background: #22c55e; color: #052e16; }}
        .task-list li.progress {{ background: #1e1b4b; }}
        .task-list li.progress .badge {{ background: #8b5cf6; color: #1e1b4b; }}
        .task-list li.todo {{ background: #27272a; }}
        .task-list li.todo .badge {{ background: #71717a; color: #18181b; }}

        .memory-list {{ list-style: none; }}
        .memory-list li {{
            padding: 8px 0;
            font-size: 14px;
            line-height: 1.5;
            border-bottom: 1px solid #27272a;
            color: #a1a1aa;
        }}
        .memory-list li:last-child {{ border-bottom: none; }}

        .full-width {{
            grid-column: 1 / -1;
        }}

        .footer {{
            text-align: center;
            color: #52525b;
            font-size: 12px;
            margin-top: 32px;
            padding-top: 16px;
            border-top: 1px solid #27272a;
        }}
    </style>
</head>
<body>
    <div class="header">
        <h1>Claude Memory Dashboard</h1>
        <span class="timestamp">Last updated: {now} | Auto-refreshes every 60s</span>
    </div>

    <div class="stats-row">
        <div class="stat-card purple">
            <div class="number">{total_tasks}</div>
            <div class="label">Total Tasks</div>
        </div>
        <div class="stat-card green">
            <div class="number">{len(tasks['done'])}</div>
            <div class="label">Completed</div>
        </div>
        <div class="stat-card blue">
            <div class="number">{len(tasks['in_progress'])}</div>
            <div class="label">In Progress</div>
        </div>
        <div class="stat-card orange">
            <div class="number">{len(tasks['todo'])}</div>
            <div class="label">To Do</div>
        </div>
    </div>

    <div class="grid">
        <div class="card tasks full-width">
            <h2><span class="icon">T</span> Project Tasks</h2>
            <ul class="task-list">"""

    # Add tasks by status
    for task in tasks["in_progress"]:
        html += f'\n                <li class="progress"><span class="badge">In Progress</span> {task}</li>'

    for task in tasks["todo"]:
        html += f'\n                <li class="todo"><span class="badge">To Do</span> {task}</li>'

    for task in tasks["done"]:
        html += f'\n                <li class="done"><span class="badge">Done</span> {task}</li>'

    if not any(tasks.values()):
        html += '\n                <li style="color: #52525b;">No tasks tracked yet. Add project memories with task status (DONE/IN PROGRESS/TODO).</li>'

    html += """
            </ul>
        </div>

        <div class="card user">
            <h2><span class="icon">U</span> User Profile</h2>
            <ul class="memory-list">"""

    for bullet in user_bullets:
        html += f"\n                <li>{bullet}</li>"

    if not user_bullets:
        html += '\n                <li style="color: #52525b;">No user memories yet.</li>'

    html += """
            </ul>
        </div>

        <div class="card prefs">
            <h2><span class="icon">P</span> Preferences</h2>
            <ul class="memory-list">"""

    for bullet in pref_bullets:
        html += f"\n                <li>{bullet}</li>"

    if not pref_bullets:
        html += '\n                <li style="color: #52525b;">No preferences yet.</li>'

    html += """
            </ul>
        </div>

        <div class="card decisions full-width">
            <h2><span class="icon">D</span> Key Decisions</h2>
            <ul class="memory-list">"""

    for bullet in decision_bullets:
        html += f"\n                <li>{bullet}</li>"

    if not decision_bullets:
        html += '\n                <li style="color: #52525b;">No decisions recorded yet.</li>'

    html += f"""
            </ul>
        </div>
    </div>

    <div class="footer">
        Claude Memory System | {total_memories} memories stored | Refresh: python memory.py dashboard
    </div>
</body>
</html>"""

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
