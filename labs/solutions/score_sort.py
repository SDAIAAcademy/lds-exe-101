# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Score the sort of the ten claims of lab 1.3.

  uv run labs/solutions/score_sort.py <claims_sort_sheet.csv>

One point per claim whose relevance matches the reference, and a note on each high-relevance
claim that was put low (the costly mistake).
"""
import csv
import sys
from pathlib import Path

REF = Path(__file__).with_name("claims_sort_reference.csv")


def load(path):
    with open(path, encoding="utf-8") as f:
        return {r[0].strip(): r[2].strip() for r in list(csv.reader(f))[1:] if r}


def main():
    ref = load(REF)
    got = load(sys.argv[1] if len(sys.argv) > 1 else REF)
    score = sum(1 for k, v in ref.items() if got.get(k) == v)
    print(f"sort {score}/{len(ref)}")
    for k, v in ref.items():
        if v == "عالية" and got.get(k) == "منخفضة":
            print(f"{k}: a high-relevance claim put low")
    return score


if __name__ == "__main__":
    main()
