"""Build the exact 2024 condition from the parsed corpus: one .txt per context and a
terms file usable by gat0.cli. Fixes parsing issues and maps citations to data/sources.json.

Usage: python scripts/build_2024_condition.py contexts_private/2024
"""
import json, sys
from pathlib import Path

root = Path(sys.argv[1])
P = lambda s: json.loads((root / f"{s}.json").read_text(encoding="utf-8"))["contexts"]

# term -> list of (source_key, pages, context_index_in_corpus); order follows the TFG (section 5.2)
PLAN = {
  "baby talk": ("baby_talk", [("lovon2020", "115-116", 0), ("marti2015", "101", 1)]),
  "cambio lingüístico": ("cambio_linguistico", [("contursi2008", "3", 0), ("contursi2008", "4", 1), ("contursi2008", "8", 2), ("bustos2006", "23", 3), ("bustos2006", "29", 4), ("bustos2006", "30", 5)]),
  "conductismo": ("conductismo", [("rubio_taylor", None, 0), ("martinperis2008", "«Conductismo»", 1), ("hernandezpina1977", "22-25", 2)]),
  "consonantización": ("consonantizacion", [("gutierrezrexach2016", "29-30", 0), ("guzman2004", "467-468", 2)]),
  "Dispositivo de Adquisición del Lenguaje": ("dispositivo_de_adquisicion_del_lenguaje", [("garayzabal2006", "7", 0), ("birchenall2014", "421-422", 1)]),
  "eyectivas": ("eyectivas", [("nercesian2021", "81", 0), ("nercesian2021", "94", 1), ("gutierrez_espinosa2023", "2", 2), ("gutierrez_espinosa2023", "3", 3), ("gutierrez_espinosa2023", "4", 4), ("gutierrez_espinosa2023", "5", 5)]),
  "helenismo": ("helenismo", [("quiros2012", "176", 0), ("andres2019", "34", 1)]),
  "homónimo": ("homonimo", [("campoy2010", "3-4", 0), ("valenzuela1993", "225-226", 1)]),
  "lingüística diacrónica": ("linguistica_diacronica", [("miranda2007", "15-16", 0), ("escandell2019", "79-80", 1)]),
  "oración dubitativa": ("oracion_dubitativa", [("mora1999", None, "mora"), ("rae2009", None, 8)]),
  "papel temático": ("papel_tematico", [("demonte1990", "116-117", 0), ("escandell2019", "182-183", 1)]),
  "pidginización": ("pidginizacion", [("parejo2000", "350", 0), ("martinperis2008", "«Pidgin»", 1)]),
  "presuposición pragmática": ("presuposicion_pragmatica", [("sentis2001", "122", 0), ("sentis2001", "128", 1), ("sentis2001", "142", 2), ("caamano2022", "144-145", 3)]),
  "sintaxis": ("sintaxis", [("rae2009", None, 0), ("zavadil2019", "15", 1), ("escandell2019", "165", 2)]),
  "verbo bivalente": ("verbo_bivalente", [("rae2009", None, 0), ("rae2009", None, 1)]),
}

terms = json.loads(Path("data/terms_2024.json").read_text(encoding="utf-8"))
out_dir = root / "texts"; out_dir.mkdir(exist_ok=True)
run, report = [], []
for t in terms:
    slug, plan = PLAN[t["term"]]
    ctx = P(slug)
    paths = []
    for n, (src, pages, idx) in enumerate(plan, start=1):
        if idx == "mora":  # the Mora quote contains its own numbered list; the parser split it
            text = " ".join(c["text"] + (f" ({c['citation']})" if c["citation"] and "López García" in c["citation"] else "") for c in ctx[:8])
            text = text.rsplit("” (Mora", 1)[0]
        else:
            text = ctx[idx]["text"]
        p = out_dir / f"{slug}_{n}.txt"
        p.write_text(text + "\n", encoding="utf-8")
        paths.append(f"texts/{p.name}")
        report.append((t["term"], n, src, pages, len(text.split())))
    run.append({"term": t["term"], "contexts": paths, "sources": [f"{s} ({pg})" if pg else s for s, pg, _ in plan]})
(root / "terms_2024_run.json").write_text(json.dumps(run, ensure_ascii=False, indent=2), encoding="utf-8")
for r in report: print(r)
