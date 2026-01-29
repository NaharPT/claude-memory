# Claude Memory System

## Project Purpose
This is a persistent memory system for Claude Code sessions. It stores structured memories (facts, preferences, decisions, project context) in markdown files that any Claude session can load.

## How It Works
- Memories are stored as markdown files in the `memories/` folder
- Each file is a category (user, projects, preferences, decisions)
- The CLI tool (`memory.py`) manages adding, querying, and updating memories
- Other projects reference this system via their own CLAUDE.md

## Rules
- Keep memories concise and factual
- Use timestamps for time-sensitive information
- Never store secrets (API keys, passwords) in memories
- Prefer updating existing memories over creating duplicates

## Structure
```
claude-memory/
  memories/
    user.md          # User profile, preferences, personal context
    projects.md      # Active projects, status, key decisions
    preferences.md   # Technical preferences, tools, languages
    decisions.md     # Important decisions and their reasoning
  src/
    memory_manager.py  # Core memory management logic
  memory.py          # CLI entry point
  CLAUDE.md          # This file
```
