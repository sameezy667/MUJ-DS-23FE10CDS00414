"""
@file test_pipeline.py
@description Integration tests for end-to-end OrtoEngine pipeline
@module tests
"""

import pytest
from orto.core.syntax_engine import SyntaxEngine
from orto.critic.verifier import SymbolicCritic
from orto.llm.client import LLMClient
from orto.pipeline import OrtoEngine


@pytest.fixture(scope="module")
def engine() -> OrtoEngine:
    """Provides an OrtoEngine initialized with mock/deterministic offline client."""
    syntax_engine = SyntaxEngine()
    client = LLMClient(mock_mode=True)
    critic = SymbolicCritic(syntax_engine)
    return OrtoEngine(
        syntax_engine=syntax_engine,
        llm_client=client,
        critic=critic,
        enable_critic=True,
        max_refinements=1,
    )


def test_pipeline_empty_input(engine: OrtoEngine) -> None:
    """Tests that empty or whitespace strings return empty edits cleanly."""
    resp = engine.analyze("")
    assert resp.original_text == ""
    assert resp.corrected_text == ""
    assert len(resp.edits) == 0

    resp_spaces = engine.analyze("   \n\t  ")
    assert len(resp_spaces.edits) == 0


def test_pipeline_sva_intervening_preposition(engine: OrtoEngine) -> None:
    """Tests end-to-end SVA correction across an intervening prepositional phrase."""
    text = "The box of old vintage vinyl records were dropped by the movers."
    resp = engine.analyze(text)

    assert len(resp.edits) == 1
    edit = resp.edits[0]
    assert edit.errant_type == "R:VERB:SVA"
    assert edit.span.original_text == "were"
    assert edit.replacement == "was"
    assert edit.critic_verified is True
    assert resp.corrected_text == "The box of old vintage vinyl records was dropped by the movers."
    assert resp.telemetry is not None
    assert resp.telemetry.latency_ms > 0


def test_pipeline_spelling_corrections(engine: OrtoEngine) -> None:
    """Tests end-to-end multi-token orthographic corrections."""
    text = "She will definately recieve the package untill Friday."
    resp = engine.analyze(text)

    assert len(resp.edits) == 3
    assert resp.corrected_text == "She will definitely receive the package until Friday."
    for edit in resp.edits:
        assert edit.errant_type == "R:SPELL"
        assert edit.critic_verified is True


def test_pipeline_already_correct_sentence(engine: OrtoEngine) -> None:
    """Tests that a clean grammatical sentence produces zero edits."""
    text = "The team of experienced research scientists has published their findings."
    resp = engine.analyze(text)

    assert len(resp.edits) == 0
    assert resp.corrected_text == text


def test_pipeline_temporal_discordance(engine: OrtoEngine) -> None:
    """Tests that a future time adverbial paired with past tense verbs is reconciled."""
    text = "tomorrow i went to the mall and bought a bag"
    resp = engine.analyze(text)

    assert resp.corrected_text == "Yesterday I went to the mall and bought a bag"
    edits = {e.span.original_text: e.replacement for e in resp.edits}
    assert edits["tomorrow"] == "Yesterday"
    assert edits["i"] == "I"


def test_pipeline_modal_auxiliary_and_pronoun(engine: OrtoEngine) -> None:
    """Tests that modal auxiliary past tense error and pronoun casing are repaired."""
    text = "can i went to the cleaners"
    resp = engine.analyze(text)

    assert resp.corrected_text == "Can I go to the cleaners"
    edits = {e.span.original_text: e.replacement for e in resp.edits}
    assert edits["can"] == "Can"
    assert edits["i"] == "I"
    assert edits["went"] == "go"

