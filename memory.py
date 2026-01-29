"""
Claude Memory CLI - Persistent memory management for Claude Code sessions.

Usage:
    python memory.py add <category> <memory> [--context <context>]
    python memory.py show [category]
    python memory.py search <query>
    python memory.py summary
    python memory.py categories
    python memory.py delete <category> <text>
    python memory.py install <project_path>

Examples:
    python memory.py add user "Nuno does not code, prefers simple solutions"
    python memory.py add projects "Finance project: importing GoodBudget to Notion"
    python memory.py add preferences "Always use Python unless specified otherwise"
    python memory.py add decisions "Chose safe import speed (0.4 tx/sec) for Notion API"

    python memory.py show                  # Show all memories
    python memory.py show user             # Show user memories only
    python memory.py search "Notion"       # Search across all categories
    python memory.py summary               # Compact summary for session loading
    python memory.py categories            # List categories and counts

    python memory.py install C:\\Users\\nfval\\Projects\\my_project
        # Adds memory loading instructions to a project's CLAUDE.md
"""

import sys
import os

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.memory_manager import (
    add_memory,
    read_category,
    read_all_memories,
    search_memories,
    generate_context_summary,
    list_categories,
    delete_memory,
    MEMORY_CATEGORIES,
)


def cmd_add(args):
    """Add a new memory."""
    if len(args) < 2:
        print("Usage: python memory.py add <category> <memory> [--context <context>]")
        print(f"Categories: {', '.join(MEMORY_CATEGORIES.keys())}")
        return

    category = args[0]
    context = ""

    # Check for --context flag
    if "--context" in args:
        ctx_idx = args.index("--context")
        context = " ".join(args[ctx_idx + 1:])
        memory = " ".join(args[1:ctx_idx])
    else:
        memory = " ".join(args[1:])

    if add_memory(category, memory, context):
        print(f"Memory added to [{category}]: {memory}")
    else:
        print("Failed to add memory.")


def cmd_show(args):
    """Show memories."""
    if args:
        category = args[0]
        content = read_category(category)
        if content:
            print(content)
        else:
            print(f"No memories in category '{category}'.")
    else:
        memories = read_all_memories()
        if memories:
            for category, content in memories.items():
                print(content)
                print()
        else:
            print("No memories stored yet.")
            print(f"Add some with: python memory.py add <category> <memory>")
            print(f"Categories: {', '.join(MEMORY_CATEGORIES.keys())}")


def cmd_search(args):
    """Search memories."""
    if not args:
        print("Usage: python memory.py search <query>")
        return

    query = " ".join(args)
    results = search_memories(query)

    if results:
        print(f"Found matches for '{query}':")
        print()
        for result in results:
            print(f"  [{result['category']}]")
            for match in result["matches"]:
                print(f"    {match}")
            print()
    else:
        print(f"No matches found for '{query}'.")


def cmd_summary(args):
    """Generate context summary."""
    summary = generate_context_summary()
    print(summary)


def cmd_categories(args):
    """List categories with counts."""
    categories = list_categories()
    print("Memory Categories:")
    print("=" * 50)
    for category, count in categories.items():
        desc = MEMORY_CATEGORIES[category]
        print(f"  {category:15} {count:3} memories - {desc}")


def cmd_delete(args):
    """Delete a memory entry."""
    if len(args) < 2:
        print("Usage: python memory.py delete <category> <text_to_find>")
        return

    category = args[0]
    text = " ".join(args[1:])

    if delete_memory(category, text):
        print(f"Deleted memory containing '{text}' from [{category}].")
    else:
        print(f"Could not find memory containing '{text}' in [{category}].")


def cmd_install(args):
    """Install memory loading into another project's CLAUDE.md."""
    if not args:
        print("Usage: python memory.py install <project_path>")
        print("Example: python memory.py install C:\\Users\\nfval\\Projects\\my_project")
        return

    project_path = args[0]
    claude_md_path = os.path.join(project_path, "CLAUDE.md")

    memory_block = """
## Persistent Memory

This project uses Claude Memory for persistent context across sessions.
At the start of each session, read the memory files for context:

**Memory location:** `C:\\Users\\nfval\\Projects\\claude-memory\\memories\\`

**To load context, read these files:**
- `memories/user.md` - User profile and preferences
- `memories/projects.md` - Active projects and status
- `memories/preferences.md` - Technical preferences
- `memories/decisions.md` - Key decisions and reasoning

**Quick load:** Run `python C:\\Users\\nfval\\Projects\\claude-memory\\memory.py summary` for a compact context summary.

**To update memories:** Run `python C:\\Users\\nfval\\Projects\\claude-memory\\memory.py add <category> <memory>`
"""

    if os.path.exists(claude_md_path):
        # Check if already installed
        with open(claude_md_path, "r", encoding="utf-8") as f:
            existing = f.read()

        if "Persistent Memory" in existing:
            print("Memory integration already installed in this project's CLAUDE.md.")
            return

        # Append to existing CLAUDE.md
        with open(claude_md_path, "a", encoding="utf-8") as f:
            f.write("\n---\n")
            f.write(memory_block)

        print(f"Memory integration added to: {claude_md_path}")
    else:
        # Create new CLAUDE.md
        with open(claude_md_path, "w", encoding="utf-8") as f:
            f.write(f"# Project Rules\n\n")
            f.write(memory_block)

        print(f"Created CLAUDE.md with memory integration at: {claude_md_path}")

    print("Claude will now load your memories at the start of each session in this project.")


def cmd_dashboard(args):
    """Generate and open the dashboard."""
    from src.dashboard_generator import save_dashboard

    output = None
    if args:
        output = args[0]

    path = save_dashboard(output)
    print(f"Dashboard saved to: {path}")

    # Try to open in browser
    try:
        import webbrowser
        webbrowser.open(f"file:///{path}")
        print("Opening in browser...")
    except Exception:
        print(f"Open manually: {path}")


def cmd_help(args=None):
    """Show help."""
    print(__doc__)


# Command dispatch
COMMANDS = {
    "add": cmd_add,
    "show": cmd_show,
    "search": cmd_search,
    "summary": cmd_summary,
    "categories": cmd_categories,
    "delete": cmd_delete,
    "install": cmd_install,
    "dashboard": cmd_dashboard,
    "help": cmd_help,
}


def main():
    if len(sys.argv) < 2:
        cmd_help()
        return

    command = sys.argv[1]
    args = sys.argv[2:]

    if command in COMMANDS:
        COMMANDS[command](args)
    else:
        print(f"Unknown command: {command}")
        print(f"Available commands: {', '.join(COMMANDS.keys())}")


if __name__ == "__main__":
    main()
