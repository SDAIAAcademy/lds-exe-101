# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Run every solution of LDS-EXE-101 and print PASS or the first difference.

  uv run labs/solutions/run_all.py      (from the repository root; needs Node 22+ for lab 1.2)

1. The file pack is deterministic: the generator, run again, writes the same bytes.
2. Lab 1.1: the fallback figures recomputed from the CSV agree with the key, the stand-in draft
   carries the planted errors, and the reference claim sheet scores full marks.
3. Lab 1.2: the sandbox page's own agent, run under Node, fails exactly as the key says.
4. Lab 1.3: the reference sort and the reference questions meet the rule; the cost arithmetic.
"""
import csv
import hashlib
import importlib.util
import json
import subprocess
import sys
from pathlib import Path

SOL = Path(__file__).resolve().parent
LABS = SOL.parent
ROOT = LABS.parent


def load(name):
    spec = importlib.util.spec_from_file_location(name, SOL / f"{name}.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def digest():
    h = hashlib.sha256()
    for p in sorted(list((LABS / "files").rglob("*")) + [LABS / "tools" / "sandbox.html"] +
                    [SOL / n for n in ("key.json", "claim_sheet_reference.csv", "claims_sort_reference.csv",
                                       "questions_reference.csv", "briefing_reference.md")]):
        if p.is_file():
            h.update(p.relative_to(LABS).as_posix().encode())
            h.update(p.read_bytes())
    return h.hexdigest()


def main():
    before = digest()
    subprocess.run([sys.executable, str(LABS / "_tools" / "prepare_files.py")], check=True,
                   stdout=subprocess.DEVNULL)
    assert digest() == before, "the generator wrote different bytes: the pack is not deterministic"
    print("PASS file pack: deterministic (seed 101)")

    key = json.loads((SOL / "key.json").read_text(encoding="utf-8"))
    k1 = key["lab_1_1"]
    with open(LABS / "files" / "q3_certificates.csv", encoding="utf-8") as f:
        rows = list(csv.DictReader(f))
    total = sum(int(r["received"]) for r in rows)
    end = k1["opening"] + sum(int(r["received"]) - int(r["closed"]) for r in rows)
    late = [r["region"] for r in rows if r["month"] == "2026-09" and int(r["median_days_to_close"]) > 12]
    assert total == k1["total_received"] and end == k1["end_backlog_sep"], (total, end)
    assert round(100 * (end - k1["opening"]) / k1["opening"]) == k1["rise_pct"]
    assert late == k1["late_regions_sep"], late
    draft = (LABS / "files" / "assisted_draft_fallback.md").read_text(encoding="utf-8")
    assert f"{k1['draft_total']:,}" in draft and f"{k1['draft_rise_pct']}%" in draft
    assert f"{total:,}" not in draft
    v, d = load("score_claims").main()
    assert v == 12 and d == 12
    print(f"PASS lab 1.1: {total:,} received, {k1['opening']:,} to {end:,} open (+{k1['rise_pct']}%), "
          f"late in September: {', '.join(late)}; draft planted 3 wrong and 3 unverifiable claims")

    r = subprocess.run(["node", str(SOL / "check_sandbox.mjs")], capture_output=True, text=True, encoding="utf-8")
    sys.stdout.write(r.stdout)
    assert r.returncode == 0, r.stderr
    print("PASS lab 1.2")

    assert load("score_sort").main() == 10
    n, c, ok = load("score_questions").main()
    assert ok and n == 13 and c == 13
    cost = key["lab_1_3"]["cost"]
    per_app = cost["model_per_app"] + (1 - cost["auto_share"]) * cost["review_cost"]
    assert round(per_app, 2) == cost["per_app_with_review"]
    print(f"PASS lab 1.3: cost per application with review {per_app:.2f} SAR, "
          f"not {cost['model_per_app']} SAR")
    print("ALL PASS")


if __name__ == "__main__":
    main()
