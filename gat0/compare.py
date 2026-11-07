"""Compare scored evaluation sheets with the 2024 baseline.

Usage:
    python -m gat0.compare evaluation/sheet_*.csv
Rows without a score are ignored.
"""

from __future__ import annotations

import csv
import json
import sys
from collections import defaultdict
from pathlib import Path

BASELINE = Path(__file__).resolve().parent.parent / "evaluation" / "baseline_2024.json"


def summarise(scores: list[float]) -> str:
    n = len(scores)
    if not n:
        return "no scored rows"
    ok = sum(s >= 0.5 for s in scores) / n * 100
    top = sum(s == 1.0 for s in scores) / n * 100
    return f"n={n}  mean={sum(scores) / n:.2f}  >=0.5: {ok:.1f}%  =1.0: {top:.1f}%"


def main(argv: list[str] | None = None) -> int:
    paths = [Path(p) for p in (argv if argv is not None else sys.argv[1:])]
    base = {r["term"]: r["score"] for r in json.loads(BASELINE.read_text(encoding="utf-8"))["results"]}
    print(f"{'2024 baseline (GPT-3.5)':<40} {summarise(list(base.values()))}")
    per_term = defaultdict(list)
    for path in paths:
        with path.open(encoding="utf-8") as f:
            rows = [r for r in csv.DictReader(f) if r["score_0_1"].strip()]
        scores = [float(r["score_0_1"]) for r in rows]
        print(f"{path.stem:<40} {summarise(scores)}")
        for r in rows:
            per_term[r["term"]].append(float(r["score_0_1"]))
    if per_term:
        print("\nPer term (mean of new runs vs 2024):")
        for term, b in base.items():
            new = per_term.get(term)
            if new:
                mean = sum(new) / len(new)
                print(f"  {term:<42} 2024={b:.2f}  new={mean:.2f}  diff={mean - b:+.2f}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
