"""Generate the static animated profile SVGs into assets/.

usage: python scripts/gen_svgs.py assets

Edit the texts below and re-run. The daily contribution image is made by
scripts/gen_activity.py in GitHub Actions instead.
"""
import os
import sys
import textwrap
from xml.sax.saxutils import escape

OUT = sys.argv[1]
os.makedirs(OUT, exist_ok=True)

# ---------------------------------------------------------------- palette (midnight + cyan)
BG, RAISED, LINE = "#0a0e14", "#0f1621", "#1f2a37"
TEXT, DIM, FAINT = "#e6edf3", "#8b98a9", "#4f5d6e"
ACCENT, ACCENT2, GREEN, RED, YELLOW = "#5ac8fa", "#a78bfa", "#7ee787", "#ff7b72", "#e3b341"
MONO = "'JetBrains Mono','SFMono-Regular',Consolas,'Liberation Mono',Menlo,monospace"
SANS = "'Inter','Segoe UI',-apple-system,BlinkMacSystemFont,Helvetica,Arial,sans-serif"

BASE_CSS = f"""
.mono{{font-family:{MONO}}} .sans{{font-family:{SANS}}}
.fade{{opacity:0;animation:fade .7s ease-out forwards}}
.rise{{opacity:0;animation:rise .7s cubic-bezier(.2,.7,.2,1) forwards}}
@keyframes fade{{to{{opacity:1}}}}
@keyframes rise{{from{{opacity:0;transform:translateY(8px)}}to{{opacity:1;transform:none}}}}
@keyframes blink{{50%{{opacity:0}}}}
@keyframes pulse{{0%,100%{{opacity:1}}50%{{opacity:.35}}}}
.cursor{{animation:blink 1.05s step-end infinite}}
@media (prefers-reduced-motion:reduce){{*{{animation:none!important;opacity:1!important;transform:none!important}}}}
"""
# Transparent images (section titles, footer) switch text colours for GitHub's light theme
LIGHT_CSS = "@media (prefers-color-scheme:light){.tt{fill:#1f2328}.ts{fill:#59636e}.rl{fill:#d0d7de}}"


def t(s):
    return escape(s)


def svg(w, h, body, css="", title=""):
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}" '
        f'role="img" aria-label="{t(title)}">\n<title>{t(title)}</title>\n'
        f"<style>{BASE_CSS}{css}</style>\n{body}\n</svg>\n"
    )


def write(name, content):
    with open(os.path.join(OUT, name), "w", encoding="utf-8", newline="\n") as f:
        f.write(content)
    print("wrote", name, len(content), "bytes")


def frame(w, h):
    return f'<rect x=".5" y=".5" width="{w-1}" height="{h-1}" rx="12" fill="{BG}" stroke="{LINE}"/>'


def titlebar(w, label):
    return (f'<path d="M12.5 .5h{w - 25}a12 12 0 0 1 12 12V38H.5V12.5a12 12 0 0 1 12-12z" fill="{RAISED}" stroke="{LINE}"/>'
            f'<circle cx="24" cy="19" r="6" fill="#ff5f57"/><circle cx="44" cy="19" r="6" fill="#febc2e"/>'
            f'<circle cx="64" cy="19" r="6" fill="#28c840"/>'
            f'<text x="{w / 2:.0f}" y="24" text-anchor="middle" class="mono" font-size="12" fill="{FAINT}">{t(label)}</text>')


# ---------------------------------------------------------------- header
def header():
    w, h = 840, 300
    cmd = "whoami"
    cw = 9.6  # approx mono advance at 16px
    px = 32 + len("ahmad@amman:~$ ") * cw
    body = f"""{frame(w, h)}
{titlebar(w, "ahmad@amman: ~")}
<text x="32" y="78" class="mono" font-size="16"><tspan fill="{GREEN}">ahmad@amman</tspan><tspan fill="{DIM}">:</tspan><tspan fill="{ACCENT}">~</tspan><tspan fill="{DIM}">$ </tspan><tspan fill="{TEXT}">{cmd}</tspan></text>
<rect class="typer" x="{px - 2:.0f}" y="62" width="{len(cmd) * cw + 6:.0f}" height="22" fill="{BG}"/>
<g class="fade" style="animation-delay:1.1s">
  <circle class="blip" cx="38" cy="117" r="4" fill="{GREEN}"/>
  <text x="50" y="121" class="mono" font-size="13" fill="{DIM}">Amman, Jordan — open to work</text>
</g>
<text x="32" y="172" class="sans rise" style="animation-delay:1.35s" font-size="40" font-weight="700" fill="url(#name)">Ahmad Al-Khasawneh</text>
<text x="32" y="206" class="mono rise" style="animation-delay:1.6s" font-size="17" fill="{ACCENT}">Software Engineer — Systems &amp; Backend</text>
<g class="sans fade" style="animation-delay:1.9s" font-size="14.5" fill="{DIM}">
  <text x="32" y="244">CS student at Amman Arab University and learner at 42 Amman. C/C++ close to the metal,</text>
  <text x="32" y="266">Spring Boot on the backend, heading toward embedded / edge AI.<tspan class="cursor" fill="{ACCENT}"> ▍</tspan></text>
</g>
<defs><linearGradient id="name" x1="0" x2="1"><stop offset="0" stop-color="{TEXT}"/><stop offset=".55" stop-color="{TEXT}"/><stop offset="1" stop-color="{ACCENT}"/></linearGradient></defs>"""
    css = (f".typer{{animation:type 1s steps({len(cmd)}) .25s forwards}}"
           f"@keyframes type{{to{{transform:translateX({len(cmd) * cw + 6:.0f}px)}}}}"
           ".blip{animation:pulse 1.6s ease-in-out infinite}")
    write("header.svg", svg(w, h, body, css, "Ahmad Al-Khasawneh — Software Engineer, Systems & Backend"))


# ---------------------------------------------------------------- section titles
def section(num, title, sub, name):
    w, h = 840, 74
    body = f"""<g class="rise">
<text x="2" y="30" class="mono" font-size="13" fill="{ACCENT}">{num}</text>
<text x="34" y="31" class="sans tt" font-size="24" font-weight="700" fill="{TEXT}">{t(title)}</text>
<text x="34" y="56" class="sans ts" font-size="14" fill="{DIM}">{t(sub)}</text>
</g>
<rect class="rule rl" x="2" y="71" width="836" height="1" fill="{LINE}"/>
<rect class="sweep" x="2" y="70" width="48" height="2" fill="url(#g)"/>
<defs><linearGradient id="g" x1="0" x2="1"><stop offset="0" stop-color="{ACCENT}"/><stop offset="1" stop-color="{ACCENT2}"/></linearGradient></defs>"""
    css = (".rule{opacity:0;animation:fade .6s .2s forwards}"
           ".sweep{transform-box:fill-box;transform-origin:left;transform:scaleX(0);"
           "animation:grow .9s .35s cubic-bezier(.4,0,.2,1) forwards}"
           "@keyframes grow{to{transform:scaleX(1)}}")
    write(name, svg(w, h, body, css + LIGHT_CSS, f"{num} {title}"))


# ---------------------------------------------------------------- project cards
def card(name, meta, body_text, tags, out, award=None, delay=0.0):
    w, h = 412, 214
    y = 34
    parts = [frame(w, h)]
    parts.append(f'<text x="22" y="{y}" class="mono" font-size="11" letter-spacing="1.2" fill="{FAINT}">{t(meta)}</text>')
    y += 30
    parts.append(f'<text x="22" y="{y}" class="sans" font-size="20" font-weight="700" fill="{TEXT}">{t(name)}</text>')
    if award:
        parts.append(f'<text x="{w - 22}" y="{y}" text-anchor="end" class="mono" font-size="11.5" fill="{YELLOW}">{t(award)}</text>')
    y += 26
    for line in textwrap.wrap(body_text, 56):
        parts.append(f'<text x="22" y="{y}" class="sans" font-size="13" fill="{DIM}">{t(line)}</text>')
        y += 19
    tx, ty = 22, h - 34
    for tag in tags:
        tw = len(tag) * 6.9 + 16
        parts.append(f'<rect x="{tx:.0f}" y="{ty}" width="{tw:.0f}" height="20" rx="4" fill="{RAISED}" stroke="{LINE}"/>'
                     f'<text x="{tx + tw / 2:.0f}" y="{ty + 14}" text-anchor="middle" class="mono" font-size="11" fill="{ACCENT}">{t(tag)}</text>')
        tx += tw + 6
    assert tx < w, f"tags overflow on {name}"
    assert y < h - 40, f"body overflow on {name}: {y}"
    parts.append(f'<rect class="accent" x="0" y="12" width="3" height="{h - 24}" rx="1.5" fill="url(#a)"/>')
    defs = f'<defs><linearGradient id="a" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="{ACCENT}"/><stop offset="1" stop-color="{ACCENT2}"/></linearGradient></defs>'
    body = defs + f'<g class="rise" style="animation-delay:{delay}s">' + "\n".join(parts) + "</g>"
    css = f".accent{{opacity:0;animation:fade .5s {delay + .5}s forwards}}"
    write(out, svg(w, h, body, css, f"{name} — {body_text}"))


# ---------------------------------------------------------------- skills as htop
# (label, fill 0..1, tag) — a self-assessment; adjust freely
METERS = [
    ("C / C++", .92, "core"),
    ("Linux/Shell", .85, "core"),
    ("Algorithms", .80, "strong"),
    ("Spring Boot", .70, "growing"),
    ("Docker / CI", .60, "growing"),
    ("Edge AI", .28, "learning"),
]
# (pid, state, cpu, mem, command)
PROCS = [
    (42, "R", "98.2", "12.4", "systems --c --cpp --unix --memory --ipc --fds --make"),
    (101, "R", "87.5", "9.8", "spring-boot --websocket --oauth2 --jwt --rbac --jpa --flyway"),
    (155, "S", "64.0", "4.2", "codeforces --leetcode --icpc --rank=5/155"),
    (1337, "S", "51.3", "6.6", "ai-coach --behaviour-driven --adaptive-roadmaps"),
    (2024, "S", "33.7", "3.1", "env --linux --git --docker-compose --github-actions"),
    (4096, "D", "12.0", "1.5", "edge-ai --embedded --on-device-inference   # loading…"),
]
FKEYS = ["C", "C++", "Java", "Spring", "Python", "Linux", "Docker", "Postgres", "React", "Git"]


def skills():
    w, h = 840, 418
    p = [frame(w, h), titlebar(w, "htop — ahmad@amman")]
    # meters
    bx, bw = 132, 236
    for i, (label, lvl, tag) in enumerate(METERS):
        y = 66 + i * 22
        d = .2 + i * .12
        p.append(f'<text x="24" y="{y + 11}" class="mono" font-size="12" fill="{ACCENT}">{t(label)}</text>'
                 f'<text x="{bx - 8}" y="{y + 11}" class="mono" font-size="12" fill="{TEXT}">[</text>'
                 f'<rect class="bar" style="animation-delay:{d:.2f}s" x="{bx}" y="{y + 1}" width="{bw * lvl:.0f}" height="12" fill="url(#bars)"/>'
                 f'<text x="{bx + bw + 2}" y="{y + 11}" class="mono" font-size="12" fill="{TEXT}">]</text>'
                 f'<text x="{bx + bw + 18}" y="{y + 11}" class="mono fade" style="animation-delay:{d + .9:.2f}s" font-size="11" fill="{FAINT}">{t(tag)}</text>')
    # summary on the right
    info = [
        (f'<tspan fill="{ACCENT}">Tasks: </tspan><tspan fill="{TEXT}">{len(PROCS)}</tspan><tspan fill="{DIM}">, 2 running</tspan>'),
        (f'<tspan fill="{ACCENT}">Load average: </tspan><tspan fill="{TEXT}">0.42 4.20 </tspan><tspan fill="{RED}">42.00</tspan>'),
        (f'<tspan fill="{ACCENT}">Uptime: </tspan><tspan fill="{TEXT}">since 2023 · 42 Amman since 2024</tspan>'),
        (f'<tspan fill="{ACCENT}">Focus: </tspan><tspan fill="{TEXT}">backend</tspan><tspan fill="{DIM}"> → </tspan><tspan fill="{ACCENT2}">embedded / edge AI</tspan>'),
    ]
    for i, s in enumerate(info):
        p.append(f'<text x="480" y="{77 + i * 26}" class="mono fade" style="animation-delay:{.4 + i * .15:.2f}s" font-size="12.5">{s}</text>')
    # process table
    ty = 212
    p.append(f'<rect x="12" y="{ty}" width="{w - 24}" height="20" fill="{GREEN}"/>'
             f'<g class="mono" font-size="12" font-weight="700" fill="{BG}">'
             f'<text x="66" y="{ty + 14}" text-anchor="end">PID</text><text x="78" y="{ty + 14}">USER</text>'
             f'<text x="150" y="{ty + 14}">S</text><text x="210" y="{ty + 14}" text-anchor="end">CPU%</text>'
             f'<text x="252" y="{ty + 14}" text-anchor="end">MEM%</text><text x="268" y="{ty + 14}">COMMAND</text></g>')
    row_h = 22
    first = ty + 24
    p.append(f'<rect class="sel" x="12" y="{first}" width="{w - 24}" height="{row_h}" fill="{ACCENT}" opacity=".16"/>')
    for i, (pid, st, cpu, mem, cmd) in enumerate(PROCS):
        y = first + i * row_h + 15
        sc = {"R": GREEN, "S": DIM, "D": YELLOW}[st]
        name, _, args = cmd.partition(" ")
        p.append(f'<g class="rise" style="animation-delay:{.9 + i * .1:.2f}s" font-size="12">'
                 f'<text x="66" y="{y}" text-anchor="end" class="mono" fill="{DIM}">{pid}</text>'
                 f'<text x="78" y="{y}" class="mono" fill="{TEXT}">ahmad</text>'
                 f'<text x="150" y="{y}" class="mono" font-weight="700" fill="{sc}">{st}</text>'
                 f'<text x="210" y="{y}" text-anchor="end" class="mono" fill="{TEXT}">{cpu}</text>'
                 f'<text x="252" y="{y}" text-anchor="end" class="mono" fill="{TEXT}">{mem}</text>'
                 f'<text x="268" y="{y}" class="mono"><tspan fill="{ACCENT}" font-weight="700">{t(name)}</tspan>'
                 f'<tspan fill="{DIM}"> {t(args)}</tspan></text></g>')
        assert len(cmd) <= 76, cmd
    # function-key bar = tech stack
    fy = h - 34
    x = 14
    for i, k in enumerate(FKEYS):
        key = f"F{i + 1}"
        kw = len(key) * 7.3 + 4
        lw = len(k) * 7.3 + 10
        p.append(f'<text x="{x}" y="{fy + 14}" class="mono" font-size="12" font-weight="700" fill="{TEXT}">{key}</text>'
                 f'<rect x="{x + kw:.0f}" y="{fy}" width="{lw:.0f}" height="19" fill="{ACCENT}" opacity=".9"/>'
                 f'<text x="{x + kw + 4:.0f}" y="{fy + 14}" class="mono" font-size="12" fill="{BG}">{t(k)}</text>')
        x += kw + lw + 6
    assert x < w, f"fkey bar overflow {x}"
    defs = (f'<defs><linearGradient id="bars" x1="0" x2="1"><stop offset="0" stop-color="{GREEN}"/>'
            f'<stop offset=".6" stop-color="{ACCENT}"/><stop offset="1" stop-color="{ACCENT2}"/></linearGradient></defs>')
    steps = len(PROCS)
    kf = "".join(f"{i * 100 / steps:.2f}%{{transform:translateY({i * row_h}px)}}" for i in range(steps))
    css = (".bar{transform-box:fill-box;transform-origin:left;transform:scaleX(0);"
           "animation:grow 1.1s cubic-bezier(.3,.8,.3,1) forwards}"
           "@keyframes grow{to{transform:scaleX(1)}}"
           f".sel{{animation:sel {steps * 1.6:.1f}s steps(1,end) 1.8s infinite}}"
           f"@keyframes sel{{{kf}100%{{transform:translateY(0)}}}}")
    write("skills.svg", svg(w, h, defs + "\n".join(p), css,
                            "htop-style skills: " + "; ".join(c for *_, c in PROCS)))


# ---------------------------------------------------------------- timeline
JOURNEY = [
    ("2024 — now", "Learner at 42 Amman", "Peer-to-peer, project-based",
     "Milestones 0–5 done: cub3D, minishell, webserv, pipex, push_swap, so_long and C++ 00–09."),
    ("2024", "1st place — RoboCraft Competition", "CodeForces Coach",
     "Led the build of an AI platform that adapts competitive-programming roadmaps to each user."),
    ("2024", "5th of 155 — Ramadan CP Marathon", "Al-3ahed Technology",
     "Held up under real time pressure against 155 competitors."),
    ("2023 — now", "CS student, Amman Arab University", "3.96 GPA · ICPC participant",
     "Algorithms, databases (ER/EER, SQL, normalization), software engineering."),
]


def timeline():
    w = 840
    item_h = 88
    h = 36 + item_h * len(JOURNEY)
    parts = [frame(w, h), f'<rect x="167" y="34" width="2" height="{h - 68}" fill="url(#sp)"/>']
    y = 36
    for i, (date, title, org, desc) in enumerate(JOURNEY):
        d = 0.2 + i * 0.25
        assert len(desc) <= 92, desc
        parts.append(
            f'<g class="rise" style="animation-delay:{d:.2f}s">'
            f'<text x="148" y="{y + 18}" text-anchor="end" class="mono" font-size="12" fill="{ACCENT}">{t(date)}</text>'
            f'<circle cx="168" cy="{y + 14}" r="6" fill="{BG}" stroke="{ACCENT}" stroke-width="2"/>'
            f'<circle class="dot" style="animation-delay:{d + .4:.2f}s" cx="168" cy="{y + 14}" r="2.5" fill="{ACCENT2}"/>'
            f'<text x="192" y="{y + 19}" class="sans" font-size="16" font-weight="700" fill="{TEXT}">{t(title)}</text>'
            f'<text x="192" y="{y + 39}" class="mono" font-size="12" fill="{FAINT}">{t(org)}</text>'
            f'<text x="192" y="{y + 60}" class="sans" font-size="13.5" fill="{DIM}">{t(desc)}</text></g>')
        y += item_h
    defs = (f'<defs><linearGradient id="sp" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="{ACCENT}" stop-opacity=".6"/>'
            f'<stop offset="1" stop-color="{ACCENT2}" stop-opacity=".2"/></linearGradient></defs>')
    css = ".dot{opacity:0;animation:fade .4s forwards,pulse 2.4s ease-in-out 2s infinite}"
    write("journey.svg", svg(w, h, defs + "\n".join(parts), css, "Experience & education: " + "; ".join(j[1] for j in JOURNEY)))


# ---------------------------------------------------------------- footer
def footer():
    w, h = 840, 64
    body = f"""<text x="420" y="38" text-anchor="middle" class="mono fade" font-size="14"><tspan fill="{GREEN}">$</tspan><tspan class="ts" fill="{DIM}"> make re &amp;&amp; ./always_compiling</tspan><tspan fill="{ACCENT}"> — let it rip.</tspan><tspan class="cursor" fill="{ACCENT}"> ▍</tspan></text>"""
    write("footer.svg", svg(w, h, body, LIGHT_CSS, "always compiling. let it rip."))


header()
section("01", "Things I've built", "42 projects, competition entries and team work — roughly in the order they got harder.", "title-projects.svg")
section("02", "What I know", "From memory management up to AI-driven systems.", "title-skills.svg")
section("03", "Experience & education", "Where the hours went.", "title-journey.svg")
section("04", "Contributions", "Regenerated every day by GitHub Actions from my real contribution data.", "title-activity.svg")
section("05", "Let's connect", "Open to junior backend / systems roles, internships and collaborative builds.", "title-contact.svg")

card("CodeForces Coach", "AI PLATFORM · SOLVEX",
     "AI-powered competitive-programming coach whose learning roadmaps adapt to each user's behaviour, "
     "hesitation and error patterns. Progressive hints, cheat detection, live Codeforces data.",
     ["React", "Express", "PostgreSQL", "Redis"], "card-coach.svg", award="🏆 1st · RoboCraft", delay=0.0)
card("ft_transcendence · Halaqa", "42 AMMAN · IN PROGRESS",
     "Collaborative study workspace: group chat, task boards and a RAG tutor over each group's files. "
     "I own the whole Spring Boot backend.",
     ["Spring Boot", "JPA", "OAuth2/JWT", "WebSocket"], "card-halaqa.svg", delay=0.15)
card("webserv", "42 AMMAN · TEAM OF 3",
     "HTTP/1.0 server in C++98: non-blocking epoll event loop, request parsing, CGI, uploads and "
     "an NGINX-style config.",
     ["C++98", "epoll", "sockets", "CGI"], "card-webserv.svg", delay=0.0)
card("minishell", "42 AMMAN",
     "A Bash-like shell from zero in C: tokenizer, quotes, pipes, every redirection, heredocs, "
     "$VAR expansion, signals and built-ins.",
     ["C", "fork/execve", "pipes", "signals"], "card-minishell.svg", delay=0.15)
card("cub3D", "42 AMMAN · TEAM OF 2",
     "Wolfenstein-style raycasting engine: DDA, textured walls, doors, sprites, minimap and "
     "flood-fill map validation.",
     ["C", "raycasting", "MiniLibX"], "card-cub3d.svg", delay=0.0)
card("philosophers", "42 AMMAN",
     "Dining philosophers with one thread per philosopher and one mutex per fork — deadlock-free "
     "by resource ordering, with a monitor thread.",
     ["C", "pthreads", "mutexes"], "card-philosophers.svg", delay=0.15)
skills()
timeline()
footer()
