"""Build stats.svg: all-time contributions and most used languages."""
import datetime, json, os, urllib.request

USER = "amirerfantim"
COLORS = {"Go": "#00ADD8", "Python": "#3776AB", "Rust": "#DEA584", "TypeScript": "#3178C6",
          "JavaScript": "#F1E05A", "Java": "#B07219", "Shell": "#89E051", "HTML": "#E34C26",
          "C": "#8b949e", "CSS": "#9B59B6", "Dockerfile": "#384D54", "PLpgSQL": "#336790"}
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
top = sorted(langs.items(), key=lambda kv: -kv[1])[:6]

created = int(gql('{user(login:"%s"){createdAt}}' % USER)["user"]["createdAt"][:4])
allc = 0
for y in range(created, datetime.date.today().year + 1):
    d = gql('{user(login:"%s"){contributionsCollection(from:"%d-01-01T00:00:00Z",to:"%d-12-31T23:59:59Z"){contributionCalendar{totalContributions}}}}' % (USER, y, y))
    allc += d["user"]["contributionsCollection"]["contributionCalendar"]["totalContributions"]

W, H = 880, 300
o = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" role="img" aria-label="{allc:,} contributions and most used languages">',
 '<defs><linearGradient id="bg" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#0d1117"/><stop offset="1" stop-color="#171a33"/></linearGradient>'
 '<linearGradient id="ac" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#36bcf7"/><stop offset="1" stop-color="#c471ed"/></linearGradient>'
 '<radialGradient id="gl" cx="0.2" cy="0.5" r="0.6"><stop offset="0" stop-color="#7c5cff" stop-opacity="0.28"/><stop offset="1" stop-color="#7c5cff" stop-opacity="0"/></radialGradient></defs>',
 '<style>text{font-family:-apple-system,Segoe UI,Helvetica,Arial,sans-serif}'
 '.big{font-size:84px;font-weight:800;fill:url(#ac)}.lab{font-size:15px;fill:#9aa4b2;letter-spacing:.5px}'
 '.h{font-size:12px;font-weight:700;fill:#8b949e;letter-spacing:2px}.nm{font-size:15px;fill:#e6edf3;font-weight:600}.pc{font-size:14px;fill:#9aa4b2}</style>',
 '<text x="48" y="64" class="h">ALL TIME</text>',
 f'<text x="44" y="158" class="big">{allc:,}</text>',
 '<text x="48" y="192" class="lab">contributions on GitHub</text>',
 '<line x1="400" y1="40" x2="400" y2="260" class="dv"/>',
 '<text x="440" y="64" class="h">MOST USED LANGUAGES</text>']
mx = top[0][1]
for i, (name, size) in enumerate(top):
    y = 100 + i * 31
    c = COLORS.get(name, "#8b949e")
    w = max(6, 300 * size / mx)
    o.append(f'<text x="440" y="{y+5}" class="nm">{name}</text>'
             f'<rect x="540" y="{y-6}" width="240" height="12" rx="6" class="tr"/>'
             f'<rect x="540" y="{y-6}" width="{240*size/mx:.0f}" height="12" rx="6" fill="{c}"/>'
             f'<text x="796" y="{y+5}" class="pc">{100*size/total:.0f}%</text>')
o.append('</svg>')
open("stats.svg", "w", encoding="utf-8").write("\n".join(o))
print(allc, top)
