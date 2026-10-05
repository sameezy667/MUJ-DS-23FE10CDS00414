"""
@file test_linguistic_fallback.py
@description Unit and integration tests for UniversalLinguisticEngine and GEC fallback rules
@module tests
"""

import pytest

from orto.core.linguistic_fallback import UniversalLinguisticEngine
from orto.core.syntax_engine import SyntaxEngine
from orto.critic.verifier import SymbolicCritic
from orto.pipeline import OrtoEngine


@pytest.fixture(scope="module")
def fallback_engine() -> UniversalLinguisticEngine:
    """Provides a singleton instance of UniversalLinguisticEngine."""
    return UniversalLinguisticEngine()


@pytest.fixture(scope="module")
def pipeline() -> OrtoEngine:
    """Provides an OrtoEngine initialized with offline fallback mode."""
    syntax = SyntaxEngine()
    critic = SymbolicCritic(syntax)
    return OrtoEngine(
        syntax_engine=syntax,
        critic=critic,
        enable_critic=True,
    )


def test_fallback_sva_intervening_phrase(pipeline: OrtoEngine) -> None:
    """Tests SVA across intervening prepositional phrases."""
    text = "The box of old vintage vinyl records were dropped by the movers."
    resp = pipeline.analyze(text)
    assert len(resp.edits) >= 1
    assert resp.corrected_text == "The box of old vintage vinyl records was dropped by the movers."
    assert any(e.errant_type == "R:VERB:SVA" and e.critic_verified for e in resp.edits)


def test_fallback_uncountable_mass_nouns(pipeline: OrtoEngine) -> None:
    """Tests correction of uncountable mass nouns with plural inflection."""
    text = "The goverment provides many informations to the public."
    resp = pipeline.analyze(text)
    assert "information" in resp.corrected_text
    assert "government" in resp.corrected_text
    assert all(e.critic_verified for e in resp.edits)


def test_fallback_homophones_and_confusables(pipeline: OrtoEngine) -> None:
    """Tests homophone replacement (Their -> There, your -> you're, etc.)."""
    text = "Their is no doubt that your welcome here."
    resp = pipeline.analyze(text)
    edits = {e.span.original_text: e.replacement for e in resp.edits}
    assert edits.get("Their") == "There"
    assert edits.get("your") == "you're"


def test_fallback_modal_and_base_verbs(pipeline: OrtoEngine) -> None:
    """Tests modal auxiliary + past verb discordance."""
    text = "He could went yesterday, but he didn't saw anything."
    resp = pipeline.analyze(text)
    edits = {e.span.original_text: e.replacement for e in resp.edits}
    assert edits.get("went") == "go"
    assert edits.get("saw") == "see"


def test_fallback_perfect_aspect_participle(pipeline: OrtoEngine) -> None:
    """Tests perfect aspect past participle concordance (have went -> have gone)."""
    text = "I have went there three times."
    resp = pipeline.analyze(text)
    assert resp.corrected_text == "I have gone there three times."
    assert len(resp.edits) == 1
    assert resp.edits[0].replacement == "gone"


def test_fallback_double_comparatives(pipeline: OrtoEngine) -> None:
    """Tests removal of double comparative markers."""
    text = "He is more taller than his brother."
    resp = pipeline.analyze(text)
    assert resp.corrected_text == "He is taller than his brother."


def test_fallback_prepositional_collocations(pipeline: OrtoEngine) -> None:
    """Tests idiomatic preposition correction (married with -> married to, arrive to -> arrive at)."""
    text = "She is married with a doctor and arrived to the airport."
    resp = pipeline.analyze(text)
    edits = {e.span.original_text: e.replacement for e in resp.edits}
    assert edits.get("with") == "to"
    assert edits.get("to") == "at"


def test_fallback_partitive_noun_number(pipeline: OrtoEngine) -> None:
    """Tests 'one of my friend' -> 'one of my friends'."""
    text = "One of my friend are coming today."
    resp = pipeline.analyze(text)
    edits = {e.span.original_text: e.replacement for e in resp.edits}
    assert edits.get("friend") == "friends"


def test_fallback_pronoun_capitalization(pipeline: OrtoEngine) -> None:
    """Tests standalone lowercase 'i' capitalization."""
    text = "can i help you with that"
    resp = pipeline.analyze(text)
    edits = {e.span.original_text: e.replacement for e in resp.edits}
    assert edits.get("can") == "Can"
    assert edits.get("i") == "I"
