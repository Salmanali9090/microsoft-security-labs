# Contributing

Thanks for helping make these labs better. Small, well-tested contributions are the most valuable.

## Ground rules
1. **Original work only.** Do not submit certification exam questions ("dumps"), copied Microsoft Learn text, or other authors' content. Explain concepts in your own words and link to official docs.
2. **Synthetic data only.** No real usernames, IPs, tenant IDs, company data or credentials. Use `contoso.example` and RFC 5737 IP ranges (`192.0.2.0/24`, `198.51.100.0/24`, `203.0.113.0/24`).
3. **Be honest about validation.** Use the labels in [docs/verification-matrix.md](docs/verification-matrix.md). Never write "tested in Sentinel" unless you actually did, and include how.
4. **Junior-friendly.** Explain what a query does, its assumptions and its limitations.

## Adding or changing a detection
1. Add `detections/NN_name.kql` with all header fields: `Name, Description, MITRE, Tables, Status, Assumptions, Limitations`.
2. If it needs new sample rows, edit `scripts/generate_sample_data.py` and re-run it.
3. Add a Python mirror in `tests/detection_logic.py` and tests in `tests/test_detections.py` (one malicious and one benign case).
4. Run `python scripts/build_datatable_queries.py` to regenerate learner queries.
5. Run `pytest -q` and the KQL parser check (`cd scripts/kql_check && npm install && node check.js`) – everything must pass.
6. Document the detection in `detections/README.md`.

## Pull requests
- One topic per PR; describe what you verified and how.
- Do not include secrets. The test-suite scans for common key patterns, but you are responsible too.
- By contributing you agree your work is licensed under the repository's MIT License.

## Reporting mistakes
Technical errors are welcome as issues. For security-sensitive reports see [SECURITY.md](SECURITY.md).
