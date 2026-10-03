"""
@file analyzer.py
@description Stylometric analyzer computing quantitative rhythm metrics and identifying synthetic patterns
@module orto/style
"""

from typing import List, Optional
from orto.core.syntax_engine import SyntaxEngine
from orto.llm.schemas import SpanCoordinate
from orto.style.metrics import (
    compute_burstiness,
    compute_naturalness_grade,
    compute_opening_variety,
    compute_passive_and_nominalization,
    detect_cliche_markers,
)
from orto.style.schemas import (
    StyleAnalysisResult,
    StyleRewriteSuggestion,
    StylometricReport,
)


class StyleAnalyzer:
    """
    Analyzes text stylometry, rhythm variation (burstiness), and detects machine-generated
    markers and rhetorical clichés.
    """

    def __init__(self, syntax_engine: Optional[SyntaxEngine] = None) -> None:
        """
        Initializes the StyleAnalyzer.

        Args:
            syntax_engine: An instance of SyntaxEngine (creates default if None).
        """
        self.syntax_engine = syntax_engine or SyntaxEngine()

    def analyze(self, text: str) -> StyleAnalysisResult:
        """
        Runs full stylometric diagnostics on the input text.

        Args:
            text: Raw input string.

        Returns:
            StyleAnalysisResult with StylometricReport and actionable rewrite suggestions.
        """
        if not text or not text.strip():
            empty_report = StylometricReport(
                burstiness_score=0.0,
                mean_sentence_length=0.0,
                std_sentence_length=0.0,
                cliche_count=0,
                detected_markers=[],
                passive_ratio=0.0,
                nominalization_ratio=0.0,
                opening_variety_score=1.0,
                naturalness_grade="Natural",
                sentence_lengths=[],
                summary="No text provided.",
            )
            return StyleAnalysisResult(report=empty_report, suggestions=[])

        doc = self.syntax_engine.parse(text)

        # 1. Sentence length distribution
        sentence_lengths: List[int] = []
        for sent in doc.sents:
            token_count = sum(1 for t in sent if not t.is_space and not t.is_punct)
            if token_count > 0:
                sentence_lengths.append(token_count)

        # 2. Burstiness & Cadence
        burstiness, mean_len, std_dev = compute_burstiness(sentence_lengths)

        # 3. Cliché and AI Marker Index
        cliche_count, unique_markers, matched_spans = detect_cliche_markers(text)

        # 4. Passive & Nominalization Density
        passive_ratio, nominal_ratio = compute_passive_and_nominalization(doc)

        # 5. Syntactic Opening Variety & Copula Ratio
        opening_variety = compute_opening_variety(doc)
        verb_tokens = [t for t in doc if t.pos_ in ("VERB", "AUX")]
        copula_count = sum(1 for t in verb_tokens if t.lemma_ == "be" and t.dep_ in ("ROOT", "cop"))
        copula_ratio = (copula_count / len(verb_tokens)) if verb_tokens else 0.0

        # 6. Naturalness Grade
        grade = compute_naturalness_grade(
            burstiness=burstiness,
            cliche_count=cliche_count,
            passive_ratio=passive_ratio,
            opening_variety=opening_variety,
            copula_ratio=copula_ratio,
        )

        # Generate human-readable summary
        summary_parts: List[str] = []
        if grade == "Natural":
            summary_parts.append("Text exhibits organic human cadence with healthy burstiness.")
        elif grade == "Monotonous":
            summary_parts.append(
                f"Sentence length rhythm is uniform (Burstiness B={burstiness:.2f} < 0.35). Consider varying sentence lengths."
            )
        else:
            summary_parts.append(
                f"Detected {cliche_count} synthetic lexical markers and formulaic AI constructions."
            )

        if passive_ratio > 0.35:
            summary_parts.append(f"High passive density ({passive_ratio * 100:.1f}%).")
        if nominal_ratio > 0.15:
            summary_parts.append(f"High nominalization density ({nominal_ratio * 100:.1f}%).")

        summary = " ".join(summary_parts)

        # 7. Construct surgical suggestions for detected cliché spans
        suggestions: List[StyleRewriteSuggestion] = []
        for match in matched_spans:
            orig = match["matched_text"]
            marker = match["marker_name"]
            rep_suggestion = self._get_default_substitution(orig, marker)
            suggestions.append(
                StyleRewriteSuggestion(
                    span=SpanCoordinate(
                        start_char=match["start_char"],
                        end_char=match["end_char"],
                        original_text=orig,
                    ),
                    original=orig,
                    suggestion=rep_suggestion,
                    reason=match["reason"],
                )
            )

        report = StylometricReport(
            burstiness_score=burstiness,
            mean_sentence_length=mean_len,
            std_sentence_length=std_dev,
            cliche_count=cliche_count,
            detected_markers=unique_markers,
            passive_ratio=passive_ratio,
            nominalization_ratio=nominal_ratio,
            opening_variety_score=opening_variety,
            naturalness_grade=grade,
            sentence_lengths=sentence_lengths,
            summary=summary,
        )

        return StyleAnalysisResult(report=report, suggestions=suggestions)

    @staticmethod
    def _get_default_substitution(original: str, marker_name: str) -> str:
        """Provides direct organic replacements for common AI marker tokens."""
        mapping = {
            "delve": "explore",
            "tapestry": "landscape",
            "beacon": "guide",
            "pivotal": "key",
            "underscores": "highlights",
            "vital role": "key part",
            "foster": "encourage",
            "testament": "evidence",
            "moreover": "also",
            "furthermore": "in addition",
            "in conclusion": "finally",
            "it is worth noting that": "notably",
            "it is crucial to": "we must",
            "multifaceted": "complex",
            "paramount": "essential",
            "by construction": "by design",
            "gates on": "filters on",
            "fabricated number": "an arbitrary number" if original.lower().startswith("a ") else "arbitrary number",
            "surface that instead": "highlight that instead",
            "is defined by": "depends on",
            "plethora": "many",
            "nuanced": "subtle",
            "interplay": "dynamic",
            "seamlessly": "smoothly",
            "ever-evolving": "changing",
            "at the forefront": "leading",
            "pave the way": "enable",
            "shed light on": "clarify",
            "harnessing": "using",
            "holistic": "integrated",
            "deep dive": "close look",
            "realm of": "field of",
            "serves as a": "is a",
            "not only ... but also": "both ... and",
            "in essence": "essentially",
            "embark": "begin",
            "align with": "match",
            "spearhead": "lead",
            "synergy": "collaboration",
        }
        sub = mapping.get(marker_name.lower(), "rephrase")
        if original.istitle():
            return sub.capitalize()
        return sub
