import glob, pathlib, re, subprocess, sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
REQUIRED = ["// Name:", "// Description:", "// MITRE:", "// Tables:", "// Status:", "// Assumptions:", "// Limitations:"]

def test_every_detection_has_metadata_and_balanced_syntax():
    files = sorted(glob.glob(str(ROOT / "detections/*.kql")))
    assert len(files) == 6
    for fp in files:
        text = open(fp).read()
        for tag in REQUIRED:
            assert tag in text, f"{fp} missing {tag}"
        assert re.search(r"// Status: (SIMULATED|VERIFIED)", text)
        body = "\n".join(l for l in text.splitlines() if not l.startswith("//"))
        for a, b in ("()", "[]"):
            assert body.count(a) == body.count(b), f"{fp} unbalanced {a}{b}"

def test_no_detection_claims_live_tenant_validation():
    for fp in glob.glob(str(ROOT / "detections/*.kql")):
        status = [l for l in open(fp) if l.startswith("// Status:")][0]
        assert "NOT run in a live" in status or "NOT confirmed" in status or "NOT run" in status

def test_datatable_queries_are_in_sync_with_detections():
    r = subprocess.run([sys.executable, str(ROOT / "scripts/build_datatable_queries.py"), "--check"])
    assert r.returncode == 0, "run: python scripts/build_datatable_queries.py"

def test_sample_data_regenerates_identically(tmp_path):
    before = {p.name: p.read_bytes() for p in (ROOT / "sample-data").iterdir()}
    subprocess.run([sys.executable, str(ROOT / "scripts/generate_sample_data.py")], check=True, capture_output=True)
    after = {p.name: p.read_bytes() for p in (ROOT / "sample-data").iterdir()}
    assert before == after

SECRET_PATTERNS = [r"[0-9a-f]{64}", r"AKIA[0-9A-Z]{16}", r"-----BEGIN [A-Z ]*PRIVATE KEY-----", r"(?i)api[_-]?key\s*[:=]\s*['\"][^'\"]{8,}", r"sk-[A-Za-z0-9]{20,}"]
def _text_files():
    for p in ROOT.rglob("*"):
        if p.is_file() and ".git/" not in str(p) and "__pycache__" not in str(p) and ".pytest_cache" not in str(p) and p.suffix in {".md", ".py", ".kql", ".json", ".jsonl", ".csv", ".bicep", ".yml", ".txt"}:
            yield p

def test_no_secret_like_strings():
    for p in _text_files():
        t = p.read_text(errors="ignore")
        for pat in SECRET_PATTERNS:
            assert not re.search(pat, t), f"possible secret in {p}: {pat}"

def test_only_reserved_example_domains_and_documentation_ips_in_samples():
    for p in (ROOT / "sample-data").iterdir():
        t = p.read_text()
        for dom in re.findall(r"@([A-Za-z0-9.-]+)", t):
            assert dom.endswith(".example"), f"{p}: non-reserved domain {dom}"
        for ip in re.findall(r"\b(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})\b", t):
            assert ip.startswith(("192.0.2.", "198.51.100.", "203.0.113.")), f"{p}: non-documentation IP {ip}"

def test_markdown_relative_links_resolve_and_mermaid_fences_balanced():
    link = re.compile(r"\[[^\]]*\]\((?!https?://|#|mailto:)([^)#\s]+)")
    for md in ROOT.rglob("*.md"):
        text = md.read_text()
        assert text.count("```") % 2 == 0, f"unbalanced code fence in {md}"
        for target in link.findall(text):
            assert (md.parent / target).exists(), f"{md}: broken relative link {target}"

def test_required_top_level_files_exist():
    for name in ["README.md", "LICENSE", "CONTRIBUTING.md", "SECURITY.md", "SC-900/README.md", "SC-200/README.md", "SC-500/README.md",
                 "docs/architecture.md", "docs/references.md", "docs/verification-matrix.md", "docs/publishing-guide.md", "docs/glossary.md"]:
        assert (ROOT / name).exists(), name
