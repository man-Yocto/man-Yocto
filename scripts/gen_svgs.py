"""Generate the animated profile SVGs (portfolio style) into <out_dir>.

usage: python scripts/gen_svgs.py assets
"""
import os
import sys
import textwrap
from xml.sax.saxutils import escape

OUT = sys.argv[1]
os.makedirs(OUT, exist_ok=True)

BG, RAISED, LINE = "#0b0d0e", "#111414", "#24282a"
TEXT, DIM, FAINT = "#e8e4dc", "#8b9296", "#565c5e"
AMBER, GREEN = "#ff9d2e", "#7ec699"
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


# ---------------------------------------------------------------- header
def header():
    w, h = 840, 300
    cmd = "whoami"
    cw = 9.6  # approx mono advance at 16px
    prompt = "ahmad@amman:~$ "
    px = 32 + len(prompt) * cw
    body = f"""{frame(w, h)}
<path d="M12.5 .5h815a12 12 0 0 1 12 12V38H.5V12.5a12 12 0 0 1 12-12z" fill="{RAISED}" stroke="{LINE}"/>
<circle cx="24" cy="19" r="6" fill="#ff5f57"/><circle cx="44" cy="19" r="6" fill="#febc2e"/><circle cx="64" cy="19" r="6" fill="#28c840"/>
<text x="420" y="24" text-anchor="middle" class="mono" font-size="12" fill="{FAINT}">ahmad@amman: ~</text>

<text x="32" y="78" class="mono" font-size="16"><tspan fill="{GREEN}">ahmad@amman</tspan><tspan fill="{DIM}">:</tspan><tspan fill="{AMBER}">~</tspan><tspan fill="{DIM}">$ </tspan><tspan fill="{TEXT}">{cmd}</tspan></text>
<rect class="typer" x="{px - 2:.0f}" y="62" width="{len(cmd) * cw + 6:.0f}" height="22" fill="{BG}"/>

<g class="fade" style="animation-delay:1.1s">
  <circle class="blip" cx="38" cy="117" r="4" fill="{GREEN}"/>
  <text x="50" y="121" class="mono" font-size="13" fill="{DIM}">Amman, Jordan — open to work</text>
</g>
<text x="32" y="172" class="sans rise" style="animation-delay:1.35s" font-size="40" font-weight="700" fill="{TEXT}">Ahmad Al-Khasawneh</text>
<text x="32" y="206" class="mono rise" style="animation-delay:1.6s" font-size="17" fill="{AMBER}">Software Engineer — Systems &amp; Backend</text>
<g class="sans fade" style="animation-delay:1.9s" font-size="14.5" fill="{DIM}">
  <text x="32" y="244">CS student at Amman Arab University and learner at 42 Amman. C/C++ close to the metal,</text>
  <text x="32" y="266">Spring Boot on the backend, heading toward embedded / edge AI.<tspan class="cursor" fill="{AMBER}"> ▍</tspan></text>
</g>"""
    css = (
        f".typer{{animation:type 1s steps({len(cmd)}) .25s forwards}}"
        f"@keyframes type{{to{{transform:translateX({len(cmd) * cw + 6:.0f}px)}}}}"
        ".blip{animation:pulse 1.6s ease-in-out infinite}"
    )
    write("header.svg", svg(w, h, body, css, "Ahmad Al-Khasawneh — Software Engineer, Systems & Backend"))


# ---------------------------------------------------------------- section titles
def section(num, title, sub, name):
    w, h = 840, 74
    body = f"""<g class="rise">
<text x="2" y="30" class="mono" font-size="13" fill="{AMBER}">{num}</text>
<text x="34" y="31" class="sans tt" font-size="24" font-weight="700" fill="{TEXT}">{t(title)}</text>
<text x="34" y="56" class="sans ts" font-size="14" fill="{DIM}">{t(sub)}</text>
</g>
<rect class="rule rl" x="2" y="71" width="836" height="1" fill="{LINE}"/>
<rect class="sweep" x="2" y="70" width="48" height="2" fill="{AMBER}"/>"""
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
        parts.append(f'<text x="{w - 22}" y="{y}" text-anchor="end" class="mono" font-size="11.5" fill="{AMBER}">{t(award)}</text>')
    y += 26
    for line in textwrap.wrap(body_text, 56):
        parts.append(f'<text x="22" y="{y}" class="sans" font-size="13" fill="{DIM}">{t(line)}</text>')
        y += 19
    # tags
    tx, ty = 22, h - 34
    for tag in tags:
        tw = len(tag) * 6.9 + 16
        parts.append(f'<rect x="{tx:.0f}" y="{ty}" width="{tw:.0f}" height="20" rx="4" fill="{RAISED}" stroke="{LINE}"/>'
                     f'<text x="{tx + tw / 2:.0f}" y="{ty + 14}" text-anchor="middle" class="mono" font-size="11" fill="{TEXT}">{t(tag)}</text>')
        tx += tw + 6
    assert tx < w, f"tags overflow on {name}"
    assert y < h - 40, f"body overflow on {name}: {y}"
    parts.append(f'<rect class="accent" x="0" y="12" width="3" height="{h - 24}" rx="1.5" fill="{AMBER}"/>')
    body = f'<g class="rise" style="animation-delay:{delay}s">' + "\n".join(parts) + "</g>"
    css = f".accent{{opacity:0;animation:fade .5s {delay + .5}s forwards}}"
    write(out, svg(w, h, body, css, f"{name} — {body_text}"))


# ---------------------------------------------------------------- skills
SKILLS = [
    ("Systems programming", "C and C++, UNIX process model, memory, IPC, file descriptors, Makefiles."),
    ("Backend & Spring Boot", "WebSocket, OAuth2/JWT, Spring Security, RBAC, JPA, Flyway, PostgreSQL."),
    ("Competitive programming", "Codeforces & LeetCode. 5th of 155 in a Ramadan CP marathon. ICPC participant."),
    ("AI & adaptive systems", "Platforms that adapt to user behaviour at runtime instead of a fixed script."),
    ("Tools & environment", "Linux daily driver, Git, shell scripting, Docker / Compose, GitHub Actions CI."),
]


def skills():
    w = 840
    row_h = 46
    h = 64 + row_h * len(SKILLS) + 16
    parts = [frame(w, h),
             f'<text x="28" y="40" class="mono" font-size="14"><tspan fill="{GREEN}">$</tspan><tspan fill="{TEXT}"> ls skills/</tspan></text>']
    y = 64
    for i, (name, desc) in enumerate(SKILLS):
        d = 0.25 + i * 0.15
        parts.append(
            f'<g class="rise" style="animation-delay:{d:.2f}s">'
            f'<rect x="20" y="{y}" width="{w - 40}" height="1" fill="{LINE}"/>'
            f'<text x="28" y="{y + 29}" class="mono" font-size="14" font-weight="600" fill="{TEXT}"><tspan fill="{AMBER}">▸ </tspan>{t(name)}</text>'
            f'<text x="300" y="{y + 29}" class="sans" font-size="13.5" fill="{DIM}">{t(desc)}</text></g>')
        assert len(desc) <= 80, desc
        y += row_h
    write("skills.svg", svg(w, h, "\n".join(parts), "", "What I know: " + "; ".join(f"{a} — {b}" for a, b in SKILLS)))


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
    parts = [frame(w, h), f'<rect class="spine" x="167" y="34" width="2" height="{h - 68}" fill="{LINE}"/>']
    y = 36
    for i, (date, title, org, desc) in enumerate(JOURNEY):
        d = 0.2 + i * 0.25
        assert len(desc) <= 92, desc
        parts.append(
            f'<g class="rise" style="animation-delay:{d:.2f}s">'
            f'<text x="148" y="{y + 18}" text-anchor="end" class="mono" font-size="12" fill="{AMBER}">{t(date)}</text>'
            f'<circle cx="168" cy="{y + 14}" r="6" fill="{BG}" stroke="{AMBER}" stroke-width="2"/>'
            f'<circle class="dot" style="animation-delay:{d + .4:.2f}s" cx="168" cy="{y + 14}" r="2.5" fill="{AMBER}"/>'
            f'<text x="192" y="{y + 19}" class="sans" font-size="16" font-weight="700" fill="{TEXT}">{t(title)}</text>'
            f'<text x="192" y="{y + 39}" class="mono" font-size="12" fill="{FAINT}">{t(org)}</text>'
            f'<text x="192" y="{y + 60}" class="sans" font-size="13.5" fill="{DIM}">{t(desc)}</text></g>')
        y += item_h
    css = ".dot{opacity:0;animation:fade .4s forwards,pulse 2.4s ease-in-out 2s infinite}"
    write("journey.svg", svg(w, h, "\n".join(parts), css, "Experience & education: " + "; ".join(j[1] for j in JOURNEY)))


# ---------------------------------------------------------------- footer
def footer():
    w, h = 840, 64
    body = f"""<text x="420" y="38" text-anchor="middle" class="mono fade" font-size="14"><tspan fill="{GREEN}">$</tspan><tspan class="ts" fill="{DIM}"> make re &amp;&amp; ./always_compiling</tspan><tspan fill="{AMBER}"> — let it rip.</tspan><tspan class="cursor" fill="{AMBER}"> ▍</tspan></text>"""
    write("footer.svg", svg(w, h, body, LIGHT_CSS, "always compiling. let it rip."))


header()
section("01", "Things I've built", "42 projects, competition entries and team work — roughly in the order they got harder.", "title-projects.svg")
section("02", "What I know", "From memory management up to AI-driven systems.", "title-skills.svg")
section("03", "Experience & education", "Where the hours went.", "title-journey.svg")
section("04", "Contributions", "Updated every day by GitHub Actions.", "title-activity.svg")
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
