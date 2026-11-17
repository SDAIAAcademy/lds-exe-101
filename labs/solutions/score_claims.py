# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Score a claim sheet of lab 1.1 (fallback task) against the reference.

  uv run labs/solutions/score_claims.py <claim_sheet.csv>

A row counts when its verdict matches; the decision mark is scored on its own. Rows are matched
by their number n (C1 or 1).
"""
import csv
import sys
from pathlib import Path

REF = Path(__file__).with_name("claim_sheet_reference.csv")


def load(path):
    with open(path, encoding="utf-8") as f:
        rows = list(csv.reader(f))
    out = {}
    for r in rows[1:]:
        if r and r[0].strip():
            out[r[0].strip().lstrip("Cc")] = [c.strip() for c in r]
    return out


def main():
    ref = load(REF)
    got = load(sys.argv[1] if len(sys.argv) > 1 else REF)
    verdict = sum(1 for n, r in ref.items() if n in got and got[n][3] == r[3])
    reaches = sum(1 for n, r in ref.items() if n in got and got[n][5] == r[5])
    missed = [f"C{n}" for n, r in ref.items() if n not in got or got[n][3] != r[3]]
    print(f"verdicts {verdict}/{len(ref)}, decision marks {reaches}/{len(ref)}")
    if missed:
        print("to review:", " ".join(missed))
    return verdict, reaches


if __name__ == "__main__":
    main()
