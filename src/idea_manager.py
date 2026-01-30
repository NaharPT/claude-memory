"""
Manage ideas with detailed specs, priorities, and project folder associations.
Ideas are stored as:
  - data/ideas.json: metadata index (priority, project folder, status)
  - memories/ideas/<slug>.md: detailed spec per idea
"""

import os
import json
import re
from datetime import datetime
from pathlib import Path

BASE_DIR = Path(__file__).parent.parent
IDEAS_JSON = BASE_DIR / "data" / "ideas.json"
IDEAS_DIR = BASE_DIR / "memories" / "ideas"


def _ensure_dirs():
    """Ensure data/ and memories/ideas/ directories exist."""
    IDEAS_JSON.parent.mkdir(parents=True, exist_ok=True)
    IDEAS_DIR.mkdir(parents=True, exist_ok=True)


def _load_ideas() -> dict:
    """Load ideas index from JSON."""
    if IDEAS_JSON.exists():
        with open(IDEAS_JSON, "r", encoding="utf-8") as f:
            return json.load(f)
    return {"ideas": []}


def _save_ideas(data: dict):
    """Save ideas index to JSON and regenerate dashboard."""
    _ensure_dirs()
    with open(IDEAS_JSON, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    _regenerate_dashboard()


def _regenerate_dashboard():
    """Auto-regenerate the dashboard after idea changes."""
    try:
        from src.dashboard_generator import save_dashboard
        path = save_dashboard()
        print(f"Dashboard regenerated: {path}")
    except Exception as e:
        print(f"Warning: dashboard regeneration failed: {e}")


def _slugify(title: str) -> str:
    """Convert title to a URL-friendly slug."""
    slug = title.lower().strip()
    slug = re.sub(r'[^a-z0-9\s-]', '', slug)
    slug = re.sub(r'[\s]+', '-', slug)
    slug = re.sub(r'-+', '-', slug)
    return slug.strip('-')


def add_idea(title: str, summary: str, project_folder: str = None) -> dict:
    """Add a new idea to the index and create a stub detail file."""
    _ensure_dirs()
    data = _load_ideas()

    idea_id = _slugify(title)

    # Check for duplicates
    for idea in data["ideas"]:
        if idea["id"] == idea_id:
            print(f"Idea '{idea_id}' already exists.")
            return None

    detail_file = f"memories/ideas/{idea_id}.md"
    detail_path = BASE_DIR / detail_file

    idea = {
        "id": idea_id,
        "title": title,
        "summary": summary,
        "priority": 0,
        "project_folder": project_folder,
        "detail_file": detail_file,
        "created": datetime.now().strftime("%Y-%m-%d"),
        "status": "parked",
    }

    data["ideas"].append(idea)
    _save_ideas(data)

    # Create stub detail file if it doesn't exist
    if not detail_path.exists():
        stub = f"""# {title}

> {summary}

## Overview

(Add detailed description here)

---

## Implementation Notes

(Add technical details, architecture, dependencies here)

---

## Notes

- Created: {idea['created']}
- Status: Parked
"""
        with open(detail_path, "w", encoding="utf-8") as f:
            f.write(stub)

    return idea


def set_priority(idea_id: str, priority: int) -> bool:
    """Set priority for an idea. 0=unset, 1=high, 2=medium, 3=low."""
    if priority not in (0, 1, 2, 3):
        print("Priority must be 0 (unset), 1 (high), 2 (medium), or 3 (low).")
        return False

    data = _load_ideas()
    for idea in data["ideas"]:
        if idea["id"] == idea_id:
            idea["priority"] = priority
            _save_ideas(data)
            return True

    print(f"Idea '{idea_id}' not found.")
    return False


def link_project(idea_id: str, project_folder: str) -> bool:
    """Associate a project folder with an idea."""
    data = _load_ideas()
    for idea in data["ideas"]:
        if idea["id"] == idea_id:
            idea["project_folder"] = project_folder
            _save_ideas(data)
            return True

    print(f"Idea '{idea_id}' not found.")
    return False


def set_status(idea_id: str, status: str) -> bool:
    """Set status for an idea. Options: parked, active, done."""
    if status not in ("parked", "active", "done"):
        print("Status must be: parked, active, or done.")
        return False

    data = _load_ideas()
    for idea in data["ideas"]:
        if idea["id"] == idea_id:
            idea["status"] = status
            _save_ideas(data)
            return True

    print(f"Idea '{idea_id}' not found.")
    return False


def list_ideas() -> list:
    """List all ideas sorted by priority (highest first)."""
    data = _load_ideas()
    # Sort: priority 1 first, then 2, then 3, then 0 (unset) last
    def sort_key(idea):
        p = idea["priority"]
        return p if p > 0 else 99
    return sorted(data["ideas"], key=sort_key)


def get_idea(idea_id: str) -> dict:
    """Get a single idea by ID."""
    data = _load_ideas()
    for idea in data["ideas"]:
        if idea["id"] == idea_id:
            return idea
    return None


def get_idea_detail(idea_id: str) -> str:
    """Read the detail markdown file for an idea."""
    idea = get_idea(idea_id)
    if not idea:
        return None

    detail_path = BASE_DIR / idea["detail_file"]
    if detail_path.exists():
        with open(detail_path, "r", encoding="utf-8") as f:
            return f.read()
    return None


def update_from_json(json_str: str) -> bool:
    """Update ideas.json from a JSON string (for dashboard sync)."""
    try:
        new_data = json.loads(json_str)
        if "ideas" not in new_data:
            print("Invalid format: missing 'ideas' key.")
            return False
        _save_ideas(new_data)
        return True
    except json.JSONDecodeError as e:
        print(f"Invalid JSON: {e}")
        return False
