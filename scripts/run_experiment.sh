#!/usr/bin/env bash
# Run the 15-term experiment with several local models and seeds (requires Ollama).
# Usage: scripts/run_experiment.sh TERMS_FILE [MODEL ...]
# Example: scripts/run_experiment.sh contexts_private/2024/terms_2024_run.json qwen2.5:7b-instruct llama3.1:8b-instruct-q4_K_M
set -euo pipefail
TERMS="${1:?terms file}"; shift
MODELS=("${@:-qwen2.5:7b-instruct}")
SEEDS=(${SEEDS:-1 2 3})
mkdir -p results evaluation
for model in "${MODELS[@]}"; do
  ollama pull "$model"
  for seed in "${SEEDS[@]}"; do
    tag="$(echo "$model" | tr ':/' '__')_seed${seed}"
    python -m gat0.cli --terms "$TERMS" --model "$model" --seed "$seed" --out "results/${tag}.jsonl"
    python -m gat0.to_sheet "results/${tag}.jsonl" "evaluation/sheet_${tag}.csv"
  done
done
echo "Done. Score the sheets in evaluation/ with evaluation/rubric.md, then run:"
echo "  python -m gat0.compare evaluation/sheet_*.csv"
