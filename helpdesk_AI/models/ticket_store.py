"""
Ticket store — in-memory (JSON-backed) ticket management.
"""

import json
import os
import uuid
from datetime import datetime

_DATA_FILE = os.path.join(os.path.dirname(__file__), "..", "data", "tickets.json")


def _load() -> dict:
    if os.path.exists(_DATA_FILE):
        with open(_DATA_FILE, "r") as f:
            return json.load(f)
    return {"tickets": [], "next_id": 1}


def _save(store: dict) -> None:
    os.makedirs(os.path.dirname(_DATA_FILE), exist_ok=True)
    with open(_DATA_FILE, "w") as f:
        json.dump(store, f, indent=2)


STATUS_FLOW = ["Open", "In Progress", "Resolved", "Closed"]


def create_ticket(name: str, email: str, description: str, ai_result: dict) -> dict:
    store = _load()
    ticket_id = f"TKT-{store['next_id']:04d}"
    ticket = {
        "id":          ticket_id,
        "name":        name,
        "email":       email,
        "description": description,
        "category":    ai_result["category"],
        "priority":    ai_result["priority"],
        "solution":    ai_result["solution"],
        "eta":         ai_result["eta"],
        "confidence":  ai_result["confidence"],
        "status":      "Open",
        "created_at":  datetime.now().isoformat(timespec="seconds"),
        "updated_at":  datetime.now().isoformat(timespec="seconds"),
        "comments":    [],
    }
    store["tickets"].append(ticket)
    store["next_id"] += 1
    _save(store)
    return ticket


def get_all_tickets() -> list[dict]:
    return _load()["tickets"]


def get_ticket(ticket_id: str) -> dict | None:
    for t in _load()["tickets"]:
        if t["id"] == ticket_id:
            return t
    return None


def update_status(ticket_id: str, new_status: str) -> dict | None:
    store = _load()
    for t in store["tickets"]:
        if t["id"] == ticket_id:
            t["status"] = new_status
            t["updated_at"] = datetime.now().isoformat(timespec="seconds")
            _save(store)
            return t
    return None


def add_comment(ticket_id: str, author: str, text: str) -> dict | None:
    store = _load()
    for t in store["tickets"]:
        if t["id"] == ticket_id:
            t["comments"].append({
                "author": author,
                "text":   text,
                "at":     datetime.now().isoformat(timespec="seconds"),
            })
            t["updated_at"] = datetime.now().isoformat(timespec="seconds")
            _save(store)
            return t
    return None


def delete_ticket(ticket_id: str) -> bool:
    store = _load()
    before = len(store["tickets"])
    store["tickets"] = [t for t in store["tickets"] if t["id"] != ticket_id]
    if len(store["tickets"]) < before:
        _save(store)
        return True
    return False


def get_stats() -> dict:
    tickets = get_all_tickets()
    total = len(tickets)
    by_status   = {}
    by_priority = {}
    by_category = {}
    for t in tickets:
        by_status[t["status"]]     = by_status.get(t["status"], 0) + 1
        by_priority[t["priority"]] = by_priority.get(t["priority"], 0) + 1
        by_category[t["category"]] = by_category.get(t["category"], 0) + 1
    return {
        "total":       total,
        "by_status":   by_status,
        "by_priority": by_priority,
        "by_category": by_category,
    }
