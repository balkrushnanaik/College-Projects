"""
Terminal UI helpers — colors, tables, banners.
No third-party dependencies.
"""

# ANSI codes
RESET  = "\033[0m"
BOLD   = "\033[1m"
DIM    = "\033[2m"

BLACK  = "\033[30m"
RED    = "\033[31m"
GREEN  = "\033[32m"
YELLOW = "\033[33m"
BLUE   = "\033[34m"
CYAN   = "\033[36m"
WHITE  = "\033[37m"

BG_BLUE  = "\033[44m"
BG_CYAN  = "\033[46m"


def colorize(text: str, *codes: str) -> str:
    return "".join(codes) + text + RESET


def banner():
    print(colorize("""
╔══════════════════════════════════════════════════════════════╗
║      🤖  AI HELP DESK MANAGEMENT SYSTEM  v1.0               ║
║         Powered by NLP · TF-IDF · Rule-Based AI             ║
╚══════════════════════════════════════════════════════════════╝
""", BOLD, CYAN))


def section(title: str):
    width = 62
    bar = "─" * width
    print(colorize(f"\n┌{bar}┐", BLUE))
    print(colorize(f"│  {title:<60}│", BOLD, BLUE))
    print(colorize(f"└{bar}┘", BLUE))


def success(msg: str):  print(colorize(f"  ✅  {msg}", GREEN))
def warning(msg: str):  print(colorize(f"  ⚠️   {msg}", YELLOW))
def error(msg: str):    print(colorize(f"  ❌  {msg}", RED))
def info(msg: str):     print(colorize(f"  ℹ️   {msg}", CYAN))


def priority_color(priority: str) -> str:
    mapping = {
        "Critical": RED,
        "High":     YELLOW,
        "Medium":   CYAN,
        "Low":      GREEN,
    }
    return colorize(priority, BOLD, mapping.get(priority, WHITE))


def status_color(status: str) -> str:
    mapping = {
        "Open":        CYAN,
        "In Progress": YELLOW,
        "Resolved":    GREEN,
        "Closed":      DIM,
    }
    return colorize(status, BOLD, mapping.get(status, WHITE))


def ticket_card(ticket: dict):
    w = 64
    bar = "═" * w
    print(colorize(f"\n╔{bar}╗", CYAN))
    print(colorize(f"║  Ticket: {ticket['id']:<10}  Status: {ticket['status']:<12}  Priority: {ticket['priority']:<10}║", BOLD))
    print(colorize(f"╠{bar}╣", CYAN))
    print(f"  {colorize('Requester:', BOLD)} {ticket['name']}  <{ticket['email']}>")
    print(f"  {colorize('Category:', BOLD)}  {ticket['category']}")
    print(f"  {colorize('Created:', BOLD)}   {ticket['created_at']}")
    print(f"  {colorize('ETA:', BOLD)}       {ticket['eta']}")
    print(f"  {colorize('AI Confidence:', BOLD)} {ticket['confidence']}%")
    print(colorize(f"╠{bar}╣", CYAN))
    print(f"  {colorize('Issue:', BOLD)}")
    for line in ticket['description'].splitlines():
        print(f"    {line}")
    print(colorize(f"╠{bar}╣", CYAN))
    print(f"  {colorize('AI Suggested Solution:', BOLD)}")
    for line in ticket['solution'].splitlines():
        print(f"    {line}")
    if ticket.get("comments"):
        print(colorize(f"╠{bar}╣", CYAN))
        print(f"  {colorize('Comments:', BOLD)}")
        for c in ticket["comments"]:
            print(f"    [{c['at']}] {colorize(c['author'], BOLD)}: {c['text']}")
    print(colorize(f"╚{bar}╝", CYAN))


def tickets_table(tickets: list[dict]):
    if not tickets:
        warning("No tickets found.")
        return
    print()
    header = f"  {'ID':<12} {'Name':<16} {'Category':<18} {'Priority':<10} {'Status':<14} {'Created':<22}"
    print(colorize(header, BOLD, BLUE))
    print(colorize("  " + "─" * 92, BLUE))
    for t in tickets:
        row = (
            f"  {colorize(t['id'], CYAN):<21}"
            f" {t['name']:<16}"
            f" {t['category']:<18}"
            f" {priority_color(t['priority']):<19}"
            f" {status_color(t['status']):<23}"
            f" {t['created_at'][:19]}"
        )
        print(row)
    print()


def stats_panel(stats: dict):
    section("📊  Dashboard — Live Statistics")
    total = stats["total"]
    print(f"\n  {colorize('Total Tickets:', BOLD)} {colorize(str(total), BOLD, CYAN)}\n")

    def bar_chart(label: str, data: dict, color: str):
        print(colorize(f"  {label}", BOLD))
        for k, v in sorted(data.items(), key=lambda x: -x[1]):
            pct = int((v / total) * 30) if total else 0
            bar = "█" * pct + "░" * (30 - pct)
            print(f"    {k:<14} {colorize(bar, color)}  {v}")
        print()

    bar_chart("By Status:",   stats["by_status"],   GREEN)
    bar_chart("By Priority:", stats["by_priority"],  YELLOW)
    bar_chart("By Category:", stats["by_category"],  CYAN)


def prompt(text: str, default: str = "") -> str:
    suffix = f" [{default}]" if default else ""
    try:
        val = input(colorize(f"  → {text}{suffix}: ", BOLD, WHITE)).strip()
    except (EOFError, KeyboardInterrupt):
        print()
        return default
    return val if val else default
