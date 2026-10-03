"""
@file test_tokenizer.py
@description Unit tests for non-destructive offset tokenizer and span validation
@module tests
"""

import pytest
from orto.core.tokenizer import NonDestructiveTokenizer
from orto.llm.schemas import SpanCoordinate


@pytest.fixture
def tokenizer() -> NonDestructiveTokenizer:
    """Provides a tokenizer instance."""
    return NonDestructiveTokenizer()


def test_tokenize_preserves_offsets(tokenizer: NonDestructiveTokenizer) -> None:
    """Tests that token character offsets strictly match the original substrings."""
    text = "The quick brown fox   jumps over the lazy dog."
    tokens = tokenizer.tokenize(text)

    assert len(tokens) > 0
    for token in tokens:
        assert text[token.start_char : token.end_char] == token.text


def test_tokenize_handles_contractions_and_punctuation(tokenizer: NonDestructiveTokenizer) -> None:
    """Tests that contractions and punctuation marks are handled with exact bounds."""
    text = "Don't say 'hello', it's complicated!"
    tokens = tokenizer.tokenize(text)

    # Reconstructed text by inserting whitespace where needed
    for token in tokens:
        assert text[token.start_char : token.end_char] == token.text


def test_validate_span_success(tokenizer: NonDestructiveTokenizer) -> None:
    """Tests successful validation of exact span coordinates."""
    text = "The box of records were dropped."
    span = SpanCoordinate(start_char=19, end_char=23, original_text="were")
    assert tokenizer.validate_span(text, span) is True


def test_validate_span_mismatch(tokenizer: NonDestructiveTokenizer) -> None:
    """Tests rejection when original_text does not match characters at [start:end]."""
    text = "The box of records were dropped."
    span = SpanCoordinate(start_char=19, end_char=23, original_text="was")
    assert tokenizer.validate_span(text, span) is False


def test_validate_span_out_of_bounds(tokenizer: NonDestructiveTokenizer) -> None:
    """Tests rejection of out-of-bounds start/end indices."""
    text = "Short sentence."
    span_overflow = SpanCoordinate(start_char=10, end_char=50, original_text="sentence.")
    span_inverted = SpanCoordinate(start_char=10, end_char=5, original_text="")

    assert tokenizer.validate_span(text, span_overflow) is False
    assert tokenizer.validate_span(text, span_inverted) is False


def test_find_span_for_token(tokenizer: NonDestructiveTokenizer) -> None:
    """Tests token index to SpanCoordinate mapping."""
    text = "Alpha Beta Gamma"
    tokens = tokenizer.tokenize(text)

    span_1 = tokenizer.find_span_for_token(tokens, 1)
    assert span_1 is not None
    assert span_1.original_text == "Beta"
    assert span_1.start_char == 6
    assert span_1.end_char == 10

    assert tokenizer.find_span_for_token(tokens, 99) is None
