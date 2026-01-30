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


def _auto_regenerate_dashboard():
    """Auto-regenerate dashboard after data changes."""
    try:
        from src.dashboard_generator import save_dashboard
        save_dashboard()
    except Exception:
        pass  # Non-critical, don't break the command


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
        _auto_regenerate_dashboard()
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
        _auto_regenerate_dashboard()
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
    """Generate dashboard and optionally publish to GitHub Pages."""
    from src.dashboard_generator import save_dashboard
    import shutil
    import subprocess

    # Generate dashboard
    memory_dir = os.path.dirname(os.path.abspath(__file__))
    dashboard_path = save_dashboard(os.path.join(memory_dir, "dashboard.html"))

    # Also save as index.html for GitHub Pages
    index_path = os.path.join(memory_dir, "index.html")
    shutil.copy2(dashboard_path, index_path)

    print(f"Dashboard saved to: {dashboard_path}")

    # Push to GitHub if --publish flag or repo exists
    publish = "--publish" in args or "--push" in args

    # Auto-detect if git repo exists
    git_dir = os.path.join(memory_dir, ".git")
    if os.path.isdir(git_dir):
        try:
            subprocess.run(
                ["git", "add", "dashboard.html", "index.html", "memories/", "data/"],
                cwd=memory_dir, capture_output=True
            )
            subprocess.run(
                ["git", "commit", "-m", f"Dashboard update {__import__('datetime').datetime.now().strftime('%Y-%m-%d %H:%M')}"],
                cwd=memory_dir, capture_output=True
            )
            result = subprocess.run(
                ["git", "push"],
                cwd=memory_dir, capture_output=True, text=True
            )
            if result.returncode == 0:
                print("Published to: https://naharpt.github.io/claude-memory/")
            else:
                print(f"Git push note: {result.stderr.strip()[:100]}")
        except Exception as e:
            print(f"Could not publish: {e}")
    else:
        print("No git repo found. Run 'git init' to enable publishing.")


def cmd_idea(args):
    """Manage ideas with detailed specs and priorities."""
    from src.idea_manager import (
        add_idea, set_priority, link_project, set_status,
        list_ideas, get_idea, get_idea_detail,
    )

    if not args:
        print("Usage: python memory.py idea <subcommand> [args]")
        print("Subcommands: add, list, priority, link, status, show")
        return

    sub = args[0]
    sub_args = args[1:]

    if sub == "add":
        if len(sub_args) < 2:
            print('Usage: python memory.py idea add "Title" "Summary description"')
            return
        title = sub_args[0]
        summary = " ".join(sub_args[1:])
        idea = add_idea(title, summary)
        if idea:
            print(f"Idea added: {idea['id']}")
            print(f"  Title: {idea['title']}")
            print(f"  Detail file: {idea['detail_file']}")

    elif sub == "list":
        ideas = list_ideas()
        if not ideas:
            print("No ideas tracked yet. Add one with: python memory.py idea add <title> <summary>")
            return
        priority_labels = {0: "---", 1: "P1 ", 2: "P2 ", 3: "P3 "}
        print(f"{'Pri':4} {'ID':25} {'Status':8} {'Title'}")
        print("-" * 70)
        for idea in ideas:
            p = priority_labels.get(idea["priority"], "---")
            folder = f" [{idea['project_folder']}]" if idea.get("project_folder") else ""
            print(f"{p:4} {idea['id']:25} {idea['status']:8} {idea['title']}{folder}")

    elif sub == "priority":
        if len(sub_args) < 2:
            print("Usage: python memory.py idea priority <id> <0-3>")
            print("  0=unset, 1=high, 2=medium, 3=low")
            return
        idea_id = sub_args[0]
        priority = int(sub_args[1])
        if set_priority(idea_id, priority):
            labels = {0: "unset", 1: "HIGH", 2: "MEDIUM", 3: "LOW"}
            print(f"Priority set: {idea_id} -> {labels.get(priority, priority)}")

    elif sub == "link":
        if len(sub_args) < 2:
            print("Usage: python memory.py idea link <id> <project_folder_path>")
            return
        idea_id = sub_args[0]
        folder = " ".join(sub_args[1:])
        if link_project(idea_id, folder):
            print(f"Linked: {idea_id} -> {folder}")

    elif sub == "status":
        if len(sub_args) < 2:
            print("Usage: python memory.py idea status <id> <parked|active|done>")
            return
        idea_id = sub_args[0]
        status = sub_args[1]
        if set_status(idea_id, status):
            print(f"Status set: {idea_id} -> {status}")

    elif sub == "show":
        if not sub_args:
            print("Usage: python memory.py idea show <id>")
            return
        idea_id = sub_args[0]
        idea = get_idea(idea_id)
        if not idea:
            print(f"Idea '{idea_id}' not found.")
            return
        priority_labels = {0: "Unset", 1: "HIGH", 2: "MEDIUM", 3: "LOW"}
        print(f"Title:    {idea['title']}")
        print(f"ID:       {idea['id']}")
        print(f"Priority: {priority_labels.get(idea['priority'], '?')}")
        print(f"Status:   {idea['status']}")
        print(f"Created:  {idea['created']}")
        print(f"Folder:   {idea.get('project_folder') or 'Not linked'}")
        print(f"Detail:   {idea['detail_file']}")
        print()
        detail = get_idea_detail(idea_id)
        if detail:
            print(detail)

    else:
        print(f"Unknown idea subcommand: {sub}")
        print("Available: add, list, priority, link, status, show")


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
    "idea": cmd_idea,
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
