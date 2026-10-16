# Detections

Six KQL detections for Microsoft Sentinel / Defender data. Every file begins with metadata: **Name, Description, MITRE, Tables, Status, Assumptions, Limitations**.

| # | Detection | Table | MITRE | Status |
|---|---|---|---|---|
| 01 | [Password spray](01_password_spray.kql) | SigninLogs | T1110.003 | 🧪 SIMULATED |
| 02 | [Success after repeated failures](02_success_after_failures.kql) | SigninLogs | T1110, T1078.004 | 🧪 SIMULATED |
| 03 | [Privileged Entra role assignment](03_privileged_role_assignment.kql) | AuditLogs | T1098.003 | 🧪 SIMULATED |
| 04 | [Encoded PowerShell](04_encoded_powershell.kql) | DeviceProcessEvents | T1059.001, T1027 | 🧪 SIMULATED |
| 05 | [Azure RBAC assignment by unapproved caller](05_azure_rbac_assignment_unapproved.kql) | AzureActivity | T1098.003 | 🧪 SIMULATED |
| 06 | [AI service key regeneration](06_ai_service_key_regeneration.kql) | AzureActivity | T1098 (judgement) | 🧪 SIMULATED, operation name unconfirmed |

## What "SIMULATED" means here
The logic and thresholds were reproduced in Python (`tests/detection_logic.py`) and checked against synthetic data. The KQL itself has **not** been executed in a live Microsoft Sentinel tenant by the author. Table and column names follow Microsoft's published schemas ([SigninLogs](https://learn.microsoft.com/azure/azure-monitor/reference/tables/signinlogs), [AuditLogs](https://learn.microsoft.com/azure/azure-monitor/reference/tables/auditlogs), [AzureActivity](https://learn.microsoft.com/azure/azure-monitor/reference/tables/azureactivity), [DeviceProcessEvents](https://learn.microsoft.com/defender-xdr/advanced-hunting-deviceprocessevents-table)); confirm them in your workspace.

## Using a detection as a Sentinel analytics rule
1. Create a scheduled analytics rule and paste the query.
2. Set the run frequency and lookback so they match the `ago()` window (the files use 1 day for readability – production rules typically use shorter windows).
3. Map entities (Account, IP, Host) and MITRE tactics, test in a lab first, then tune.

## Learner versions
`SC-200/lab-queries/*.datatable.kql` are generated from these files with synthetic rows embedded, so you can run them anywhere without ingesting data. Regenerate with `python scripts/build_datatable_queries.py`.
