import datetime, json, os, re, urllib.request

USER = "amirerfantim"
FEATURED = {"ichnos", "seath", "ChatbotHub", "Reviewfy"}
req = urllib.request.Request(
    f"https://api.github.com/users/{USER}/repos?sort=pushed&per_page=30&type=owner",
    headers={"Authorization": f"Bearer {os.environ['GITHUB_TOKEN']}",
             "Accept": "application/vnd.github+json"},
)
repos = json.load(urllib.request.urlopen(req))
rows = []
for r in repos:
    if r["fork"] or r["private"] or r["name"] == USER or r["archived"] or r["name"] in FEATURED or not (r["description"] or "").strip():
        continue
    day = r["pushed_at"][:10]
    if day < str(datetime.date.today() - datetime.timedelta(days=365)):
        continue
    desc = (r["description"] or "").strip()
    rows.append(f"- [{r['name']}]({r['html_url']}) — {desc} _(pushed {day})_")
    if len(rows) == 5:
        break

block = "<!--RECENT:START-->\n" + "\n".join(rows) + "\n<!--RECENT:END-->"
text = open("README.md", encoding="utf-8").read()
text = re.sub(r"<!--RECENT:START-->.*?<!--RECENT:END-->", block, text, flags=re.S)
open("README.md", "w", encoding="utf-8").write(text)
