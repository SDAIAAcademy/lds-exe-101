# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Count the questions of lab 1.3 and the distinct reference criteria they match.

  uv run labs/solutions/score_questions.py <questions_sheet.csv>

The participant tags each question with a criterion code in step 4; the trainer confirms each tag
by reading the question. The script checks the rule: eight questions or more, six distinct
criteria or more. It does not judge the wording.
"""
import csv
import sys
from pathlib import Path

CODES = {"T1", "T2", "E1", "E2", "E3", "D1", "D2", "C1", "C2", "O1", "O2", "W1", "W2"}
REF = Path(__file__).with_name("questions_reference.csv")


def main():
    path = sys.argv[1] if len(sys.argv) > 1 else REF
    with open(path, encoding="utf-8") as f:
        rows = [r for r in list(csv.reader(f))[1:] if len(r) > 1 and r[1].strip()]
    codes = {r[-1].strip().upper() for r in rows if r[-1].strip().upper() in CODES}
    ok = len(rows) >= 8 and len(codes) >= 6
    print(f"questions {len(rows)}, distinct criteria {len(codes)}: {'meets' if ok else 'does not meet'} the rule (8 and 6)")
    return len(rows), len(codes), ok


if __name__ == "__main__":
    main()
