"""Deterministically generates ALL synthetic sample data for this repository.
Nothing here is real telemetry. Domain: contoso.example (reserved), IPs: RFC 5737 documentation ranges."""
import base64, csv, json, pathlib

OUT = pathlib.Path(__file__).resolve().parents[1] / "sample-data"
ATTACKER = "203.0.113.10"   # TEST-NET-3 (documentation range)
CORP = "192.0.2.50"         # TEST-NET-1 (documentation range)
HOME_BOB = "192.0.2.20"

def signin():
    rows = [("TimeGenerated", "UserPrincipalName", "IPAddress", "ResultType", "AppDisplayName")]
    # Normal business-hours noise (successes, ResultType 0)
    for i, u in enumerate(["carol", "dave", "erin", "frank"]):
        rows.append((f"2026-01-10T07:{10+i}:00Z", f"{u}@contoso.example", CORP, "0", "Office 365"))
    # Phase 1: password spray 08:00-08:09 - 12 users, 16 failures (ResultType 50126)
    for i in range(12):
        rows.append((f"2026-01-10T08:0{i % 5}:1{i % 6}Z", f"user{i:02d}@contoso.example", ATTACKER, "50126", "Azure Portal"))
    for i in range(4):
        rows.append((f"2026-01-10T08:0{5 + i % 4}:4{i}Z", f"user{i:02d}@contoso.example", ATTACKER, "50126", "Azure Portal"))
    # Phase 2: targeted guessing against alice, then success
    for m in range(6):
        rows.append((f"2026-01-10T09:1{m}:00Z", "alice@contoso.example", ATTACKER, "50126", "Office 365"))
    rows.append(("2026-01-10T09:20:00Z", "alice@contoso.example", ATTACKER, "0", "Office 365"))
    # Benign look-alike: user mistypes twice then succeeds
    rows += [("2026-01-10T10:00:00Z", "bob@contoso.example", HOME_BOB, "50126", "Office 365"),
             ("2026-01-10T10:01:00Z", "bob@contoso.example", HOME_BOB, "50126", "Office 365"),
             ("2026-01-10T10:02:00Z", "bob@contoso.example", HOME_BOB, "0", "Office 365")]
    with open(OUT / "signinlogs_sample.csv", "w", newline="") as f:
        csv.writer(f).writerows(rows)

def audit():
    def rec(t, op, actor, target, role, cid):
        mp = [] if role is None else [{"displayName": "Role.DisplayName", "oldValue": "[]", "newValue": json.dumps(role)}]
        return {"TimeGenerated": t, "OperationName": op,
                "InitiatedBy": {"user": {"userPrincipalName": actor}},
                "TargetResources": [{"userPrincipalName": target, "modifiedProperties": mp}],
                "CorrelationId": cid}
    recs = [
        rec("2026-01-10T07:30:00Z", "Add member to role", "it.admin@contoso.example", "helpdesk.user@contoso.example", "Security Administrator", "11111111-0000-0000-0000-000000000001"),
        rec("2026-01-10T07:45:00Z", "Add member to role", "it.admin@contoso.example", "helpdesk.user@contoso.example", "Helpdesk Administrator", "11111111-0000-0000-0000-000000000002"),
        rec("2026-01-10T09:35:00Z", "Add member to role", "alice@contoso.example", "svc-backup@contoso.example", "Global Administrator", "11111111-0000-0000-0000-000000000003"),
        rec("2026-01-10T09:36:00Z", "Update user", "alice@contoso.example", "svc-backup@contoso.example", None, "11111111-0000-0000-0000-000000000004"),
    ]
    with open(OUT / "auditlogs_sample.jsonl", "w") as f:
        for r in recs:
            f.write(json.dumps(r) + "\n")

def device():
    payload = base64.b64encode("Write-Output 'synthetic-lab-payload-benign'".encode("utf-16-le")).decode()
    rows = [("TimeGenerated", "DeviceName", "AccountName", "FileName", "ProcessCommandLine", "InitiatingProcessFileName"),
            ("2026-01-10T08:30:00Z", "SYN-WKS-014", "alice", "powershell.exe", "powershell.exe -File C:\\Scripts\\backup.ps1", "taskeng.exe"),
            ("2026-01-10T09:00:00Z", "SYN-WKS-021", "carol", "pwsh.exe", "pwsh.exe -Command Get-Process", "explorer.exe"),
            ("2026-01-10T09:42:00Z", "SYN-WKS-014", "alice", "powershell.exe", f"powershell.exe -NoP -W Hidden -enc {payload}", "winword.exe"),
            ("2026-01-10T09:43:00Z", "SYN-WKS-014", "alice", "notepad.exe", "notepad.exe notes.txt", "explorer.exe")]
    with open(OUT / "deviceprocessevents_sample.csv", "w", newline="") as f:
        csv.writer(f).writerows(rows)

def activity():
    rows = [("TimeGenerated", "OperationNameValue", "ActivityStatusValue", "Caller", "CallerIpAddress", "ResourceGroup", "ResourceProviderValue"),
            ("2026-01-10T07:50:00Z", "MICROSOFT.AUTHORIZATION/ROLEASSIGNMENTS/WRITE", "Success", "it.admin@contoso.example", CORP, "rg-lab-prod", "MICROSOFT.AUTHORIZATION"),
            ("2026-01-10T09:50:00Z", "MICROSOFT.AUTHORIZATION/ROLEASSIGNMENTS/WRITE", "Success", "alice@contoso.example", ATTACKER, "rg-lab-prod", "MICROSOFT.AUTHORIZATION"),
            ("2026-01-10T09:55:00Z", "MICROSOFT.COGNITIVESERVICES/ACCOUNTS/REGENERATEKEY/ACTION", "Success", "alice@contoso.example", ATTACKER, "rg-lab-ai", "MICROSOFT.COGNITIVESERVICES"),
            ("2026-01-10T10:10:00Z", "MICROSOFT.STORAGE/STORAGEACCOUNTS/LISTKEYS/ACTION", "Success", "it.admin@contoso.example", CORP, "rg-lab-prod", "MICROSOFT.STORAGE")]
    with open(OUT / "azureactivity_sample.csv", "w", newline="") as f:
        csv.writer(f).writerows(rows)

def inventory():
    accounts = [
        {"name": "stlabcompliant01", "type": "Microsoft.Storage/storageAccounts", "properties": {"allowBlobPublicAccess": False, "minimumTlsVersion": "TLS1_2", "supportsHttpsTrafficOnly": True}},
        {"name": "stlabpublic02", "type": "Microsoft.Storage/storageAccounts", "properties": {"allowBlobPublicAccess": True, "minimumTlsVersion": "TLS1_2", "supportsHttpsTrafficOnly": True}},
        {"name": "stlabdefault03", "type": "Microsoft.Storage/storageAccounts", "properties": {"minimumTlsVersion": "TLS1_0", "supportsHttpsTrafficOnly": False}},
        {"name": "kvlab01", "type": "Microsoft.KeyVault/vaults", "properties": {}},
    ]
    (OUT / "resource_inventory.json").write_text(json.dumps({"_note": "SYNTHETIC inventory for offline policy simulation", "resources": accounts}, indent=2) + "\n")

if __name__ == "__main__":
    OUT.mkdir(exist_ok=True)
    signin(); audit(); device(); activity(); inventory()
    print("sample data written to", OUT)
