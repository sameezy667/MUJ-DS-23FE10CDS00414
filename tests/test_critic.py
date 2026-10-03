"""
@file test_critic.py
@description Unit tests for symbolic morphosyntactic verifier and SVA assertions
@module tests
"""

import pytest
from orto.core.syntax_engine import SyntaxEngine
from orto.critic.verifier import SymbolicCritic
from orto.llm.schemas import DiagnosticEdit, SpanCoordinate


@pytest.fixture(scope="module")
def critic() -> SymbolicCritic:
    """Provides a SymbolicCritic instance."""
    return SymbolicCritic(SyntaxEngine())


def make_sva_edit(start: int, end: int, orig: str, rep: str) -> DiagnosticEdit:
    """Helper to create SVA diagnostic edits."""
    return DiagnosticEdit(
        span=SpanCoordinate(start_char=start, end_char=end, original_text=orig),
        replacement=rep,
        errant_type="R:VERB:SVA",
        linguistic_rule="Subject-Verb Agreement",
        explanation="Testing SVA agreement",
        counterfactual_example="Example",
        confidence=0.98,
        critic_verified=False,
    )


def test_critic_passes_valid_sva_correction(critic: SymbolicCritic) -> None:
    """Tests that a correct SVA fix (singular subject + singular verb) is approved."""
    # Singular 'box' with incorrect 'were' -> fixed to 'was'
    text = "The box of old vintage vinyl records were dropped."
    edit = make_sva_edit(start=37, end=41, orig="were", rep="was")

    result = critic.verify_edit(text, edit)
    assert result.passed is True
    assert "verified successfully" in result.diagnostic_message.lower() or result.passed


def test_critic_rejects_invalid_sva_regression(critic: SymbolicCritic) -> None:
    """Tests that an incorrect edit inducing agreement mismatch is rejected."""
    # Plural 'boxes' with 'were' -> maliciously edit 'were' to 'was'
    text = "The boxes of old vintage vinyl records were dropped."
    bad_edit = make_sva_edit(start=39, end=43, orig="were", rep="was")

    result = critic.verify_edit(text, bad_edit)
    assert result.passed is False
    assert "Agreement violation" in result.diagnostic_message


def test_critic_handles_non_sva_edits(critic: SymbolicCritic) -> None:
    """Tests that non-SVA edits (e.g. spelling) pass verification cleanly."""
    text = "She will definately come."
    spell_edit = DiagnosticEdit(
        span=SpanCoordinate(start_char=9, end_char=19, original_text="definately"),
        replacement="definitely",
        errant_type="R:SPELL",
        linguistic_rule="Spelling rule",
        explanation="Orthographic correction",
        counterfactual_example="She will definitely come.",
        confidence=0.99,
        critic_verified=False,
    )

    result = critic.verify_edit(text, spell_edit)
    assert result.passed is True
