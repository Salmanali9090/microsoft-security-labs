"""Python mirrors of the KQL detections in /detections, run on SYNTHETIC data in /sample-data.
They verify the LOGIC and thresholds. They do not prove the KQL executes in Microsoft Sentinel."""
import csv, json, pathlib, re
from collections import defaultdict
from datetime import datetime, timedelta

ROOT = pathlib.Path(__file__).resolve().parents[1]
S = ROOT / "sample-data"
FMT = "%Y-%m-%dT%H:%M:%SZ"

def _csv(name):
    with open(S / name, newline="") as f:
        rows = list(csv.DictReader(f))
    for r in rows:
        r["t"] = datetime.strptime(r["TimeGenerated"], FMT)
    return rows

def signin(): return _csv("signinlogs_sample.csv")
def device(): return _csv("deviceprocessevents_sample.csv")
def activity(): return _csv("azureactivity_sample.csv")
def audit():
    rows = [json.loads(l) for l in (S / "auditlogs_sample.jsonl").read_text().splitlines() if l.strip()]
    for r in rows:
        r["t"] = datetime.strptime(r["TimeGenerated"], FMT)
    return rows

def _bin(t, minutes=10):
    return t.replace(minute=t.minute - t.minute % minutes, second=0)

def password_spray(rows, min_users=8, min_fails=10):
    g = defaultdict(list)
    for r in rows:
        if r["ResultType"] == "50126":
            g[(r["IPAddress"], _bin(r["t"]))].append(r["UserPrincipalName"])
    return sorted((ip, b, len(u), len(set(u))) for (ip, b), u in g.items() if len(set(u)) >= min_users and len(u) >= min_fails)

def success_after_failures(rows, threshold=5, gap=timedelta(minutes=30)):
    fails = defaultdict(list)
    for r in rows:
        if r["ResultType"] == "50126":
            fails[(r["UserPrincipalName"], r["IPAddress"])].append(r["t"])
    hits = []
    for r in rows:
        k = (r["UserPrincipalName"], r["IPAddress"])
        if r["ResultType"] == "0" and len(fails[k]) >= threshold:
            last = max(fails[k])
            if r["t"] > last and r["t"] - last <= gap:
                hits.append((k[0], k[1], len(fails[k]), last, r["t"]))
    return hits

PRIV = {"Global Administrator", "Privileged Role Administrator", "Security Administrator", "Exchange Administrator"}
def privileged_role_assignment(rows):
    out = []
    for r in rows:
        if r["OperationName"] not in ("Add member to role", "Add eligible member to role"):
            continue
        tgt = r["TargetResources"][0]
        for prop in tgt["modifiedProperties"]:
            if prop["displayName"] == "Role.DisplayName":
                role = prop["newValue"].strip('"')
                if role in PRIV:
                    out.append((r["TimeGenerated"], r["InitiatedBy"]["user"]["userPrincipalName"], tgt["userPrincipalName"], role))
    return out

PS_RE = re.compile(r"(?i)\s-(e|ec|enc|encodedcommand)\s+[A-Za-z0-9+/=]{20,}")
def encoded_powershell(rows):
    return [(r["TimeGenerated"], r["DeviceName"], r["AccountName"]) for r in rows
            if r["FileName"].lower() in ("powershell.exe", "pwsh.exe") and PS_RE.search(r["ProcessCommandLine"])]

def rbac_unapproved(rows, approved=("it.admin@contoso.example",)):
    ok = {a.lower() for a in approved}
    return [(r["TimeGenerated"], r["Caller"], r["CallerIpAddress"]) for r in rows
            if r["OperationNameValue"].lower() == "microsoft.authorization/roleassignments/write"
            and r["ActivityStatusValue"].lower() in ("success", "succeeded") and r["Caller"].lower() not in ok]

def ai_key_regen(rows):
    return [(r["TimeGenerated"], r["Caller"], r["CallerIpAddress"]) for r in rows
            if r["ResourceProviderValue"].lower() == "microsoft.cognitiveservices"
            and "regeneratekey" in r["OperationNameValue"].lower()
            and r["ActivityStatusValue"].lower() in ("success", "succeeded")]
