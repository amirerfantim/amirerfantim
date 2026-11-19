"""Build marquee.svg, banner-*.svg and footer-*.svg (run by hand, files are committed)."""
import base64, math, re, urllib.request

def get(url):
    import time
    for attempt in range(6):
        try:
            return urllib.request.urlopen(urllib.request.Request(url, headers={"User-Agent": "profile-build"}), timeout=30).read()
        except Exception:
            time.sleep(2 + attempt)
    raise SystemExit("could not fetch " + url)

b64 = lambda raw: base64.b64encode(raw).decode()
W = 880

# ---------- marquee ----------
ICONS_A = "go,py,rust,ts,bash,postgres,redis,mongodb,cassandra,rabbitmq,docker,kubernetes".split(",")
ICONS_B = "linux,git,gitlab,openstack,prometheus,grafana,pytorch,django,fastapi,react,nginx".split(",")
BADGES = [("NATS", "27AAE1", "natsdotio"), ("Helm", "0F1689", "helm"), ("Argo%20CD", "EF7B4D", "argo"),
          ("gRPC", "244C5A", "grpc"), ("Airflow", "017CEE", "apacheairflow"), ("pandas", "150458", "pandas"),
          ("NumPy", "013243", "numpy")]

def icon_item(name):
    return b64(get(f"https://skillicons.dev/icons?i={name}")), 48, 48

def badge_item(n, c, l):
    raw = get(f"https://img.shields.io/badge/{n}-{c}?style=for-the-badge&logo={l}&logoColor=white")
    w = int(float(re.search(rb'width="([\d.]+)"', raw).group(1)))
    h = int(float(re.search(rb'height="([\d.]+)"', raw).group(1)))
    return b64(raw), w, h

def row(items, y, rowh, gap, direction, dur):
    period = sum(w + gap for _, w, _ in items)
    copies = math.ceil((W + period) / period) + 1
    parts, x = [], 0
    for _ in range(copies):
        for data, w, h in items:
            parts.append(f'<image x="{x}" y="{y + (rowh - h) / 2:.0f}" width="{w}" height="{h}" href="data:image/svg+xml;base64,{data}"/>')
            x += w + gap
    frm, to = (0, -period) if direction < 0 else (-period, 0)
    return (f'<g><animateTransform attributeName="transform" type="translate" from="{frm} 0" to="{to} 0" dur="{dur}s" repeatCount="indefinite"/>'
            + "".join(parts) + "</g>")

A = [icon_item(n) for n in ICONS_A]
B = [icon_item(n) for n in ICONS_B]
C = [badge_item(*b) for b in BADGES]
H = 8 + 48 + 14 + 48 + 18 + 28 + 8
m = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" role="img" aria-label="Tools and technologies">',
     '<defs><linearGradient id="f" x1="0" x2="1"><stop offset="0" stop-color="#fff" stop-opacity="0"/><stop offset="0.1" stop-color="#fff"/>'
     '<stop offset="0.9" stop-color="#fff"/><stop offset="1" stop-color="#fff" stop-opacity="0"/></linearGradient>'
     f'<mask id="m"><rect width="{W}" height="{H}" fill="url(#f)"/></mask></defs><g mask="url(#m)">',
     row(A, 8, 48, 14, -1, 38), row(B, 70, 48, 14, 1, 34), row(C, 136, 28, 12, -1, 30), '</g></svg>']
open("marquee.svg", "w", encoding="utf-8").write("\n".join(m))

# ---------- banner + footer ----------
def wave(y, amp, period, phase=0):
    pts = [f"{x},{y + amp*math.sin(2*math.pi*(x+phase)/period):.1f}" for x in range(0, 2*W + 20, 20)]
    return "M" + " L".join(pts) + f" L{2*W+20},400 L0,400 Z"

def banner(dark):
    if dark:
        bg = ("#0d1117", "#1b1740", "#3b1d5a"); name = "#ffffff"; sub = "#b8c4d6"; w1, w2 = "#36bcf7", "#c471ed"
    else:
        bg = ("#e8f4ff", "#e9e4ff", "#f7dfff"); name = "#1f2328"; sub = "#57606a"; w1, w2 = "#36bcf7", "#c471ed"
    s = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="210" viewBox="0 0 {W} 210" role="img" aria-label="Amirerfan Teimouri">',
         f'<defs><linearGradient id="b" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="{bg[0]}"/><stop offset="0.55" stop-color="{bg[1]}"/><stop offset="1" stop-color="{bg[2]}"/></linearGradient>'
         '<clipPath id="c"><rect width="880" height="210" rx="14"/></clipPath></defs>',
         '<g clip-path="url(#c)"><rect width="880" height="210" fill="url(#b)"/>',
         f'<path d="{wave(168, 9, 440)}" fill="{w1}" fill-opacity="0.35"><animateTransform attributeName="transform" type="translate" from="0 0" to="-{W} 0" dur="14s" repeatCount="indefinite"/></path>',
         f'<path d="{wave(180, 8, 440, 110)}" fill="{w2}" fill-opacity="0.45"><animateTransform attributeName="transform" type="translate" from="-{W} 0" to="0 0" dur="18s" repeatCount="indefinite"/></path>',
         '</g>',
         f'<text x="440" y="96" text-anchor="middle" font-family="-apple-system,Segoe UI,Helvetica,Arial,sans-serif" font-size="46" font-weight="800" fill="{name}">Amirerfan Teimouri</text>',
         f'<text x="440" y="132" text-anchor="middle" font-family="\'Fira Code\',\'SF Mono\',ui-monospace,Menlo,Consolas,monospace" font-size="16" letter-spacing="1" fill="{sub}">Software Engineer  |  Researcher  |  Agentic AI</text>',
         '</svg>']
    return "\n".join(s)

def footer(dark):
    bg = ("#0d1117", "#3b1d5a") if dark else ("#e9e4ff", "#f7dfff")
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="90" viewBox="0 0 {W} 90"><defs><clipPath id="c"><rect width="880" height="90" rx="14"/></clipPath></defs>'
            f'<g clip-path="url(#c)"><path d="{wave(46, 7, 440)}" fill="#36bcf7" fill-opacity="0.35"><animateTransform attributeName="transform" type="translate" from="0 0" to="-{W} 0" dur="14s" repeatCount="indefinite"/></path>'
            f'<path d="{wave(58, 6, 440, 110)}" fill="#c471ed" fill-opacity="0.45"><animateTransform attributeName="transform" type="translate" from="-{W} 0" to="0 0" dur="18s" repeatCount="indefinite"/></path></g></svg>')

for d in (True, False):
    open(f"banner-{'dark' if d else 'light'}.svg", "w", encoding="utf-8").write(banner(d))
    open(f"footer-{'dark' if d else 'light'}.svg", "w", encoding="utf-8").write(footer(d))
print('ok')
