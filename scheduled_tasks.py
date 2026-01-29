"""
Scheduled tasks manager for Claude Memory system.
Uses Windows Task Scheduler to run automated jobs.

Usage:
    python scheduled_tasks.py setup     # Create all scheduled tasks
    python scheduled_tasks.py list      # List active scheduled tasks
    python scheduled_tasks.py remove    # Remove all scheduled tasks
    python scheduled_tasks.py run       # Run all tasks now (manual trigger)
"""

import sys
import os
import subprocess
from pathlib import Path
from datetime import datetime

MEMORY_DIR = Path(__file__).parent
TASKS_LOG = MEMORY_DIR / "data" / "task_runs.log"

# Task definitions
SCHEDULED_TASKS = [
    {
        "name": "ClaudeMemory_DashboardRefresh",
        "description": "Refresh Claude Memory Dashboard",
        "script": "memory.py dashboard",
        "schedule": "HOURLY",
        "interval": 1,
    },
]


def log_task_run(task_name: str, result: str):
    """Log a task execution."""
    TASKS_LOG.parent.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open(TASKS_LOG, "a", encoding="utf-8") as f:
        f.write(f"{timestamp} | {task_name} | {result}\n")


def setup_tasks():
    """Create Windows Scheduled Tasks."""
    print("Setting up scheduled tasks...")
    print("=" * 60)

    python_path = sys.executable
    working_dir = str(MEMORY_DIR)

    for task in SCHEDULED_TASKS:
        task_name = task["name"]
        script = task["script"]
        schedule = task["schedule"]
        interval = task.get("interval", 1)

        print(f"\nTask: {task_name}")
        print(f"  Description: {task['description']}")
        print(f"  Schedule: Every {interval} {schedule.lower()}")
        print(f"  Command: {python_path} {script}")

        # Build schtasks command
        cmd = [
            "schtasks", "/create",
            "/tn", task_name,
            "/tr", f'"{python_path}" "{working_dir}\\{script}"',
            "/sc", schedule,
            "/f",  # Force overwrite
        ]

        if schedule == "HOURLY":
            pass  # Default is every hour
        elif schedule == "DAILY":
            cmd.extend(["/st", "08:00"])  # Run at 8 AM
        elif schedule == "MINUTE":
            cmd.extend(["/mo", str(interval)])

        try:
            result = subprocess.run(cmd, capture_output=True, text=True, shell=True)
            if result.returncode == 0:
                print(f"  Status: CREATED")
                log_task_run(task_name, "Task created")
            else:
                print(f"  Status: FAILED")
                print(f"  Error: {result.stderr.strip()}")
        except Exception as e:
            print(f"  Status: ERROR - {e}")

    print()
    print("=" * 60)
    print("Scheduled tasks setup complete!")
    print()
    print("To view tasks: schtasks /query /tn ClaudeMemory*")
    print("To remove tasks: python scheduled_tasks.py remove")


def list_tasks():
    """List all Claude Memory scheduled tasks."""
    print("Active Claude Memory scheduled tasks:")
    print("=" * 60)

    try:
        result = subprocess.run(
            ["schtasks", "/query", "/fo", "TABLE", "/nh"],
            capture_output=True, text=True, shell=True
        )

        found = False
        for line in result.stdout.split("\n"):
            if "ClaudeMemory" in line:
                print(f"  {line.strip()}")
                found = True

        if not found:
            print("  No Claude Memory tasks found.")
            print("  Run 'python scheduled_tasks.py setup' to create them.")

    except Exception as e:
        print(f"  Error: {e}")


def remove_tasks():
    """Remove all Claude Memory scheduled tasks."""
    print("Removing scheduled tasks...")

    for task in SCHEDULED_TASKS:
        task_name = task["name"]
        try:
            result = subprocess.run(
                ["schtasks", "/delete", "/tn", task_name, "/f"],
                capture_output=True, text=True, shell=True
            )
            if result.returncode == 0:
                print(f"  Removed: {task_name}")
            else:
                print(f"  Not found: {task_name}")
        except Exception as e:
            print(f"  Error removing {task_name}: {e}")


def run_all():
    """Run all tasks manually."""
    print("Running all tasks manually...")
    print("=" * 60)

    for task in SCHEDULED_TASKS:
        task_name = task["name"]
        script = task["script"]

        print(f"\nRunning: {task_name}")
        try:
            result = subprocess.run(
                [sys.executable, *script.split()],
                cwd=str(MEMORY_DIR),
                capture_output=True, text=True
            )
            print(f"  Output: {result.stdout.strip()}")
            log_task_run(task_name, "Manual run - success")
        except Exception as e:
            print(f"  Error: {e}")
            log_task_run(task_name, f"Manual run - error: {e}")


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        return

    command = sys.argv[1]
    commands = {
        "setup": setup_tasks,
        "list": list_tasks,
        "remove": remove_tasks,
        "run": run_all,
    }

    if command in commands:
        commands[command]()
    else:
        print(f"Unknown command: {command}")
        print(f"Available: {', '.join(commands.keys())}")


if __name__ == "__main__":
    main()
