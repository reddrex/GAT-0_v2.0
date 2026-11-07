"""Run every condition in a conditions file over the same terms, with several seeds.

Usage:
    python -m gat0.experiment experiments/conditions.json
    python -m gat0.experiment experiments/conditions.json --only alia --seeds 1
    python -m gat0.experiment experiments/conditions.json --dry-run   # check config only

API keys are read from the environment variable named in each condition, never from the file.
Each run writes results/<condition>_seed<N>.jsonl and evaluation/sheet_<condition>_seed<N>.csv.
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path

from . import cli, to_sheet

LOCAL_KEY = "not-needed-for-local-models"


def load_conditions(path: Path) -> dict:
    spec = json.loads(path.read_text(encoding="utf-8"))
    names = [c["name"] for c in spec["conditions"]]
    if len(names) != len(set(names)):
        raise ValueError("condition names must be unique")
    return spec


def main(argv: list[str] | None = None, client_factory=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("conditions", type=Path)
    parser.add_argument("--only", nargs="*", help="run only these condition names")
    parser.add_argument("--seeds", nargs="*", type=int, help="override the seeds in the file")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args(argv)

    spec = load_conditions(args.conditions)
    base = args.conditions.parent
    terms = (base / spec["terms"]).resolve()
    seeds = args.seeds or spec.get("seeds", [1, 2, 3])
    conditions = [c for c in spec["conditions"] if not args.only or c["name"] in args.only]

    problems = []
    for c in conditions:
        key_var = c.get("api_key_env")
        if key_var and not os.environ.get(key_var):
            problems.append(f"{c['name']}: set the environment variable {key_var}")
        if c["model"].startswith("REPLACE"):
            problems.append(f"{c['name']}: fill in the model ID from your provider's catalogue")
    if not terms.exists():
        problems.append(f"terms file not found: {terms}")
    for c in conditions:
        print(f"· {c['name']:<12} {c['model']}  @ {c['base_url']}", file=sys.stderr)
    if problems:
        print("\n".join("! " + p for p in problems), file=sys.stderr)
        return 1
    if args.dry_run:
        print(f"OK: {len(conditions)} conditions x {len(seeds)} seeds on {terms}", file=sys.stderr)
        return 0

    for c in conditions:
        key = os.environ.get(c["api_key_env"], "") if c.get("api_key_env") else LOCAL_KEY
        for seed in seeds:
            out = Path("results") / f"{c['name']}_seed{seed}.jsonl"
            cli_args = ["--terms", str(terms), "--model", c["model"], "--base-url", c["base_url"],
                        "--api-key", key, "--seed", str(seed), "--out", str(out)]
            if not c.get("send_seed", True):
                cli_args.append("--no-seed")
            if not c.get("send_penalties", True):
                cli_args.append("--no-penalties")
            client = client_factory(c) if client_factory else None
            cli.main(cli_args, client=client, condition=c["name"])
            to_sheet.main([str(out), str(Path("evaluation") / f"sheet_{c['name']}_seed{seed}.csv")])
    print("Score the sheets with evaluation/rubric.md, then: python -m gat0.compare evaluation/sheet_*.csv",
          file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
