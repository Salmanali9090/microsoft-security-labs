# Verification matrix

## Labels
| Label | Meaning |
|---|---|
| ✅ **VERIFIED (automated)** | A script ran and the result is reproducible (command given) |
| 🧪 **SIMULATED** | Logic reproduced offline on synthetic data; not run in the real product |
| ⚠️ **UNTESTED IN TENANT** | Never executed against a live Microsoft cloud service |
| 📚 **CONCEPTUAL** | Educational text; accuracy depends on linked official docs |
| 🔗 **LINK NOT CHECKED** | URL not machine-verified (see [references](references.md)) |

## Status per artifact (as of 2026-10-16)
| Artifact | Status | How checked |
|---|---|---|
| `pytest -q` suite | ✅ | Run in the author's sandbox; CI re-runs on every push |
| Sample-data regeneration is deterministic | ✅ | `tests/test_repo_quality.py` |
| Synthetic-only data (domains, IPs) | ✅ | Automated scan in tests |
| No secret-like strings | ✅ (pattern-based, not exhaustive) | Automated scan in tests |
| Markdown relative links, code fences | ✅ | Automated |
| Datatable learner queries in sync with detections | ✅ | `build_datatable_queries.py --check` |
| Detections 01–06 logic | 🧪 | Python mirrors in `tests/detection_logic.py` |
| Detections 01–06 KQL execution | ⚠️ | **Not executed anywhere** – no Kusto/Log Analytics engine was available to the author's tooling; not run in a live Sentinel/Log Analytics workspace |
| KQL syntax (all 12 `.kql` files) | ✅ | Microsoft's open-source Kusto.Language parser via `scripts/kql_check` (parse only for `detections/`) |
| KQL semantics (6 learner `datatable` files) | ✅ | Same parser with analysis; schema is the embedded `datatable`. Real table schemas were **not** loaded, so column names in `detections/` are not machine-checked against Microsoft's schemas |
| Detection 06 operation name | ⚠️ | Substring match on purpose; confirm in your AzureActivity data |
| `main.bicep` | ✅ compile / ⚠️ deploy | `bicep build` OK, Bicep CLI 0.48.1, exit 0, no warnings; never deployed |
| Azure Policy JSON | 🧪 / ⚠️ | Structure test + offline simulator; never assigned in Azure |
| Conditional Access simulator | 🧪 | Teaching model, not Microsoft's engine |
| SC-900 / SC-500 guides | 📚 | Written from own understanding; verify against official study guides |
| Official URLs | 🔗 | Only those flagged "Source-checked" in references were read |

## How to upgrade a label honestly
Run the artifact in your own lab, capture screenshots/results under `docs/evidence/`, and edit the `Status` header and this table in the same pull request. Describe the environment (portal, workspace type, date).
