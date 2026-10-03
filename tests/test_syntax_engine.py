"""
@file test_syntax_engine.py
@description Unit tests for spaCy syntax engine and feature extraction
@module tests
"""

import pytest
from orto.core.syntax_engine import SyntaxEngine


@pytest.fixture(scope="module")
def syntax_engine() -> SyntaxEngine:
    """Provides a shared SyntaxEngine instance."""
    return SyntaxEngine()


def test_parse_returns_spacy_doc(syntax_engine: SyntaxEngine) -> None:
    """Tests that parse produces a valid spaCy Doc."""
    doc = syntax_engine.parse("The quick brown fox jumps over the lazy dog.")
    assert len(doc) > 0
    assert doc[0].text == "The"
    assert doc[-1].text == "."


def test_extract_dependency_triples(syntax_engine: SyntaxEngine) -> None:
    """Tests directed Universal Dependency edge extraction."""
    doc = syntax_engine.parse("The scientist conducted a series of experiments.")
    triples = syntax_engine.extract_dependency_triples(doc)

    assert len(triples) == len(doc)
    # Check that root verb exists
    root_triples = [t for t in triples if t["dep"] == "ROOT"]
    assert len(root_triples) == 1
    assert root_triples[0]["child_text"] == "conducted"

    # Check nominal subject
    nsubj_triples = [t for t in triples if t["dep"] == "nsubj"]
    assert len(nsubj_triples) >= 1
    assert nsubj_triples[0]["child_text"] == "scientist"


def test_extract_sva_pairs(syntax_engine: SyntaxEngine) -> None:
    """Tests extraction of subject-verb agreement candidate nodes."""
    text = "The box of vintage vinyl records was dropped."
    doc = syntax_engine.parse(text)
    sva_pairs = syntax_engine.extract_sva_pairs(doc)

    assert len(sva_pairs) > 0
    first_pair = sva_pairs[0]
    assert first_pair["subject"]["text"] == "box"
    assert first_pair["subject"]["number"] == "Sing"
    assert first_pair["verb"]["text"] == "was"
    assert first_pair["verb"]["number"] == "Sing"


def test_extract_priors_structure(syntax_engine: SyntaxEngine) -> None:
    """Tests the structured priors dictionary serialization."""
    text = "The committee discusses the proposal."
    priors = syntax_engine.extract_priors(text)

    assert "sentence_length" in priors
    assert "key_dependencies" in priors
    assert "subject_verb_pairs" in priors
    assert "anomalies" in priors
    assert isinstance(priors["key_dependencies"], list)
