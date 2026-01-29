"""
Check the status of the Notion import and log results.
Can be run manually or via scheduled task.
"""

import os
import sys
from datetime import datetime
from pathlib import Path

# Add parent to path
sys.path.insert(0, str(Path(__file__).parent))

from dotenv import load_dotenv

# Load .env from the finance project
finance_env = Path(r"c:\Users\nfval\Projects\auto_finance_merging\.env")
if finance_env.exists():
    load_dotenv(finance_env)

import requests

MEMORY_DIR = Path(__file__).parent
STATUS_LOG = MEMORY_DIR / "data" / "import_status.log"
STATUS_FILE = MEMORY_DIR / "data" / "last_import_status.txt"


def check_import():
    """Check current Notion import status."""
    api_key = os.getenv("NOTION_API_KEY")
    if not api_key:
        return {"error": "No NOTION_API_KEY found"}

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Notion-Version": "2022-06-28",
        "Content-Type": "application/json"
    }

    dbs = {
        "Expenses": "2eecc31f-2839-81a4-940f-df3784949765",
        "Income": "2eecc31f-2839-81d2-8634-e11419f36578",
        "Accounts": "2eecc31f-2839-81f0-af05-eaa513611f84",
        "Categories": "2eecc31f-2839-81e7-9cb2-f4320823185b"
    }

    results = {}

    for name, db_id in dbs.items():
        try:
            count = 0
            has_more = True
            cursor = None

            while has_more:
                payload = {"page_size": 100}
                if cursor:
                    payload["start_cursor"] = cursor

                resp = requests.post(
                    f"https://api.notion.com/v1/databases/{db_id}/query",
                    headers=headers, json=payload, timeout=30
                )

                if resp.status_code == 200:
                    data = resp.json()
                    count += len(data.get("results", []))
                    has_more = data.get("has_more", False)
                    cursor = data.get("next_cursor")
                elif resp.status_code == 429:
                    results[name] = f"{count}+ (rate limited)"
                    has_more = False
                else:
                    results[name] = f"Error: {resp.status_code}"
                    has_more = False

            results[name] = count

        except requests.exceptions.Timeout:
            results[name] = f"{count}+ (timeout)"
        except Exception as e:
            results[name] = f"Error: {str(e)[:50]}"

    return results


def log_status(results: dict):
    """Log status to file."""
    STATUS_LOG.parent.mkdir(parents=True, exist_ok=True)

    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    total = sum(v for v in results.values() if isinstance(v, int))

    log_line = f"{timestamp} | Total: {total} | " + " | ".join(
        f"{k}: {v}" for k, v in results.items()
    )

    # Append to log
    with open(STATUS_LOG, "a", encoding="utf-8") as f:
        f.write(log_line + "\n")

    # Write latest status
    status_text = f"Import Status ({timestamp})\n"
    status_text += "=" * 50 + "\n"
    for name, count in results.items():
        status_text += f"  {name:15} {count}\n"
    status_text += f"\n  TOTAL: {total}\n"
    status_text += f"  Target: 12,111 transactions\n"

    if total >= 12000:
        status_text += f"\n  STATUS: LIKELY COMPLETE!\n"
    else:
        progress = (total / 12111) * 100
        status_text += f"\n  Progress: {progress:.1f}%\n"

    STATUS_FILE.write_text(status_text, encoding="utf-8")

    return total


def main():
    print("Checking Notion import status...")
    results = check_import()

    if "error" in results:
        print(f"Error: {results['error']}")
        return

    total = log_status(results)

    print(f"Import Status ({datetime.now().strftime('%H:%M:%S')})")
    print("=" * 50)
    for name, count in results.items():
        print(f"  {name:15} {count}")
    print(f"\n  TOTAL: {total} / 12,111 ({(total/12111)*100:.1f}%)")

    if total >= 12000:
        print("\n  STATUS: LIKELY COMPLETE!")
    else:
        remaining = 12111 - total
        print(f"  Remaining: ~{remaining}")


if __name__ == "__main__":
    main()
