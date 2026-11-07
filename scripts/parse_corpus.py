"""Parse the 2024 context corpus (Markdown) into one JSON file per term.

Usage: python scripts/parse_corpus.py CORPUS.md OUTPUT_DIR
"""
import json, re, sys, unicodedata
from pathlib import Path

src, out = Path(sys.argv[1]), Path(sys.argv[2])
text = src.read_text(encoding="utf-8").replace("\\)", ")").replace("\\[", "[").replace("\\]", "]").replace("\\-", "-")
sections = re.split(r"^# \*\*(.+?)\*\*\s*$", text, flags=re.M)
out.mkdir(parents=True, exist_ok=True)

def slug(s):
    s = unicodedata.normalize("NFKD", s).encode("ascii", "ignore").decode().lower()
    return re.sub(r"[^a-z0-9]+", "_", re.sub(r"\(.*?\)", "", s)).strip("_")

summary = []
for title, body in zip(sections[1::2], sections[2::2]):
    block = body.split("## Contextos:", 1)[1]
    block = re.split(r"^\*\*[^*]+\*\*\s*$", block, flags=re.M)[0]  # stop at unused term headers
    items = re.split(r"^\s*\d+\)\s*", block, flags=re.M)
    contexts = []
    for item in items:
        item = re.sub(r"\s+", " ", item).strip()
        if not item:
            continue
        m = re.search(r"\(([^()]*\d{4}[^()]*)\)\s*$", item)
        citation = m.group(1).strip() if m else None
        body_text = item[: m.start()].strip() if m else item
        body_text = body_text.strip("“”\" ").strip()
        contexts.append({"text": body_text, "citation": citation})
    name = title.strip().lower()
    record = {"term_heading": title.strip(), "contexts": contexts}
    (out / f"{slug(name)}.json").write_text(json.dumps(record, ensure_ascii=False, indent=2), encoding="utf-8")
    summary.append((slug(name), len(contexts), [c["citation"] for c in contexts], [len(c["text"].split()) for c in contexts]))

for s in summary:
    print(s)
