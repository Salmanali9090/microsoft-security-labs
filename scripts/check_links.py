"""Run on a machine WITH internet access: reports HTTP status of every external link in *.md files."""
import pathlib, re, sys, urllib.request

ROOT = pathlib.Path(__file__).resolve().parents[1]
URL = re.compile(r"https?://[^\s)>\]\"']+")
bad = 0
seen = set()
for md in ROOT.rglob("*.md"):
    for u in URL.findall(md.read_text()):
        u = u.rstrip(".,")
        if u in seen:
            continue
        seen.add(u)
        try:
            req = urllib.request.Request(u, headers={"User-Agent": "link-check"})
            code = urllib.request.urlopen(req, timeout=15).status
        except Exception as e:
            code = str(e)
        flag = "OK " if code == 200 else "ERR"
        bad += flag == "ERR"
        print(flag, code, u, "(in", md.relative_to(ROOT), ")")
sys.exit(1 if bad else 0)
