"""
@file metrics.py
@description Stylometric research metrics for quantifying sentence rhythm, burstiness, and synthetic markers
@module orto/style
"""

import math
import re
from typing import Any, Dict, List, Literal, Tuple
from spacy.tokens import Doc, Span


# Curated dictionary of overrepresented LLM lexical tropes and natural replacements
LLM_MARKER_PATTERNS: List[Tuple[str, str, str]] = [
    (
        r"\bdelve(?:\s+into)?\b",
        "delve",
        "Overused LLM transition. Prefer 'explore', 'examine', or 'investigate'.",
    ),
    (
        r"\b(?:rich\s+)?tapestry\b",
        "tapestry",
        "Common synthetic metaphor. Prefer 'blend', 'network', 'variety', or specific nouns.",
    ),
    (
        r"\bbeacon\s+of\b",
        "beacon",
        "Cliché inspirational trope. Prefer 'model', 'guide', or 'example'.",
    ),
    (
        r"\bpivotal(?:\s+role)?\b",
        "pivotal",
        "Overused emphatic adjective. Prefer 'key', 'central', 'essential', or 'critical'.",
    ),
    (
        r"\bunderscores\b",
        "underscores",
        "Repetitive academic filler. Prefer 'highlights', 'shows', or 'emphasizes'.",
    ),
    (
        r"\bvital\s+role\b",
        "vital role",
        "Corporate/AI filler phrase. Prefer 'essential part', 'key contribution', or active verbs.",
    ),
    (
        r"\bfoster(?:\s+a)?\b",
        "foster",
        "Overrepresented bureaucratic verb. Prefer 'encourage', 'build', or 'support'.",
    ),
    (
        r"\btestament\s+to\b",
        "testament",
        "Overused rhetorical idiom. Prefer 'evidence of', 'proof of', or 'demonstrates'.",
    ),
    (
        r"\bmoreover\b",
        "moreover",
        "Rigid formal discourse marker. Prefer conversational connectors like 'also', 'further', or omit.",
    ),
    (
        r"\bfurthermore\b",
        "furthermore",
        "Overly rigid transition. Prefer natural transition words or combining clauses.",
    ),
    (
        r"\bin\s+conclusion\b",
        "in conclusion",
        "Formulaic essay trope. Prefer organic summarizing phrasing.",
    ),
    (
        r"\bit\s+is\s+worth\s+noting\s+that\b",
        "it is worth noting that",
        "Bloated preamble trope. Omit or replace with 'notably' / direct statement.",
    ),
    (
        r"\bin\s+today's\s+(?:fast-paced|digital|interconnected)\s+world\b",
        "in today's world",
        "Generic synthetic introductory cliché.",
    ),
    (
        r"\bit\s+is\s+crucial\s+to\b",
        "it is crucial to",
        "Preachy impersonal construction. Prefer direct imperatives or 'we must'.",
    ),
    (
        r"\bmultifaceted\b",
        "multifaceted",
        "Stiff academic adjective. Prefer 'complex', 'varied', or 'diverse'.",
    ),
    (
        r"\bparamount\b",
        "paramount",
        "Overwrought intensifier. Prefer 'top priority', 'vital', or 'essential'.",
    ),
]


def compute_burstiness(sentence_lengths: List[int]) -> Tuple[float, float, float]:
    """
    Computes the Burstiness Score (B) defined as the Coefficient of Variation:
        B = std_dev / mean

    Args:
        sentence_lengths: List of word counts for each sentence.

    Returns:
        Tuple of (burstiness_score, mean_length, std_dev).
    """
    if not sentence_lengths:
        return 0.0, 0.0, 0.0

    n = len(sentence_lengths)
    if n <= 1:
        # A single sentence has zero variance
        return 0.0, float(sentence_lengths[0]), 0.0

    mean_len = sum(sentence_lengths) / n
    if mean_len == 0.0:
        return 0.0, 0.0, 0.0

    variance = sum((x - mean_len) ** 2 for x in sentence_lengths) / n
    std_dev = math.sqrt(variance)
    burstiness = std_dev / mean_len

    return round(burstiness, 3), round(mean_len, 2), round(std_dev, 2)


def detect_cliche_markers(text: str) -> Tuple[int, List[str], List[Dict[str, Any]]]:
    """
    Scans text for overused LLM markers, rigid transitions, and cliché tropes.

    Args:
        text: Raw input string.

    Returns:
        Tuple of (total_cliche_count, unique_markers_list, matched_span_dicts).
    """
    matches: List[Dict[str, Any]] = []
    unique_markers: set = set()

    for pattern, name, reason in LLM_MARKER_PATTERNS:
        for m in re.finditer(pattern, text, re.IGNORECASE):
            start, end = m.span()
            matched_text = m.group(0)
            unique_markers.add(name)
            matches.append(
                {
                    "marker_name": name,
                    "matched_text": matched_text,
                    "start_char": start,
                    "end_char": end,
                    "reason": reason,
                }
            )

    return len(matches), sorted(list(unique_markers)), matches


def compute_passive_and_nominalization(doc: Doc) -> Tuple[float, float]:
    """
    Computes:
    1. Passive verb ratio: auxpass occurrences / total verb tokens.
    2. Nominalization density: nouns ending in -tion, -ment, -ance, -ence, -ity / total tokens.

    Args:
        doc: Parsed spaCy Doc.

    Returns:
        Tuple of (passive_ratio, nominalization_ratio).
    """
    if len(doc) == 0:
        return 0.0, 0.0

    # Passive ratio
    verb_count = sum(1 for t in doc if t.pos_ in ("VERB", "AUX"))
    auxpass_count = sum(1 for t in doc if t.dep_ == "auxpass")
    passive_ratio = (auxpass_count / verb_count) if verb_count > 0 else 0.0

    # Nominalization density
    nominal_suffixes = (
        "tion",
        "tions",
        "ment",
        "ments",
        "ance",
        "ances",
        "ence",
        "ences",
        "ity",
        "ities",
    )
    nominal_count = sum(
        1
        for t in doc
        if t.pos_ == "NOUN" and t.text.lower().endswith(nominal_suffixes) and len(t.text) > 4
    )
    nominal_ratio = nominal_count / len(doc)

    return round(passive_ratio, 3), round(nominal_ratio, 3)


def compute_opening_variety(doc: Doc) -> float:
    """
    Measures the syntactic variety of sentence openings based on initial POS tags.

    Args:
        doc: Parsed spaCy Doc.

    Returns:
        Ratio of unique sentence opening POS patterns [0.0, 1.0].
    """
    sentences = list(doc.sents)
    if not sentences:
        return 1.0
    if len(sentences) == 1:
        return 1.0

    openings: List[str] = []
    for sent in sentences:
        tokens = [t for t in sent if not t.is_space and not t.is_punct]
        if tokens:
            # First 2 POS tags
            pos_pattern = "-".join(t.pos_ for t in tokens[:2])
            openings.append(pos_pattern)

    if not openings:
        return 1.0

    unique_patterns = len(set(openings))
    return round(unique_patterns / len(openings), 3)


def compute_naturalness_grade(
    burstiness: float,
    cliche_count: int,
    passive_ratio: float,
    opening_variety: float,
) -> Literal["Natural", "Monotonous", "Heavily Synthetic"]:
    """
    Determines qualitative naturalness grade from quantitative stylometric indices.

    Args:
        burstiness: Sentence-length variation ratio.
        cliche_count: Total detected AI markers.
        passive_ratio: Density of passive constructions.
        opening_variety: Syntactic opening variety ratio.

    Returns:
        "Natural", "Monotonous", or "Heavily Synthetic".
    """
    if cliche_count >= 2 or (burstiness < 0.25 and cliche_count >= 1):
        return "Heavily Synthetic"
    if burstiness < 0.30 or opening_variety < 0.50:
        return "Monotonous"
    return "Natural"
