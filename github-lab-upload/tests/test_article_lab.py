"""Python mirrors for SC-200/article-lab queries, run on SYNTHETIC data. Verifies logic, not KQL execution."""
import subprocess, sys, pathlib
from collections import defaultdict
from datetime import datetime
import detection_logic as d

ROOT = pathlib.Path(__file__).resolve().parents[1]
ATT = "203.0.113.10"

def noisy_ips(rows, min_failures=5):
    g = defaultdict(list)
    for r in rows:
        g[r["IPAddress"]].append(r)
    out = []
    for ip, rs in g.items():
        failures = sum(r["ResultType"] == "50126" for r in rs)
        if failures >= min_failures:
            out.append({"IPAddress": ip, "Attempts": len(rs), "Failures": failures,
                        "Successes": sum(r["ResultType"] == "0" for r in rs),
                        "DistinctUsers": len({r["UserPrincipalName"] for r in rs}),
                        "FirstSeen": min(r["t"] for r in rs), "LastSeen": max(r["t"] for r in rs)})
    return sorted(out, key=lambda x: -x["Failures"])

def ip_successes(rows, ip):
    return [(r["TimeGenerated"], r["UserPrincipalName"], r["IPAddress"], r["AppDisplayName"])
            for r in rows if r["IPAddress"] == ip and r["ResultType"] == "0"]

def account_timeline(rows, user):
    rs = sorted((r for r in rows if r["UserPrincipalName"] == user), key=lambda r: r["t"])
    return [(r["TimeGenerated"], r["IPAddress"], r["AppDisplayName"], r["ResultType"],
             "Success" if r["ResultType"] == "0" else "Failure") for r in rs]

def test_noisy_ips_flags_only_the_attacker_and_shows_the_success():
    res = noisy_ips(d.signin())
    assert len(res) == 1
    r = res[0]
    assert (r["IPAddress"], r["Attempts"], r["Failures"], r["Successes"], r["DistinctUsers"]) == (ATT, 23, 22, 1, 13)
    assert r["FirstSeen"] == datetime(2026, 1, 10, 8, 0, 10) and r["LastSeen"] == datetime(2026, 1, 10, 9, 20, 0)

def test_benign_ips_not_flagged():
    ips = {r["IPAddress"] for r in noisy_ips(d.signin())}
    assert "192.0.2.20" not in ips and "192.0.2.50" not in ips   # bob mistyped twice; corp IP only succeeds

def test_ip_successes_one_account():
    assert ip_successes(d.signin(), ATT) == [("2026-01-10T09:20:00Z", "alice@contoso.example", ATT, "Office 365")]

def test_account_timeline_failures_then_success():
    tl = account_timeline(d.signin(), "alice@contoso.example")
    assert [x[4] for x in tl] == ["Failure"] * 6 + ["Success"]
    assert {x[1] for x in tl} == {ATT}
    assert tl[0][0] == "2026-01-10T09:10:00Z" and tl[-1][0] == "2026-01-10T09:20:00Z"

def test_article_lab_datatable_files_are_in_sync():
    r = subprocess.run([sys.executable, str(ROOT / "SC-200/article-lab/build_lab.py"), "--check"])
    assert r.returncode == 0, "run: python SC-200/article-lab/build_lab.py"

def test_article_lab_queries_have_metadata_and_honest_status():
    for fp in sorted((ROOT / "SC-200/article-lab/queries").glob("*.kql")):
        text = fp.read_text()
        for tag in ["// Name:", "// Description:", "// MITRE:", "// Tables: SigninLogs", "// Status: SIMULATED", "// Assumptions:", "// Limitations:"]:
            assert tag in text, f"{fp.name} missing {tag}"
        assert "NOT run in a live" in text
