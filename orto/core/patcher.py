"""
@file patcher.py
@description In-memory string patcher applying edits in reverse offset order
@module orto/core
"""

from typing import List, Optional, Set, Tuple
from orto.llm.schemas import DiagnosticEdit


class ReverseOffsetPatcher:
    """
    Applies character-level diagnostic edits to source text in reverse offset order
    to completely eliminate index-shifting mutations.
    """

    @staticmethod
    def validate_non_overlapping(edits: List[DiagnosticEdit]) -> bool:
        """
        Verifies that no two edits overlap in their character intervals.

        Args:
            edits: The list of diagnostic edits to check.

        Returns:
            True if all edit intervals are mutually disjoint, False otherwise.
        """
        sorted_edits = sorted(edits, key=lambda e: e.span.start_char)
        for i in range(len(sorted_edits) - 1):
            if sorted_edits[i].span.end_char > sorted_edits[i + 1].span.start_char:
                return False
        return True

    @classmethod
    def filter_conflicts(cls, edits: List[DiagnosticEdit]) -> List[DiagnosticEdit]:
        """
        Greedily retains non-overlapping edits prioritized by higher confidence.

        Args:
            edits: Candidate diagnostic edits.

        Returns:
            Disjoint subset of edits.
        """
        if not edits:
            return []

        # Sort by confidence descending, then by start_char ascending
        sorted_by_conf = sorted(edits, key=lambda e: (-e.confidence, e.span.start_char))
        accepted: List[DiagnosticEdit] = []

        for candidate in sorted_by_conf:
            c_start = candidate.span.start_char
            c_end = candidate.span.end_char
            overlaps = False
            for acc in accepted:
                a_start = acc.span.start_char
                a_end = acc.span.end_char
                if not (c_end <= a_start or c_start >= a_end):
                    overlaps = True
                    break
            if not overlaps:
                accepted.append(candidate)

        # Return sorted by start_char for consistency
        return sorted(accepted, key=lambda e: e.span.start_char)

    @classmethod
    def patch(
        cls,
        text: str,
        edits: List[DiagnosticEdit],
        accepted_indices: Optional[Set[int]] = None,
    ) -> str:
        """
        Applies diagnostic edits to the text in reverse character offset order.

        Args:
            text: The original source text.
            edits: List of DiagnosticEdit instances.
            accepted_indices: Optional set of 0-based edit indices to apply. If None, all are applied.

        Returns:
            The patched string.

        Raises:
            ValueError: If an edit span bounds are out of range or text alignment fails.
        """
        if not edits:
            return text

        # Select target edits
        target_edits: List[Tuple[int, DiagnosticEdit]] = []
        for idx, edit in enumerate(edits):
            if accepted_indices is None or idx in accepted_indices:
                target_edits.append((idx, edit))

        # Check disjointness among targets
        selected_edits_only = [e for _, e in target_edits]
        if not cls.validate_non_overlapping(selected_edits_only):
            selected_edits_only = cls.filter_conflicts(selected_edits_only)
            target_edits = [(i, e) for i, e in enumerate(selected_edits_only)]

        # Sort in descending order of start_char (Reverse-Offset Patcher)
        sorted_targets = sorted(target_edits, key=lambda item: item[1].span.start_char, reverse=True)

        result = text
        for _, edit in sorted_targets:
            span = edit.span
            start = span.start_char
            end = span.end_char

            if start < 0 or end > len(text):
                raise ValueError(
                    f"Edit span [{start}, {end}] is out of bounds for text of length {len(text)}"
                )

            # Assert alignment against the slice in the original text
            current_slice = text[start:end]
            if current_slice != span.original_text:
                raise ValueError(
                    f"Span text mismatch: expected '{span.original_text}' but found '{current_slice}'"
                )

            result = result[:start] + edit.replacement + result[end:]

        return result
