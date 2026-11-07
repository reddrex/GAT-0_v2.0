"""Command-line interface.

Usage:
    python -m gat0.cli --terms examples/terms.json --model qwen2.5:7b-instruct --out results/run.jsonl

The terms file lists each term with the context files an expert selected for it:
    [{"term": "eyectivas", "contexts": ["contexts/eyectivas_1.txt", ...],
      "sources": ["Gutiérrez & Espinosa (2023: 2)", ...]}]
Context paths are resolved relative to the terms file.
"""

from __future__ import annotations

import argparse
import datetime as dt
import json
import sys
from pathlib import Path

from .pipeline import Config, DefinitionGenerator
from . import __version__


def load_terms(path: Path) -> list[dict]:
    entries = json.loads(path.read_text(encoding="utf-8"))
    for entry in entries:
        entry["context_texts"] = [
            (path.parent / ctx).read_text(encoding="utf-8") for ctx in entry["contexts"]
        ]
    return entries


def main(argv: list[str] | None = None, client=None) -> int:
    parser = argparse.ArgumentParser(description="Generate terminological definitions from expert-selected contexts.")
    parser.add_argument("--terms", type=Path, required=True, help="JSON file with terms and context paths")
    parser.add_argument("--model", required=True, help="Model name as known to the endpoint, e.g. qwen2.5:7b-instruct")
    parser.add_argument("--base-url", default="http://localhost:11434/v1", help="OpenAI-compatible endpoint (default: local Ollama)")
    parser.add_argument("--api-key", default="not-needed-for-local-models")
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--out", type=Path, required=True, help="Output JSONL file")
    args = parser.parse_args(argv)

    config = Config(model=args.model, base_url=args.base_url, api_key=args.api_key, seed=args.seed)
    generator = DefinitionGenerator(config, client=client)

    args.out.parent.mkdir(parents=True, exist_ok=True)
    started = dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds")
    with args.out.open("w", encoding="utf-8") as out:
        for entry in load_terms(args.terms):
            if not entry["context_texts"]:
                print(f"! {entry['term']}: no context files listed, skipped", file=sys.stderr)
                continue
            print(f"· {entry['term']}", file=sys.stderr)
            record = generator.run(entry["term"], entry["context_texts"])
            record["sources"] = entry.get("sources", [])
            record["run"] = {"started": started, "gat0_version": __version__}
            out.write(json.dumps(record, ensure_ascii=False) + "\n")
    print(f"Saved to {args.out}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
