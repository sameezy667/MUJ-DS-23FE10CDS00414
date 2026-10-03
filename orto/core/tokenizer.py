"""
@file tokenizer.py
@description Non-destructive offset tokenizer and character span validator
@module orto/core
"""

from dataclasses import dataclass
from typing import List, Optional
import re

from orto.llm.schemas import SpanCoordinate


@dataclass(frozen=True)
class OffsetToken:
    """Represents a token with exact character start and end offsets in the original text."""

    text: str
    start_char: int
    end_char: int
    index: int


class NonDestructiveTokenizer:
    """
    Tokenizer that preserves exact character offsets, whitespace, line breaks,
    and punctuation without mutating the original text.
    """

    # Regex matches contiguous alphanumeric words (including contractions) or individual non-whitespace characters
    TOKEN_PATTERN = re.compile(r"\w+(?:['’]\w+)?|[^\w\s]", re.UNICODE)

    def tokenize(self, text: str) -> List[OffsetToken]:
        """
        Tokenizes the input string into a list of OffsetToken objects.

        Args:
            text: The raw input string.

        Returns:
            A list of OffsetToken instances with exact [start_char, end_char] bounds.
        """
        tokens: List[OffsetToken] = []
        for index, match in enumerate(self.TOKEN_PATTERN.finditer(text)):
            start, end = match.span()
            tokens.append(
                OffsetToken(
                    text=match.group(0),
                    start_char=start,
                    end_char=end,
                    index=index,
                )
            )
        return tokens

    @staticmethod
    def validate_span(text: str, span: SpanCoordinate) -> bool:
        """
        Validates whether the span coordinates strictly match the original text slice.

        Args:
            text: The original text.
            span: The span coordinate to validate.

        Returns:
            True if 0 <= start_char <= end_char <= len(text) and text[start_char:end_char] == span.original_text.
        """
        if span.start_char < 0 or span.end_char > len(text) or span.start_char > span.end_char:
            return False
        return text[span.start_char : span.end_char] == span.original_text

    @staticmethod
    def find_span_for_token(tokens: List[OffsetToken], token_idx: int) -> Optional[SpanCoordinate]:
        """
        Returns a SpanCoordinate for a given token index.

        Args:
            tokens: List of offset tokens.
            token_idx: 0-indexed token index.

        Returns:
            SpanCoordinate or None if token_idx is out of bounds.
        """
        if 0 <= token_idx < len(tokens):
            t = tokens[token_idx]
            return SpanCoordinate(
                start_char=t.start_char,
                end_char=t.end_char,
                original_text=t.text,
            )
        return None
