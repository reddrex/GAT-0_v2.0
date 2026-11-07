"""Two-stage pipeline: (1) extract defining information from expert-selected
contexts, (2) generate a definition following "term = genus + differentiae".

Prompts and sampling parameters follow the 2024 dissertation (Zamora Rey, 2024,
section 5.1). The model is reached through any OpenAI-compatible endpoint, so it
can run on a local open-weight model (Ollama, llama.cpp server, vLLM) instead of
a proprietary API.
"""

from __future__ import annotations

from dataclasses import dataclass, field, asdict

EXTRACTION_PROMPT = (
    'Extrae la información más relevante de cada contexto sobre "qué es {term}" '
    "en los siguientes contextos, si no te ofrece información sobre qué es o sus "
    "características, no prestes atención al contexto:\n{contexts}"
)

GENERATION_PROMPT = (
    "Utilizando solo la información necesaria de la que te voy a proporcionar, "
    'debes elaborar una definición propia del término "{term}", siguiendo la '
    "siguiente fórmula: Término = hiperónimo + características distintivas. "
    'Por ejemplo, "Las eyectivas son [hiperónimo] [características distintivas]". '
    "La información comienza aquí: {info}"
)


@dataclass
class StageParams:
    temperature: float
    max_tokens: int = 100
    top_p: float = 0.8
    frequency_penalty: float = 0.5
    presence_penalty: float = 0.5


@dataclass
class Config:
    model: str
    base_url: str = "http://localhost:11434/v1"  # Ollama default
    api_key: str = "not-needed-for-local-models"
    extraction: StageParams = field(default_factory=lambda: StageParams(temperature=0.3, max_tokens=300))
    generation: StageParams = field(default_factory=lambda: StageParams(temperature=0.5, max_tokens=150))
    seed: int | None = 42


def format_contexts(contexts: list[str]) -> str:
    """Number contexts from 1, as in the dissertation."""
    return "\n".join(
        f"[contexto {i}] '{text.strip()}' [fin contexto {i}]"
        for i, text in enumerate(contexts, start=1)
    )


class DefinitionGenerator:
    def __init__(self, config: Config, client=None):
        self.config = config
        if client is None:
            from openai import OpenAI

            client = OpenAI(base_url=config.base_url, api_key=config.api_key)
        self.client = client

    def _complete(self, prompt: str, params: StageParams) -> str:
        kwargs = dict(
            model=self.config.model,
            messages=[{"role": "user", "content": prompt}],
            temperature=params.temperature,
            max_tokens=params.max_tokens,
            top_p=params.top_p,
            frequency_penalty=params.frequency_penalty,
            presence_penalty=params.presence_penalty,
        )
        if self.config.seed is not None:
            kwargs["seed"] = self.config.seed
        response = self.client.chat.completions.create(**kwargs)
        return (response.choices[0].message.content or "").strip()

    def extract(self, term: str, contexts: list[str]) -> tuple[str, str]:
        # All contexts go into a single prompt (the 2024 script returned
        # inside the loop and only ever used the first context).
        prompt = EXTRACTION_PROMPT.format(term=term, contexts=format_contexts(contexts))
        return prompt, self._complete(prompt, self.config.extraction)

    def generate(self, term: str, info: str) -> tuple[str, str]:
        prompt = GENERATION_PROMPT.format(term=term, info=info)
        return prompt, self._complete(prompt, self.config.generation)

    def run(self, term: str, contexts: list[str]) -> dict:
        extraction_prompt, info = self.extract(term, contexts)
        generation_prompt, definition = self.generate(term, info)
        return {
            "term": term,
            "definition": definition,
            "extracted_info": info,
            "n_contexts": len(contexts),
            "prompts": {"extraction": extraction_prompt, "generation": generation_prompt},
            "config": {
                "model": self.config.model,
                "base_url": self.config.base_url,
                "seed": self.config.seed,
                "extraction": asdict(self.config.extraction),
                "generation": asdict(self.config.generation),
            },
        }
