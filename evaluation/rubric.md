# Evaluation rubric (2024)

Each generated definition is compared with a specialised linguistics dictionary
(Alcaraz Varó & Martínez Linares, 1997, except where noted in the dissertation)
and given a single score on a 0–1 scale. Two criteria are considered together:
conceptual delimitation and repetition/expression errors.

| Score | Conceptual delimitation | Repetition or expression errors |
|------:|-------------------------|---------------------------------|
| 1.00 | No key or complementary information from the dictionary is missing; anything missing was absent from the contexts | No repetition, no expression problems |
| 0.75 | No key or complementary information is missing; anything missing was absent from the contexts | At most one repetition and at most one expression error (e.g. terminological) |
| 0.50 | No key information is missing, but complementary information present in the contexts is | At most one repetition and/or more than one expression error |
| 0.25 | Part of the key information is present, but features needed to understand and delimit the term are missing | More than one repetition and/or expression error |
| 0.00 | Essential information about the term is wrong or false | More than one repetition and/or expression error |

Information missing from the definition is only penalised if it appeared in the
contexts given to the model: the system is judged on what it could have known.

## 2024 results (GPT-3.5 series, OpenAI API)

| Score | Terms |
|------:|-------|
| 1.00 | baby talk, conductismo, Dispositivo de Adquisición del Lenguaje, presuposición pragmática |
| 0.75 | consonantización, eyectivas, helenismo, oración dubitativa, papel temático, pidginización, sintaxis |
| 0.50 | cambio lingüístico, verbo bivalente |
| 0.25 | lingüística diacrónica |
| 0.00 | homónimo |

87% of definitions scored 0.5 or above; 27% achieved the maximum score.

## Known limitations

- A single evaluator (the author); no inter-annotator agreement.
- The planned pairwise evaluation by a panel of experts was not carried out.
- 15 terms from one domain (linguistics), in Spanish only.
