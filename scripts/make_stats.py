"""Build stats.svg: a few fixed facts plus live numbers from public repos."""
import json, os, urllib.request

USER = "amirerfantim"
COLORS = {"Go": "#00ADD8", "Python": "#3776AB", "Rust": "#DEA584", "TypeScript": "#3178C6",
          "JavaScript": "#F1E05A", "Java": "#B07219", "Shell": "#89E051", "HTML": "#E34C26",
          "CSS": "#9B59B6", "Dockerfile": "#384D54", "PLpgSQL": "#336790", "TSX": "#3178C6",
          "Makefile": "#427819", "Jupyter Notebook": "#DA5B0B"}


TOKEN = os.environ.get("STATS_TOKEN") or os.environ["GITHUB_TOKEN"]


def api(path):
    req = urllib.request.Request("https://api.github.com" + path, headers={
        "Authorization": "Bearer " + TOKEN, "Accept": "application/vnd.github+json"})
    return json.load(urllib.request.urlopen(req, timeout=60))


def gql(query):
    req = urllib.request.Request("https://api.github.com/graphql",
        data=json.dumps({"query": query}).encode(),
        headers={"Authorization": "Bearer " + TOKEN, "Content-Type": "application/json"})
    return json.load(urllib.request.urlopen(req, timeout=60))["data"]


repos = [r for r in api(f"/users/{USER}/repos?per_page=100&type=owner")
         if not r["fork"] and not r["private"]]
langs = {}
for r in repos:
    for k, v in api(f"/repos/{USER}/{r['name']}/languages").items():
        langs[k] = langs.get(k, 0) + v
total = sum(langs.values()) or 1
top = sorted(langs.items(), key=lambda kv: -kv[1])[:7]
created = int(gql('{user(login:"%s"){createdAt}}' % USER)["user"]["createdAt"][:4])
import datetime
now = datetime.datetime.utcnow()
allc = 0
for y in range(created, now.year + 1):
    d = gql('{user(login:"%s"){contributionsCollection(from:"%d-01-01T00:00:00Z",to:"%d-12-31T23:59:59Z"){contributionCalendar{totalContributions}}}}' % (USER, y, y))
    allc += d["user"]["contributionsCollection"]["contributionCalendar"]["totalContributions"]
d = gql('{user(login:"%s"){pullRequests{totalCount} contributionsCollection{contributionCalendar{totalContributions}}}}' % USER)
last12 = d["user"]["contributionsCollection"]["contributionCalendar"]["totalContributions"]
prs = d["user"]["pullRequests"]["totalCount"]
stars = sum(r["stargazers_count"] for r in repos)
fmt = lambda n: f"{n:,}"
facts = [(fmt(allc), "contributions, all time"), (fmt(last12), "contributions, last 12 months"),
         (fmt(prs), "pull requests"), (fmt(stars), "stars earned")]

W, H = 880, 330
out = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" role="img" aria-label="Stats">',
 '<defs><linearGradient id="bg" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#0d1117"/><stop offset="1" stop-color="#161b2e"/></linearGradient>'
 '<linearGradient id="ac" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="#36bcf7"/><stop offset="1" stop-color="#c471ed"/></linearGradient>'
 '<clipPath id="bar"><rect x="30" y="228" width="820" height="14" rx="7"/></clipPath></defs>',
 '<style>text{font-family:-apple-system,Segoe UI,Helvetica,Arial,sans-serif}'
 '.n{font-size:40px;font-weight:800;fill:url(#ac)}.l{font-size:13px;fill:#9aa4b2}.h{font-size:13px;font-weight:700;fill:#e6edf3;letter-spacing:1.5px}'
 '.k{font-size:12.5px;fill:#c9d1d9}.t{opacity:1}'
 '@keyframes f{to{opacity:1}}@keyframes g{from{transform:scaleX(0)}to{transform:scaleX(1)}}'
 '.s{transform-origin:30px 0;animation:g 1.2s ease-out both}</style>',
 f'<rect width="{W}" height="{H}" rx="16" fill="url(#bg)" stroke="#30363d"/>']
tw = (W - 60) / len(facts)
for i, (n, l) in enumerate(facts):
    x = 30 + i * tw
    out.append(f'<g class="t"><text x="{x+tw/2:.0f}" y="82" text-anchor="middle" class="n">{n}</text>'
               f'<text x="{x+tw/2:.0f}" y="108" text-anchor="middle" class="l">{l}</text></g>')
    if i:
        out.append(f'<line x1="{x:.0f}" y1="48" x2="{x:.0f}" y2="116" stroke="#30363d"/>')
out.append('<text x="30" y="178" class="h">MOST USED LANGUAGES (PUBLIC REPOS)</text>')
out.append('<g clip-path="url(#bar)"><g class="s">')
x = 30.0
for name, size in top:
    w = 820 * size / sum(s for _, s in top)
    out.append(f'<rect x="{x:.1f}" y="228" width="{w+1:.1f}" height="14" fill="{COLORS.get(name, "#8b949e")}"/>')
    x += w
out.append('</g></g>')
lx, ly = 30, 272
for name, size in top:
    pct = 100 * size / total
    out.append(f'<circle cx="{lx+5}" cy="{ly-4}" r="5" fill="{COLORS.get(name, "#8b949e")}"/>'
               f'<text x="{lx+16}" y="{ly}" class="k">{name} {pct:.0f}%</text>')
    lx += 16 + 8 * len(f"{name} {pct:.0f}%") + 22
    if lx > W - 120:
        lx, ly = 30, ly + 24
out.append('</svg>')
open("stats.svg", "w", encoding="utf-8").write("\n".join(out))
print(top)
