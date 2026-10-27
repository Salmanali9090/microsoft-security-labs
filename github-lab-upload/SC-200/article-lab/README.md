# Article lab – From security alerts to investigation (synthetic data)

Supporting lab for the Medium article *"From Security Alerts to Investigation: A Practical Microsoft Sentinel and KQL Walkthrough"* by Syed Salman Ali.
<!-- Add the public article URL here after publishing. -->

**Verification status – read first**
- Data: 100% synthetic (`sample-data/signinlogs_sample.csv`, reserved `contoso.example` domain, RFC 5737 documentation IPs).
- ✅ The three queries parse with Microsoft's open-source Kusto.Language parser (syntax for `queries/`, syntax + semantic for the self-contained `datatable/` versions).
- ✅ Python mirrors of the logic pass in `tests/test_article_lab.py`.
- ⚠️ **The KQL was not executed in a live Microsoft Sentinel workspace or any Kusto engine by the author.** The expected output below was produced by the Python mirror. If your run differs, trust your run and open an issue.

## The three steps
| Step | File | Question |
|---|---|---|
| 1 | `queries/01_noisy_ips.kql` | Which source IPs generate many failed sign-ins, how many accounts do they touch, and did any attempt succeed? |
| 2 | `queries/02_ip_successes.kql` | Which accounts did the suspect IP sign in to successfully? |
| 3 | `queries/03_account_timeline.kql` | What happened to that account, in order? |

`queries/` holds workspace-style queries for the **`SigninLogs`** table (Log Analytics / Microsoft Sentinel, time column `TimeGenerated`). `datatable/` holds copies with the synthetic rows embedded so you can run them without any real data.

## How to run without a Sentinel tenant
1. **Free Azure Data Explorer cluster (no Azure subscription needed, Microsoft account is enough):** see [Start for free](https://learn.microsoft.com/azure/data-explorer/start-for-free). Open the web UI, paste one file from `datatable/`, press **Run** (Shift+Enter). This runs KQL but is **not** Sentinel; `SigninLogs` here is a stand-in table created by `datatable`.
2. **Any Log Analytics query window** (Azure Monitor → Logs or Sentinel → Logs): paste a `datatable/` file; no tables are read.
3. **Offline:** `pip install -r requirements-dev.txt && pytest -q tests/test_article_lab.py`.

In a real workspace use the files in `queries/` instead. In Microsoft Defender's advanced hunting, Defender XDR tables use `Timestamp`; Sentinel workspace tables use `TimeGenerated`. Always check the schema of the surface you query.

## Expected output (from the Python mirror)
**Step 1 – `01_noisy_ips`** (one row; benign IPs `192.0.2.20` with 2 failures and `192.0.2.50` with 0 failures are excluded)

| IPAddress | Attempts | Failures | Successes | DistinctUsers | FirstSeen (UTC) | LastSeen (UTC) |
|---|---|---|---|---|---|---|
| 203.0.113.10 | 23 | 22 | 1 | 13 | 2026-01-10 08:00:10 | 2026-01-10 09:20:00 |

**Step 2 – `02_ip_successes`**

| TimeGenerated | UserPrincipalName | IPAddress | AppDisplayName |
|---|---|---|---|
| 2026-01-10 09:20:00 | alice@contoso.example | 203.0.113.10 | Office 365 |

**Step 3 – `03_account_timeline`** – 7 rows: six `50126` failures from 09:10 to 09:15, then one success (`0`) at 09:20, all from `203.0.113.10` to Office 365.

## How to interpret it
- 22 failures across 13 accounts from one IP is the shape of password spraying/guessing, not proof of intent. A shared office or VPN address could look similar.
- The same IP then succeeded for one account after repeated failures. That account is the priority, but it still needs corroboration (MFA result, Conditional Access outcome, what the session did).
- The queries cannot show who the actor is, whether MFA was satisfied, or post-sign-in activity.

## Turning it into a detection
See `detections/01_password_spray.kql` and `detections/02_success_after_failures.kql` for rule-style versions with thresholds. Before creating an analytics rule: match the lookback to the run frequency, map entities (Account, IP) so incidents can be investigated, tune thresholds with real baseline data, and add allowlists.

## Regenerate / validate
```bash
python SC-200/article-lab/build_lab.py          # rebuild datatable/ from queries/
python SC-200/article-lab/build_lab.py --check  # verify they are in sync
pytest -q
cd scripts/kql_check && npm install && node check.js
```
