"""Builds SC-200/article-lab/datatable/*.datatable.kql from queries/*.kql using the repository's generator.
Run from repo root:  python SC-200/article-lab/build_lab.py          (add --check to verify they are up to date)"""
import pathlib, sys
ROOT = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))
import build_datatable_queries as g

SRC = pathlib.Path(__file__).resolve().parent / "queries"
OUT = pathlib.Path(__file__).resolve().parent / "datatable"

def main(check=False):
    OUT.mkdir(exist_ok=True)
    ok = True
    for q in sorted(SRC.glob("*.kql")):
        target = OUT / (q.stem + ".datatable.kql")
        content = g.build(q)
        if check:
            ok &= target.exists() and target.read_text() == content
        else:
            target.write_text(content)
    return ok

if __name__ == "__main__":
    if "--check" in sys.argv:
        sys.exit(0 if main(check=True) else 1)
    main(); print("article-lab datatable queries written")
