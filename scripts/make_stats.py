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


cal = gql('{user(login:"%s"){contributionsCollection{contributionCalendar{weeks{contributionDays{contributionCount}}}}}}' % USER)
weeks = [sum(d["contributionCount"] for d in w["contributionDays"])
         for w in cal["user"]["contributionsCollection"]["contributionCalendar"]["weeks"]]

W, H = 880, 310
MONO = "'Fira Code','SF Mono',ui-monospace,Menlo,Consolas,monospace"
o = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" role="img" aria-label="{allc:,} contributions and most used languages">',
 '<defs><linearGradient id="ac" gradientUnits="userSpaceOnUse" x1="0" y1="0" x2="360" y2="0">'
 '<stop offset="0" stop-color="#36bcf7"/><stop offset="0.5" stop-color="#c471ed"/><stop offset="1" stop-color="#36bcf7"/>'
 '<animateTransform attributeName="gradientTransform" type="translate" from="-360 0" to="360 0" dur="6s" repeatCount="indefinite"/></linearGradient>'
 '<linearGradient id="bar" x1="0" y1="1" x2="0" y2="0"><stop offset="0" stop-color="#36bcf7"/><stop offset="1" stop-color="#c471ed"/></linearGradient></defs>',
 '<style>'
 f'text{{font-family:{MONO}}}'
 '.big{font-size:78px;font-weight:700;fill:url(#ac)}'
 '.cap{font-size:12px;fill:#768390;letter-spacing:3px;font-weight:600}'
 '.lab{font-size:14px;fill:#768390}'
 '.nm{font-size:14px;fill:#768390;font-weight:700}.pc{font-size:13px;fill:#768390}'
 '.w{transform-box:fill-box;transform-origin:bottom;animation:up 1s cubic-bezier(.2,.8,.2,1) both}'
 '.l{transform-box:fill-box;transform-origin:left;animation:right 1.1s cubic-bezier(.2,.8,.2,1) both}'
 '@keyframes up{from{transform:scaleY(0)}to{transform:scaleY(1)}}'
 '@keyframes right{from{transform:scaleX(0)}to{transform:scaleX(1)}}'
 '.dot{animation:pulse 2.4s ease-in-out infinite}@keyframes pulse{50%{opacity:.35}}'
 '</style>',
 '<circle class="dot" cx="52" cy="46" r="4" fill="#3fb950"/>',
 '<text x="66" y="51" class="cap">ALL-TIME CONTRIBUTIONS</text>',
 f'<text x="44" y="136" class="big">{allc:,}</text>',
 '<text x="48" y="162" class="lab">commits, pull requests, reviews, issues</text>']
mxw = max(weeks) or 1
bw = 360 / len(weeks)
for i, v in enumerate(weeks):
    h = max(2, 70 * v / mxw)
    o.append(f'<rect class="w" style="animation-delay:{i*0.018:.2f}s" x="{48+i*bw:.1f}" y="{250-h:.1f}" width="{bw-1.6:.1f}" height="{h:.1f}" rx="1.5" fill="url(#bar)" fill-opacity="{0.35+0.65*v/mxw:.2f}"/>')
o.append('<text x="48" y="278" class="lab" style="font-size:11px">last 12 months, per week</text>')
o.append('<line x1="440" y1="40" x2="440" y2="270" stroke="#8b949e" stroke-opacity="0.35"/>')
o.append('<text x="480" y="51" class="cap">MOST USED LANGUAGES</text>')
mx = top[0][1]
for i, (name, size) in enumerate(top):
    y = 94 + i * 35
    c = COLORS.get(name, "#8b949e")
    o.append(f'<text x="480" y="{y+5}" class="nm">{name}</text>'
             f'<rect x="580" y="{y-6}" width="220" height="12" rx="6" fill="#8b949e" fill-opacity="0.25"/>'
             f'<rect class="l" style="animation-delay:{0.2+i*0.12:.2f}s" x="580" y="{y-6}" width="{max(8, 220*size/mx):.0f}" height="12" rx="6" fill="{c}"/>'
             f'<text x="816" y="{y+5}" class="pc">{100*size/total:.0f}%</text>')
o.append('</svg>')
open("stats.svg", "w", encoding="utf-8").write("\n".join(o))
print(allc, top)
