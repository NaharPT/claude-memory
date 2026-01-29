"""
Core memory management for Claude persistent memory.

Handles reading, writing, searching, and organizing memories
stored as structured markdown files.
"""

import os
import re
from datetime import datetime
from pathlib import Path
from typing import List, Optional, Dict

# Memory categories and their descriptions
MEMORY_CATEGORIES = {
    "user": "User profile, personal context, communication style",
    "projects": "Active projects, status, key decisions, architecture",
    "preferences": "Technical preferences, tools, languages, coding style",
    "decisions": "Important decisions made and their reasoning",
}

MEMORIES_DIR = Path(__file__).parent.parent / "memories"


def ensure_memories_dir():
    """Ensure the memories directory exists."""
    MEMORIES_DIR.mkdir(parents=True, exist_ok=True)


def get_memory_file(category: str) -> Path:
    """Get the path to a memory category file."""
    return MEMORIES_DIR / f"{category}.md"


def read_category(category: str) -> str:
    """Read all memories from a category."""
    filepath = get_memory_file(category)
    if filepath.exists():
        return filepath.read_text(encoding="utf-8")
    return ""


def read_all_memories() -> Dict[str, str]:
    """Read all memory categories."""
    memories = {}
    for category in MEMORY_CATEGORIES:
        content = read_category(category)
        if content.strip():
            memories[category] = content
    return memories


def add_memory(category: str, memory: str, context: str = "") -> bool:
    """
    Add a new memory entry to a category.

    Args:
        category: Memory category (user, projects, preferences, decisions)
        memory: The memory content to store
        context: Optional context about when/why this was stored

    Returns:
        True if successfully stored
    """
    if category not in MEMORY_CATEGORIES:
        print(f"Invalid category '{category}'.")
        print(f"Valid categories: {', '.join(MEMORY_CATEGORIES.keys())}")
        return False

    ensure_memories_dir()
    filepath = get_memory_file(category)

    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")

    # Build the entry
    entry_lines = [
        f"\n### {timestamp}",
    ]
    if context:
        entry_lines.append(f"*Context: {context}*")
    entry_lines.append(f"- {memory}")
    entry_lines.append("")

    entry = "\n".join(entry_lines)

    # Create file with header if it doesn't exist
    if not filepath.exists():
        header = f"# {category.title()}\n\n"
        header += f"> {MEMORY_CATEGORIES[category]}\n\n"
        header += "---\n"
        filepath.write_text(header + entry, encoding="utf-8")
    else:
        # Append to existing file
        with open(filepath, "a", encoding="utf-8") as f:
            f.write(entry)

    return True


def update_memory(category: str, old_text: str, new_text: str) -> bool:
    """
    Update an existing memory by replacing text.

    Args:
        category: Memory category
        old_text: Text to find
        new_text: Text to replace with

    Returns:
        True if successfully updated
    """
    filepath = get_memory_file(category)
    if not filepath.exists():
        print(f"Category '{category}' has no memories yet.")
        return False

    content = filepath.read_text(encoding="utf-8")
    if old_text not in content:
        print(f"Could not find '{old_text}' in {category} memories.")
        return False

    updated = content.replace(old_text, new_text, 1)
    filepath.write_text(updated, encoding="utf-8")
    return True


def search_memories(query: str) -> List[Dict]:
    """
    Search all memories for a query string.

    Args:
        query: Text to search for (case-insensitive)

    Returns:
        List of matches with category and matching lines
    """
    results = []
    query_lower = query.lower()

    for category in MEMORY_CATEGORIES:
        content = read_category(category)
        if not content:
            continue

        lines = content.split("\n")
        matching_lines = []

        for i, line in enumerate(lines):
            if query_lower in line.lower():
                matching_lines.append(line.strip())

        if matching_lines:
            results.append({
                "category": category,
                "matches": matching_lines,
            })

    return results


def delete_memory(category: str, text_to_remove: str) -> bool:
    """
    Delete a memory entry containing specific text.

    Args:
        category: Memory category
        text_to_remove: Text that identifies the entry to remove

    Returns:
        True if successfully deleted
    """
    filepath = get_memory_file(category)
    if not filepath.exists():
        return False

    content = filepath.read_text(encoding="utf-8")
    lines = content.split("\n")
    new_lines = []
    skip_until_next_entry = False

    for line in lines:
        if text_to_remove in line:
            # Remove this line and preceding timestamp if applicable
            if new_lines and new_lines[-1].startswith("### "):
                new_lines.pop()  # Remove timestamp
            if new_lines and new_lines[-1].startswith("*Context:"):
                new_lines.pop()  # Remove context
            skip_until_next_entry = True
            continue

        if skip_until_next_entry and (line.startswith("### ") or line.startswith("---")):
            skip_until_next_entry = False

        if not skip_until_next_entry:
            new_lines.append(line)

    filepath.write_text("\n".join(new_lines), encoding="utf-8")
    return True


def generate_context_summary() -> str:
    """
    Generate a compact context summary for loading into a Claude session.
    This is what gets included in other projects' CLAUDE.md files.
    """
    memories = read_all_memories()

    if not memories:
        return "No memories stored yet."

    summary_parts = ["# Claude Memory Context\n"]
    summary_parts.append(f"*Last loaded: {datetime.now().strftime('%Y-%m-%d %H:%M')}*\n")

    for category, content in memories.items():
        # Extract just the bullet points (skip headers and timestamps)
        lines = content.split("\n")
        bullets = [line for line in lines if line.strip().startswith("- ")]

        if bullets:
            summary_parts.append(f"## {category.title()}")
            for bullet in bullets:
                summary_parts.append(bullet)
            summary_parts.append("")

    return "\n".join(summary_parts)


def list_categories() -> Dict[str, int]:
    """List all categories with memory counts."""
    result = {}
    for category, description in MEMORY_CATEGORIES.items():
        content = read_category(category)
        count = content.count("\n- ") if content else 0
        result[category] = count
    return result
