import json
from types import SimpleNamespace

from gat0 import cli
from gat0.pipeline import Config, DefinitionGenerator, format_contexts


class FakeClient:
    """Records calls and returns canned answers, so tests need no model."""

    def __init__(self):
        self.calls = []
        self.chat = SimpleNamespace(completions=SimpleNamespace(create=self._create))

    def _create(self, **kwargs):
        self.calls.append(kwargs)
        text = "INFO" if len(self.calls) % 2 == 1 else "DEFINICIÓN"
        return SimpleNamespace(choices=[SimpleNamespace(message=SimpleNamespace(content=text))])


def test_all_contexts_reach_the_extraction_prompt():
    client = FakeClient()
    gen = DefinitionGenerator(Config(model="m"), client=client)
    gen.run("eyectivas", ["uno", "dos", "tres"])
    prompt = client.calls[0]["messages"][0]["content"]
    assert "[contexto 1] 'uno'" in prompt and "[contexto 3] 'tres'" in prompt


def test_stage_parameters_follow_the_dissertation():
    client = FakeClient()
    DefinitionGenerator(Config(model="m"), client=client).run("t", ["c"])
    extraction, generation = client.calls
    assert extraction["temperature"] == 0.3 and generation["temperature"] == 0.5
    assert extraction["top_p"] == 0.8 and generation["frequency_penalty"] == 0.5
    assert "INFO" in generation["messages"][0]["content"]


def test_format_contexts_numbers_from_one():
    assert format_contexts(["a"]).startswith("[contexto 1]")


def test_cli_writes_one_record_per_term_and_skips_empty(tmp_path):
    (tmp_path / "c.txt").write_text("contexto", encoding="utf-8")
    terms = tmp_path / "terms.json"
    terms.write_text(json.dumps([
        {"term": "a", "contexts": ["c.txt"], "sources": ["S"]},
        {"term": "b", "contexts": []},
    ]), encoding="utf-8")
    out = tmp_path / "out.jsonl"
    cli.main(["--terms", str(terms), "--model", "m", "--out", str(out)], client=FakeClient())
    records = [json.loads(l) for l in out.read_text(encoding="utf-8").splitlines()]
    assert [r["term"] for r in records] == ["a"]
    assert records[0]["definition"] == "DEFINICIÓN" and records[0]["sources"] == ["S"]
