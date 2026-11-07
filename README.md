# GAT-0: generating terminological definitions from expert-selected contexts

GAT-0 generates Spanish terminological definitions with a large language model in two
stages: it first extracts the defining information about a term from a small set of
contexts, and then writes a definition following the classic pattern
**term = genus (hypernym) + differentiae**.

It accompanies the undergraduate dissertation *Aproximación a la generación automática de
definiciones terminológicas* (Jorge Zamora Rey, University of Cádiz, 2024; graded 10/10
with Honours), presented at the 41st International Conference of the Spanish Association
of Applied Linguistics (AESLA, 2024) and extended in *Context-Augmented Generation for
Automatic Term Definition in Low-Resource Domains* (Estudios Interlingüísticos, 14, in press).

## Design choice: humans choose the sources

Standard retrieval-augmented generation lets the system retrieve its own documents.
GAT-0 deliberately leaves **source selection to the terminologist**: automatic retrieval
risks favouring idiosyncratic, author-specific uses of a term over its accepted meaning,
and the experiments showed that output quality depended more on the quality of the
contexts than on the model itself.

```
expert-selected contexts ──► 1. extraction ──► defining information ──► 2. generation ──► definition
                                                                                              │
                                                    terminologist reviews and corrects ◄──────┘
```

## Reproducibility note (2026)

The 2024 experiments used a GPT-3.5-series model through OpenAI's legacy Completions API.
That model and API have since been retired, so **the original results cannot be exactly
reproduced**. The original script is kept unchanged in `legacy/` for the record; it does
not run as published (it contains a syntax error and, because of a misplaced `return`,
only passed the first context to the model).

Version 1.0 (this repository) is a cleaned-up reimplementation that:

- runs on **local open-weight models** through any OpenAI-compatible endpoint
  (Ollama, llama.cpp server, vLLM), so data never leaves the user's machine;
- keeps the prompts and sampling parameters described in the dissertation (§5.1);
- passes **all** contexts to the extraction stage;
- logs the model, parameters, seed and prompts with every definition, so each output can be traced.

Results obtained with open models are not expected to match the 2024 scores and should
be reported as a new run, not as a replication.

## Usage

```bash
pip install -r requirements.txt

# Local model with Ollama (https://ollama.com)
ollama pull qwen2.5:7b-instruct

python -m gat0.cli --terms examples/terms_example.json \
                   --model qwen2.5:7b-instruct \
                   --out results/example.jsonl

# Create a sheet for human evaluation with the 2024 rubric
python -m gat0.to_sheet results/example.jsonl evaluation/sheet_example.csv
```

A terms file lists each term, the context files an expert selected for it, and their sources:

```json
[{"term": "eyectivas",
  "contexts": ["contexts/eyectivas_1.txt", "contexts/eyectivas_2.txt"],
  "sources": ["Nercesian (2021: 81)", "Gutiérrez & Espinosa (2023: 2)"]}]
```

Any OpenAI-compatible endpoint can be used with `--base-url` (and `--api-key` if needed).

## Reproducing the 2024 experiment

```bash
# 1. Build the 15-term, 42-context input from the context corpus
python scripts/parse_corpus.py CORPUS_CONTEXTOS_TFG.md contexts_private/2024
python scripts/build_2024_condition.py contexts_private/2024

# 2. Run several local models and seeds (default seeds: 1 2 3)
scripts/run_experiment.sh contexts_private/2024/terms_2024_run.json qwen2.5:7b-instruct llama3.1:8b

# 3. Score each sheet in evaluation/ with the rubric, then compare with 2024
python -m gat0.compare evaluation/sheet_*.csv
```

`gat0.compare` reports, for each run, the mean score and the share of definitions scoring
0.5 or above and 1.0, next to the 2024 baseline, plus the per-term difference.

Notes on the reconstruction:

- The input matches the dissertation's table of sources and contexts (42 contexts).
- *consonantización*: the corpus holds four contexts, but the dissertation reports two
  (one per cited source). Contexts 1 (Gutiérrez-Rexach) and 3 (Guzmán Betancourt) are used.
- The dissertation gives a maximum of about 100 tokens per call, but the 2024 definitions
  are longer than that limit allows; the published script used 200 and 150. This version
  uses 300 (extraction) and 150 (generation).

## Data

- `data/terms_2024.json`: the 15 terms, their area and the exact source and pages of every
  context used in 2024.
- `data/sources.json`: full references for the 26 sources, with their type and licence.
- `evaluation/baseline_2024.json`: the definitions generated in 2024 and their scores,
  so new runs can be compared term by term.
- `examples/`: an illustrative context written for this repository, for a quick test.

Context texts are being restored (work in progress). Excerpts from openly licensed sources
will be included with their licence; short quotations from other sources will be included
only where the right of quotation for research purposes applies, and are **not covered by
this repository's Apache 2.0 licence**. Rights holders can request removal.

## Evaluation

`evaluation/rubric.md` describes the 0–1 rubric used in 2024 and reports its results:
87% of definitions scored 0.5 or above, and 27% achieved the maximum score. Errors
concentrated where sources were scarce or the concept itself is theoretically contested.

Known limitations: a single evaluator, 15 terms from a single domain, and no expert
evaluation. A pairwise comparison by a panel of terminologists is planned as future work.

## Tests

```bash
pip install pytest
python -m pytest
```

## Licence

Apache 2.0 (see `LICENSE`).
