"""
@file test_fewshot.py
@description Unit tests for Dynamic Few-Shot Exemplar Bank and Retrieval Engine
@module tests
"""

import pytest

from orto.fewshot.bank import FEW_SHOT_EXEMPLAR_BANK, Exemplar
from orto.fewshot.retriever import ExemplarRetriever


def test_few_shot_bank_integrity():
    """Verifies that all exemplars in the bank conform to schema and valid spans."""
    assert len(FEW_SHOT_EXEMPLAR_BANK) >= 6

    for ex in FEW_SHOT_EXEMPLAR_BANK:
        assert ex.id
        assert ex.errant_type.startswith(("R:", "M:", "U:"))
        assert 0 <= ex.start_char < ex.end_char <= len(ex.input_text)
        assert ex.input_text[ex.start_char : ex.end_char] == ex.original_text
        assert ex.linguistic_rule
        assert ex.explanation
        assert ex.counterfactual_example


def test_exemplar_retriever_sva_query():
    """Verifies that SVA queries retrieve SVA exemplars."""
    retriever = ExemplarRetriever()
    query = "The list of registered members are not verified."
    priors = {"subject_verb_pairs": [{"subject": {"text": "list"}, "verb": {"text": "are"}}]}

    retrieved = retriever.retrieve(query, syntax_priors=priors, k=2)
    assert len(retrieved) == 2
    assert any(ex.errant_type == "R:VERB:SVA" for ex in retrieved)


def test_exemplar_retriever_spelling_and_confusables():
    """Verifies that spelling and homophone queries retrieve corresponding exemplars."""
    retriever = ExemplarRetriever()
    query = "Their is no reason to worry about the results."

    retrieved = retriever.retrieve(query, k=2)
    assert len(retrieved) == 2
    assert any("their" in ex.original_text.lower() or ex.errant_type == "R:SPELL" for ex in retrieved)


def test_format_few_shot_prompt():
    """Verifies that formatted prompt contains structured markdown demonstration blocks."""
    retriever = ExemplarRetriever()
    query = "A unexpected error occured."
    prompt_str = retriever.format_few_shot_prompt(query, k=2)

    assert "### Pedagogical Reference Demonstrations" in prompt_str
    assert "Demonstration 1" in prompt_str
    assert "ERRANT Category:" in prompt_str
    assert "Counterfactual Minimal Pair:" in prompt_str
