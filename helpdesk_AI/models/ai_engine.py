"""
AI Engine for Help Desk Management
Uses NLP techniques: TF-IDF, keyword matching, and rule-based classification
"""

import re
import math
from collections import Counter


# ──────────────────────────────────────────────
# Knowledge Base
# ──────────────────────────────────────────────
KNOWLEDGE_BASE = {
    "password_reset": {
        "keywords": ["password", "reset", "forgot", "login", "can't login", "locked", "unlock", "credentials"],
        "category": "Account & Security",
        "priority": "Medium",
        "solution": (
            "To reset your password:\n"
            "  1. Go to the login page and click 'Forgot Password'.\n"
            "  2. Enter your registered email address.\n"
            "  3. Check your inbox for a reset link (valid for 30 minutes).\n"
            "  4. Follow the link and set a new strong password.\n"
            "  If you're still locked out after 3 attempts, contact IT Security."
        ),
        "estimated_time": "5–10 minutes",
    },
    "software_install": {
        "keywords": ["install", "software", "application", "download", "setup", "program", "app"],
        "category": "Software",
        "priority": "Low",
        "solution": (
            "For software installation:\n"
            "  1. Raise an approved-software request in the IT Portal.\n"
            "  2. Get manager approval (usually within 24 hrs).\n"
            "  3. IT will push the installation remotely, or send instructions.\n"
            "  4. Restart your machine post-install.\n"
            "  Note: Unauthorized software violates company policy."
        ),
        "estimated_time": "1–2 business days",
    },
    "network_issue": {
        "keywords": ["network", "internet", "wifi", "connection", "slow", "disconnected", "vpn", "offline"],
        "category": "Network",
        "priority": "High",
        "solution": (
            "Troubleshooting network issues:\n"
            "  1. Restart your router/modem (unplug 30 sec).\n"
            "  2. Forget and reconnect to the Wi-Fi network.\n"
            "  3. Check VPN status — disconnect and reconnect.\n"
            "  4. Run: ipconfig /release && ipconfig /renew (Windows).\n"
            "  5. If persistent, escalate to the Network team with your IP address."
        ),
        "estimated_time": "15–60 minutes",
    },
    "hardware_issue": {
        "keywords": ["hardware", "laptop", "computer", "mouse", "keyboard", "monitor", "screen", "printer", "device"],
        "category": "Hardware",
        "priority": "High",
        "solution": (
            "For hardware problems:\n"
            "  1. Perform a hard reboot (hold power 10 sec, then restart).\n"
            "  2. Check all cable connections.\n"
            "  3. Test peripherals on another machine to isolate the fault.\n"
            "  4. If device is under warranty, log a replacement request.\n"
            "  5. For critical failures, request a loaner device from IT."
        ),
        "estimated_time": "Same day – 3 business days",
    },
    "email_issue": {
        "keywords": ["email", "outlook", "mail", "inbox", "calendar", "teams", "send", "receive", "spam"],
        "category": "Communication",
        "priority": "Medium",
        "solution": (
            "Resolving email issues:\n"
            "  1. Restart Outlook / Mail client.\n"
            "  2. Check account settings — IMAP/SMTP ports.\n"
            "  3. Clear cache: File → Account Settings → Repair.\n"
            "  4. Verify mailbox quota isn't full.\n"
            "  5. Re-add the account if sync fails after reboot."
        ),
        "estimated_time": "10–30 minutes",
    },
    "data_backup": {
        "keywords": ["backup", "restore", "data", "file", "lost", "recover", "deleted", "storage"],
        "category": "Data Management",
        "priority": "Critical",
        "solution": (
            "Data backup and recovery:\n"
            "  1. Check Recycle Bin / Trash first.\n"
            "  2. Search OneDrive/SharePoint version history.\n"
            "  3. Contact IT immediately — do NOT write new data to the drive.\n"
            "  4. IT will attempt shadow-copy restore (up to 30 days back).\n"
            "  5. For critical data loss, a forensic recovery may be initiated."
        ),
        "estimated_time": "1–5 business days",
    },
    "general": {
        "keywords": [],
        "category": "General",
        "priority": "Low",
        "solution": (
            "I've logged your ticket for review by a human agent.\n"
            "You'll receive an update within 4 business hours.\n"
            "For urgent issues, call the IT Hotline: 1800-HELPDESK."
        ),
        "estimated_time": "4 business hours",
    },
}

PRIORITY_COLORS = {
    "Critical": "🔴",
    "High":     "🟠",
    "Medium":   "🟡",
    "Low":      "🟢",
}


# ──────────────────────────────────────────────
# TF-IDF helpers
# ──────────────────────────────────────────────

def _tokenize(text: str) -> list[str]:
    return re.findall(r"\b[a-z]{2,}\b", text.lower())


def _tf(tokens: list[str]) -> dict[str, float]:
    count = Counter(tokens)
    total = len(tokens) or 1
    return {w: c / total for w, c in count.items()}


def _build_idf() -> dict[str, float]:
    docs = [" ".join(v["keywords"]) for v in KNOWLEDGE_BASE.values()]
    N = len(docs)
    idf: dict[str, float] = {}
    all_words = set(w for doc in docs for w in _tokenize(doc))
    for word in all_words:
        df = sum(1 for doc in docs if word in _tokenize(doc))
        idf[word] = math.log((N + 1) / (df + 1)) + 1
    return idf


_IDF = _build_idf()


def _tfidf_score(query_tokens: list[str], keywords: list[str]) -> float:
    if not keywords:
        return 0.0
    kw_tokens = _tokenize(" ".join(keywords))
    tf_q = _tf(query_tokens)
    score = 0.0
    for word, tf_val in tf_q.items():
        if word in kw_tokens:
            score += tf_val * _IDF.get(word, 1.0)
    return score


# ──────────────────────────────────────────────
# Classifier
# ──────────────────────────────────────────────

def classify_ticket(description: str) -> dict:
    """Return the best matching KB entry + confidence score."""
    tokens = _tokenize(description)
    best_key, best_score = "general", 0.0

    for key, info in KNOWLEDGE_BASE.items():
        if key == "general":
            continue
        score = _tfidf_score(tokens, info["keywords"])
        # boost for direct keyword substring match
        for kw in info["keywords"]:
            if kw in description.lower():
                score += 0.4
        if score > best_score:
            best_score = score
            best_key = key

    confidence = min(round(best_score * 40, 1), 99.0)  # normalize 0–99%
    if best_score < 0.1:
        best_key = "general"
        confidence = 0.0

    entry = KNOWLEDGE_BASE[best_key]
    return {
        "topic_key":   best_key,
        "category":    entry["category"],
        "priority":    entry["priority"],
        "solution":    entry["solution"],
        "eta":         entry["estimated_time"],
        "confidence":  confidence,
        "priority_icon": PRIORITY_COLORS[entry["priority"]],
    }


def suggest_keywords(partial: str) -> list[str]:
    """Simple autocomplete from all KB keywords."""
    partial = partial.lower()
    suggestions = []
    for info in KNOWLEDGE_BASE.values():
        for kw in info["keywords"]:
            if kw.startswith(partial) and kw not in suggestions:
                suggestions.append(kw)
    return sorted(suggestions)[:5]
