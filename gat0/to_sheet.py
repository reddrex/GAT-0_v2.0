"""Turn a results JSONL into a CSV evaluation sheet using the 2024 rubric
(see evaluation/rubric.md). Scores are left empty for the human evaluator.

Usage:
    python -m gat0.to_sheet results/run.jsonl evaluation/sheet_run.csv
"""

from __future__ import annotations

import csv
import json
import sys
from pathlib import Path


def main(argv: list[str] | None = None) -> int:
    argv = argv if argv is not None else sys.argv[1:]
    src, dst = Path(argv[0]), Path(argv[1])
    rows = [json.loads(line) for line in src.read_text(encoding="utf-8").splitlines() if line.strip()]
    dst.parent.mkdir(parents=True, exist_ok=True)
    with dst.open("w", encoding="utf-8", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["term", "model", "definition", "reference_dictionary",
                         "score_0_1", "repetitions", "expression_errors", "missing_info_in_contexts", "notes"])
        for r in rows:
            writer.writerow([r["term"], r["config"]["model"], r["definition"], "", "", "", "", "", ""])
    print(f"{len(rows)} definitions written to {dst}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
