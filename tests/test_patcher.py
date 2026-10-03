"""
@file test_patcher.py
@description Unit tests for reverse-offset in-memory string patcher
@module tests
"""

import pytest
from orto.core.patcher import ReverseOffsetPatcher
from orto.llm.schemas import DiagnosticEdit, SpanCoordinate


def make_edit(
    start: int,
    end: int,
    orig: str,
    rep: str,
    err_type: str = "R:SPELL",
    conf: float = 0.95,
) -> DiagnosticEdit:
    """Helper to construct DiagnosticEdit instances for testing."""
    return DiagnosticEdit(
        span=SpanCoordinate(start_char=start, end_char=end, original_text=orig),
        replacement=rep,
        errant_type=err_type,  # type: ignore
        linguistic_rule="Rule test",
        explanation="Explanation test",
        counterfactual_example="Counterfactual test",
        confidence=conf,
        critic_verified=True,
    )


def test_patch_single_edit() -> None:
    """Tests applying a single surgical replacement."""
    text = "The box were heavy."
    edit = make_edit(8, 12, "were", "was", "R:VERB:SVA")
    patched = ReverseOffsetPatcher.patch(text, [edit])
    assert patched == "The box was heavy."


def test_patch_multiple_non_overlapping_edits() -> None:
    """Tests applying multiple disjoint edits without index drift."""
    text = "She will definately recieve the letter."
    edit1 = make_edit(9, 19, "definately", "definitely")
    edit2 = make_edit(20, 27, "recieve", "receive")

    # Pass in normal order
    patched = ReverseOffsetPatcher.patch(text, [edit1, edit2])
    assert patched == "She will definitely receive the letter."

    # Pass in reverse order to ensure patcher handles any input order correctly
    patched_reverse_order = ReverseOffsetPatcher.patch(text, [edit2, edit1])
    assert patched_reverse_order == "She will definitely receive the letter."


def test_patch_selective_indices() -> None:
    """Tests selective application using accepted_indices."""
    text = "She will definately recieve the letter."
    edit1 = make_edit(9, 19, "definately", "definitely")
    edit2 = make_edit(20, 27, "recieve", "receive")

    # Accept only edit 0 ("definitely")
    patched = ReverseOffsetPatcher.patch(text, [edit1, edit2], accepted_indices={0})
    assert patched == "She will definitely recieve the letter."

    # Accept only edit 1 ("receive")
    patched = ReverseOffsetPatcher.patch(text, [edit1, edit2], accepted_indices={1})
    assert patched == "She will definately receive the letter."


def test_patch_conflict_resolution() -> None:
    """Tests that overlapping edits are filtered based on highest confidence."""
    text = "The quick fox."
    # Conflicting overlapping edits:
    edit_low = make_edit(4, 9, "quick", "fast", conf=0.60)
    edit_high = make_edit(4, 13, "quick fox", "clever animal", conf=0.99)

    filtered = ReverseOffsetPatcher.filter_conflicts([edit_low, edit_high])
    assert len(filtered) == 1
    assert filtered[0].replacement == "clever animal"


def test_patch_text_mismatch_raises() -> None:
    """Tests that a span text mismatch raises ValueError."""
    text = "The quick brown fox."
    # Span points to 'quick' but original_text says 'slow'
    bad_edit = make_edit(4, 9, "slow", "fast")
    with pytest.raises(ValueError, match="Span text mismatch"):
        ReverseOffsetPatcher.patch(text, [bad_edit])


def test_patch_out_of_bounds_raises() -> None:
    """Tests that out-of-bounds start or end raises ValueError."""
    text = "Short text"
    bad_edit = make_edit(0, 50, "Short text and more", "New text")
    with pytest.raises(ValueError, match="out of bounds"):
        ReverseOffsetPatcher.patch(text, [bad_edit])
