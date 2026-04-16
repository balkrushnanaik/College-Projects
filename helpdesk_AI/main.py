"""
AI Help Desk Management System — Main CLI
Run: python main.py
"""

import sys
import os

# Make sure local modules resolve correctly
sys.path.insert(0, os.path.dirname(__file__))

from models.ai_engine   import classify_ticket, suggest_keywords, KNOWLEDGE_BASE
from models.ticket_store import (
    create_ticket, get_all_tickets, get_ticket,
    update_status, add_comment, delete_ticket,
    get_stats, STATUS_FLOW,
)
from utils.ui import (
    banner, section, success, warning, error, info,
    ticket_card, tickets_table, stats_panel, prompt,
    colorize, BOLD, CYAN, YELLOW, GREEN, RED,
)


# ──────────────────────────────────────────────
# Menu handlers
# ──────────────────────────────────────────────

def menu_submit():
    section("🎫  Submit New Ticket")
    name  = prompt("Your full name")
    if not name:
        warning("Name cannot be empty."); return
    email = prompt("Your email address")
    if "@" not in email:
        warning("Please enter a valid email."); return

    print(colorize("\n  Describe your issue (type END on a new line to finish):", BOLD))
    lines = []
    while True:
        try:
            line = input("    ")
        except EOFError:
            break
        if line.strip().upper() == "END":
            break
        lines.append(line)
    description = "\n".join(lines).strip()
    if not description:
        warning("Description cannot be empty."); return

    info("Analyzing issue with AI engine…")
    result = classify_ticket(description)

    print(f"\n  {colorize('AI Classification Result', BOLD, CYAN)}")
    print(f"    Category   : {result['category']}")
    print(f"    Priority   : {result['priority_icon']}  {result['priority']}")
    print(f"    Confidence : {result['confidence']}%")
    print(f"    ETA        : {result['eta']}")

    confirm = prompt("\n  Create ticket? (y/n)", "y").lower()
    if confirm != "y":
        warning("Ticket creation cancelled.")
        return

    ticket = create_ticket(name, email, description, result)
    success(f"Ticket created: {ticket['id']}")
    ticket_card(ticket)


def menu_view_all():
    section("📋  All Tickets")
    tickets = get_all_tickets()

    # Optional filter
    filt = prompt("Filter by status (Open/In Progress/Resolved/Closed) or press Enter for all", "")
    if filt:
        tickets = [t for t in tickets if t["status"].lower() == filt.lower()]

    sort_key = prompt("Sort by (priority/date/status)", "date")
    if sort_key == "priority":
        order = {"Critical": 0, "High": 1, "Medium": 2, "Low": 3}
        tickets.sort(key=lambda t: order.get(t["priority"], 9))
    elif sort_key == "status":
        tickets.sort(key=lambda t: STATUS_FLOW.index(t["status"]) if t["status"] in STATUS_FLOW else 9)
    else:
        tickets.sort(key=lambda t: t["created_at"], reverse=True)

    tickets_table(tickets)
    info(f"{len(tickets)} ticket(s) displayed.")


def menu_view_one():
    section("🔍  View Ticket Details")
    tid = prompt("Enter Ticket ID (e.g. TKT-0001)").upper()
    ticket = get_ticket(tid)
    if not ticket:
        error(f"Ticket {tid} not found.")
        return
    ticket_card(ticket)


def menu_update_status():
    section("🔄  Update Ticket Status")
    tid = prompt("Ticket ID to update").upper()
    ticket = get_ticket(tid)
    if not ticket:
        error(f"Ticket {tid} not found."); return

    print(f"  Current status: {colorize(ticket['status'], BOLD, CYAN)}")
    print(f"  Available statuses: {', '.join(STATUS_FLOW)}")
    new_status = prompt("New status")

    if new_status not in STATUS_FLOW:
        error(f"Invalid status. Choose from: {', '.join(STATUS_FLOW)}"); return

    update_status(tid, new_status)
    success(f"Ticket {tid} status updated to '{new_status}'.")


def menu_add_comment():
    section("💬  Add Comment to Ticket")
    tid    = prompt("Ticket ID").upper()
    ticket = get_ticket(tid)
    if not ticket:
        error(f"Ticket {tid} not found."); return

    author  = prompt("Your name")
    comment = prompt("Comment")
    if not comment:
        warning("Comment cannot be empty."); return

    add_comment(tid, author, comment)
    success("Comment added.")


def menu_delete():
    section("🗑️   Delete Ticket")
    tid = prompt("Ticket ID to delete").upper()
    confirm = prompt(f"Are you sure you want to delete {tid}? (yes/no)", "no").lower()
    if confirm != "yes":
        warning("Deletion cancelled."); return
    if delete_ticket(tid):
        success(f"Ticket {tid} deleted.")
    else:
        error(f"Ticket {tid} not found.")


def menu_dashboard():
    stats = get_stats()
    if stats["total"] == 0:
        warning("No tickets yet. Submit one first!")
        return
    stats_panel(stats)


def menu_ai_demo():
    section("🧪  AI Engine Demo — Test Classification")
    print(colorize("  Enter any issue description and see how the AI classifies it.\n", CYAN))
    description = prompt("Describe an issue")
    if not description:
        return
    result = classify_ticket(description)
    print(f"\n  {colorize('Classification Result', BOLD, CYAN)}")
    print(f"    Topic Key  : {result['topic_key']}")
    print(f"    Category   : {result['category']}")
    print(f"    Priority   : {result['priority_icon']}  {result['priority']}")
    print(f"    Confidence : {result['confidence']}%")
    print(f"    ETA        : {result['eta']}")
    print(f"\n  {colorize('Suggested Solution:', BOLD)}")
    for line in result["solution"].splitlines():
        print(f"    {line}")

    # autocomplete demo
    partial = prompt("\n  Test keyword autocomplete (type 2+ letters)")
    if partial:
        suggestions = suggest_keywords(partial)
        if suggestions:
            info(f"Suggestions: {', '.join(suggestions)}")
        else:
            warning("No suggestions found.")


def menu_knowledge_base():
    section("📚  Knowledge Base — Categories & Keywords")
    for key, info_dict in KNOWLEDGE_BASE.items():
        if key == "general":
            continue
        print(f"\n  {colorize(info_dict['category'], BOLD, CYAN)}")
        print(f"    Priority : {info_dict['priority']}")
        print(f"    Keywords : {', '.join(info_dict['keywords'])}")
        print(f"    ETA      : {info_dict['estimated_time']}")
    print()


# ──────────────────────────────────────────────
# Main loop
# ──────────────────────────────────────────────

MENU = [
    ("1", "Submit New Ticket",           menu_submit),
    ("2", "View All Tickets",            menu_view_all),
    ("3", "View Ticket Details",         menu_view_one),
    ("4", "Update Ticket Status",        menu_update_status),
    ("5", "Add Comment",                 menu_add_comment),
    ("6", "Delete Ticket",               menu_delete),
    ("7", "Dashboard / Statistics",      menu_dashboard),
    ("8", "AI Engine Demo",              menu_ai_demo),
    ("9", "Browse Knowledge Base",       menu_knowledge_base),
    ("0", "Exit",                        None),
]


def print_menu():
    section("🏠  Main Menu")
    for key, label, _ in MENU:
        if key == "0":
            print(colorize(f"    [{key}] {label}", RED))
        else:
            print(f"    {colorize(f'[{key}]', BOLD, CYAN)} {label}")
    print()


def main():
    banner()
    while True:
        print_menu()
        choice = prompt("Choose an option", "1")
        handler = None
        for key, _, fn in MENU:
            if choice == key:
                handler = fn
                break
        if handler is None and choice == "0":
            print(colorize("\n  👋  Goodbye! Stay productive.\n", BOLD, GREEN))
            break
        elif handler:
            try:
                handler()
            except KeyboardInterrupt:
                warning("\n  Action cancelled.")
        else:
            error("Invalid option. Please choose from the menu.")
        input(colorize("\n  Press Enter to continue…", YELLOW))


if __name__ == "__main__":
    main()
