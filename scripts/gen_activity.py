"""Render the last year of contributions as an animated `valgrind` memory dump.

usage:
  GITHUB_TOKEN=... python scripts/gen_activity.py <login> <out.svg>      # fetch live (GitHub Actions)
  python scripts/gen_activity.py --from-json data.json <out.svg>          # offline / preview

Standard library only.
"""
import datetime as dt
import json
import os
import sys
import urllib.request
from xml.sax.saxutils import escape

BG, RAISED, LINE = "#0a0e14", "#0f1621", "#1f2a37"
TEXT, DIM, FAINT = "#e6edf3", "#8b98a9", "#4f5d6e"
ACCENT, ACCENT2, GREEN = "#5ac8fa", "#a78bfa", "#7ee787"
LEVELS = {"NONE": "#121a25", "FIRST_QUARTILE": "#0e3a52", "SECOND_QUARTILE": "#1572a1",
          "THIRD_QUARTILE": "#2aa7e0", "FOURTH_QUARTILE": "#5ac8fa"}
MONO = "'JetBrains Mono','SFMono-Regular',Consolas,'Liberation Mono',Menlo,monospace"

QUERY = """query($login:String!){user(login:$login){contributionsCollection{contributionCalendar{
totalContributions weeks{contributionDays{date contributionCount contributionLevel}}}}}}"""


def fetch(login):
    req = urllib.request.Request(
        "https://api.github.com/graphql",
        data=json.dumps({"query": QUERY, "variables": {"login": login}}).encode(),
        headers={"Authorization": f"bearer {os.environ['GITHUB_TOKEN']}", "Content-Type": "application/json"},
    )
    with urllib.request.urlopen(req, timeout=30) as r:
        data = json.load(r)
    if "errors" in data:
        sys.exit(f"GraphQL error: {data['errors']}")
    return data["data"]["user"]["contributionsCollection"]["contributionCalendar"]


def load_json(path):
    data = json.load(open(path, encoding="utf-8"))["data"]
    root = data.get("user") or data.get("viewer")
    return root["contributionsCollection"]["contributionCalendar"]


def plural(n, word):
    return f"{n} {word}{'s' * (n != 1)}"


def streaks(days):
    longest = run = 0
    for d in days:
        run = run + 1 if d["contributionCount"] else 0
        longest = max(longest, run)
    current = 0
    tail = days[:-1] if days and not days[-1]["contributionCount"] else days  # today may still be empty
    for d in reversed(tail):
        if not d["contributionCount"]:
            break
        current += 1
    return longest, current


def render(cal):
    weeks = cal["weeks"]
    days = [d for w in weeks for d in w["contributionDays"]]
    total = cal["totalContributions"]
    longest, current = streaks(days)
    best = max(days, key=lambda d: d["contributionCount"])
    best_date = dt.date.fromisoformat(best["date"]).strftime("%b %d")
    active = sum(1 for d in days if d["contributionCount"])

    W, cell, gap = 840, 11, 2
    step = cell + gap
    gx, gy = 108, 104
    H = 352
    p = [f'<rect x=".5" y=".5" width="{W - 1}" height="{H - 1}" rx="12" fill="{BG}" stroke="{LINE}"/>',
         f'<path d="M12.5 .5h{W - 25}a12 12 0 0 1 12 12V38H.5V12.5a12 12 0 0 1 12-12z" fill="{RAISED}" stroke="{LINE}"/>',
         '<circle cx="24" cy="19" r="6" fill="#ff5f57"/><circle cx="44" cy="19" r="6" fill="#febc2e"/>'
         '<circle cx="64" cy="19" r="6" fill="#28c840"/>',
         f'<text x="{W // 2}" y="24" text-anchor="middle" class="m" font-size="12" fill="{FAINT}">memcheck — ahmad@amman</text>',
         f'<text x="24" y="66" class="m" font-size="13.5"><tspan fill="{GREEN}">$</tspan>'
         f'<tspan fill="{TEXT}"> valgrind --leak-check=full ./contributions --last-year</tspan></text>']

    # legend
    lx = W - 24 - 5 * 13 - 70
    p.append(f'<text x="{lx}" y="64" class="m" font-size="10" fill="{FAINT}">less</text>')
    for i, c in enumerate(LEVELS.values()):
        p.append(f'<rect x="{lx + 30 + i * 13}" y="55" width="11" height="11" rx="2" fill="{c}"/>')
    p.append(f'<text x="{lx + 30 + 5 * 13 + 4}" y="64" class="m" font-size="10" fill="{FAINT}">more</text>')

    # month labels
    last_month = None
    for wi, w in enumerate(weeks):
        m = dt.date.fromisoformat(w["contributionDays"][0]["date"]).month
        if m != last_month and wi < len(weeks) - 2:
            name = dt.date(2000, m, 1).strftime("%b")
            p.append(f'<text x="{gx + wi * step}" y="{gy - 14}" class="m" font-size="10" fill="{FAINT}">{name}</text>')
            last_month = m

    # address column (one "row" of memory per weekday)
    for r in range(7):
        p.append(f'<text x="{gx - 10}" y="{gy + r * step + 9}" text-anchor="end" class="m" font-size="10" fill="{FAINT}">'
                 f'0x7ffd{r * 0x40:04x}</text>')

    # cells: allocated column by column
    for wi, w in enumerate(weeks):
        cells = []
        for d in w["contributionDays"]:
            r = dt.date.fromisoformat(d["date"]).weekday()  # Mon=0
            r = (r + 1) % 7  # GitHub rows start on Sunday
            n = d["contributionCount"]
            cells.append(f'<rect x="{gx + wi * step}" y="{gy + r * step}" width="{cell}" height="{cell}" rx="2" '
                         f'fill="{LEVELS[d["contributionLevel"]]}"><title>{d["date"]}: {n} contribution{"s" * (n != 1)}</title></rect>')
        p.append(f'<g class="alloc" style="animation-delay:{.3 + wi * .028:.3f}s">{"".join(cells)}</g>')

    gw = len(weeks) * step
    # scanner sweeping the heap
    p.append(f'<rect class="scan" x="{gx - 4}" y="{gy - 4}" width="{step + 2}" height="{7 * step + 6}" rx="3" '
             f'fill="none" stroke="{ACCENT2}" stroke-width="1.5"/>')

    # heap summary
    pid = "==42=="
    lines = [
        [(pid, FAINT), (" HEAP SUMMARY:", TEXT)],
        [(pid, FAINT), ("     in use at exit: ", DIM), ("0 bytes in 0 blocks", GREEN)],
        [(pid, FAINT), ("   total heap usage: ", DIM), (f"{total} allocs", ACCENT), (f", {total} frees", DIM),
         (f" — one per contribution, {plural(active, 'active day')}", FAINT)],
        [(pid, FAINT), ("   longest streak: ", DIM), (plural(longest, "day"), ACCENT2), ("   current streak: ", DIM),
         (plural(current, "day"), ACCENT2), ("   busiest day: ", DIM), (f"{best_date} ({best['contributionCount']})", ACCENT)],
        [(pid, FAINT), (" All heap blocks were freed -- no leaks are possible", GREEN)],
    ]
    for i, segs in enumerate(lines):
        spans = "".join(f'<tspan fill="{c}">{escape(s)}</tspan>' for s, c in segs)
        p.append(f'<text x="24" y="{gy + 7 * step + 44 + i * 21}" class="m line" style="animation-delay:{2.0 + i * .35:.2f}s" '
                 f'font-size="12.5" xml:space="preserve">{spans}</text>')
    p.append(f'<text x="24" y="{H - 16}" class="m cursor" font-size="12.5" fill="{ACCENT}">▍</text>')

    css = f"""
.m{{font-family:{MONO}}}
.alloc{{opacity:0;animation:alloc .35s ease-out forwards}}
@keyframes alloc{{from{{opacity:0;transform:translateY(-4px)}}to{{opacity:1;transform:none}}}}
.scan{{opacity:0;animation:scan 7s linear 2s infinite}}
@keyframes scan{{0%{{opacity:.9;transform:translateX(0)}}92%{{opacity:.9;transform:translateX({gw - step}px)}}100%{{opacity:0;transform:translateX({gw - step}px)}}}}
.line{{opacity:0;animation:fade .4s forwards}}
@keyframes fade{{to{{opacity:1}}}}
.cursor{{animation:blink 1.05s step-end infinite}}
@keyframes blink{{50%{{opacity:0}}}}
@media (prefers-reduced-motion:reduce){{*{{animation:none!important;opacity:1!important;transform:none!important}}}}
"""
    title = f"{total} contributions in the last year; longest streak {plural(longest, 'day')}, current streak {plural(current, 'day')}."
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" role="img" '
            f'aria-label="{escape(title)}"><title>{escape(title)}</title><style>{css}</style>\n' + "\n".join(p) + "\n</svg>\n")


def main():
    args = sys.argv[1:]
    if args[:1] == ["--from-json"]:
        cal, out = load_json(args[1]), args[2]
    else:
        cal, out = fetch(args[0]), args[1]
    os.makedirs(os.path.dirname(out) or ".", exist_ok=True)
    with open(out, "w", encoding="utf-8", newline="\n") as f:
        f.write(render(cal))
    print("wrote", out)


if __name__ == "__main__":
    main()
