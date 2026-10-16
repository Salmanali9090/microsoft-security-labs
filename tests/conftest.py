import pathlib, sys
ROOT = pathlib.Path(__file__).resolve().parents[1]
for p in (ROOT / "tests", ROOT / "SC-900", ROOT / "SC-500" / "labs" / "01-governance-azure-policy"):
    sys.path.insert(0, str(p))
