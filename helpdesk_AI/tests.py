"""
Unit tests — AI Help Desk Management System
Run: python tests.py
"""

import sys, os, json, tempfile
sys.path.insert(0, os.path.dirname(__file__))

# Patch data file to a temp location before importing ticket_store
import models.ticket_store as ts
_tmpfile = tempfile.mktemp(suffix=".json")
ts._DATA_FILE = _tmpfile

from models.ai_engine   import classify_ticket, suggest_keywords
from models.ticket_store import create_ticket, get_all_tickets, update_status, get_stats, delete_ticket, add_comment

PASS = "\033[32m✅ PASS\033[0m"
FAIL = "\033[31m❌ FAIL\033[0m"

results = {"pass": 0, "fail": 0}

def check(name: str, condition: bool, extra: str = ""):
    tag = PASS if condition else FAIL
    print(f"  {tag}  {name}" + (f"  ({extra})" if extra else ""))
    if condition:
        results["pass"] += 1
    else:
        results["fail"] += 1


# ── AI Engine Tests ──────────────────────────

print("\n\033[1m── AI Engine ──────────────────────────────\033[0m")

r = classify_ticket("I forgot my password and can't login")
check("Password reset classification", r["topic_key"] == "password_reset", f"got {r['topic_key']}")
check("Password reset category", r["category"] == "Account & Security")
check("Confidence > 0", r["confidence"] > 0)

r = classify_ticket("My laptop screen is broken and keyboard not working")
check("Hardware classification", r["topic_key"] == "hardware_issue", f"got {r['topic_key']}")
check("Hardware priority High", r["priority"] == "High")

r = classify_ticket("Internet is very slow and wifi keeps disconnecting")
check("Network classification", r["topic_key"] == "network_issue", f"got {r['topic_key']}")

r = classify_ticket("I need to install Python on my computer")
check("Software install classification", r["topic_key"] == "software_install", f"got {r['topic_key']}")

r = classify_ticket("My Outlook is not receiving emails")
check("Email issue classification", r["topic_key"] == "email_issue", f"got {r['topic_key']}")

r = classify_ticket("I accidentally deleted an important file")
check("Data backup classification", r["topic_key"] == "data_backup", f"got {r['topic_key']}")
check("Data backup priority Critical", r["priority"] == "Critical")

r = classify_ticket("xyzzy frobble wumpus")
check("Unknown issue falls to general", r["topic_key"] == "general")

s = suggest_keywords("pass")
check("Autocomplete 'pass' → 'password'", "password" in s)

s = suggest_keywords("net")
check("Autocomplete 'net' → 'network'", "network" in s)

# ── Ticket Store Tests ───────────────────────

print("\n\033[1m── Ticket Store ────────────────────────────\033[0m")

ai = classify_ticket("My wifi keeps dropping connection all day")
t1 = create_ticket("Alice", "alice@test.com", "wifi issue", ai)
check("Ticket created with ID", t1["id"].startswith("TKT-"))
check("Ticket status is Open", t1["status"] == "Open")
check("Ticket email stored", t1["email"] == "alice@test.com")

t2 = create_ticket("Bob", "bob@test.com", "can't reset password", classify_ticket("can't reset password"))
all_t = get_all_tickets()
check("Two tickets stored", len(all_t) == 2)

updated = update_status(t1["id"], "In Progress")
check("Status updated to In Progress", updated["status"] == "In Progress")

commented = add_comment(t1["id"], "Support Agent", "Working on it now.")
check("Comment added", len(commented["comments"]) == 1)
check("Comment author correct", commented["comments"][0]["author"] == "Support Agent")

stats = get_stats()
check("Stats total correct", stats["total"] == 2)
check("Stats has by_priority", "by_priority" in stats)
check("Stats has In Progress", "In Progress" in stats["by_status"])

deleted = delete_ticket(t2["id"])
check("Ticket deleted", deleted is True)
check("Total after delete is 1", len(get_all_tickets()) == 1)

# ── Summary ─────────────────────────────────

total = results["pass"] + results["fail"]
print(f"\n\033[1m── Results: {results['pass']}/{total} passed ──────────────────────────\033[0m\n")

# Cleanup
try: os.remove(_tmpfile)
except: pass

sys.exit(0 if results["fail"] == 0 else 1)
