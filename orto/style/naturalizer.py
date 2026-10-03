"""
@file naturalizer.py
@description Re-rhythms monotonous sentence cadences and replaces synthetic clichés with organic phrasing
@module orto/style
"""

from typing import List, Optional
from orto.llm.client import LLMClient
from orto.style.analyzer import StyleAnalyzer
from orto.style.schemas import StyleAnalysisResult, StyleRewriteSuggestion


NATURALIZER_SYSTEM_PROMPT = """You are Orto's Stylometry & Naturalness Re-Rhythmer.

Your task is to revise text flagged for synthetic monotony or cliché LLM markers.

STRICT PRINCIPLES:
1. CADENCE VARIATION (Burstiness): Mix short punchy clauses with longer explanatory ones to avoid robotic sentence length uniformity.
2. DE-CLICHÉ: Replace overused corporate/AI markers ("delve", "tapestry", "moreover", "beacon", "pivotal", "vital role", "testament") with organic, concrete words.
3. SEMANTIC FIDELITY: Never alter the author's underlying meaning, facts, or technical accuracy.
4. SURGICAL PRECISION: Avoid unnecessary rewrites.
"""


class StyleNaturalizer:
    """
    Applies stylometric re-rhythming and de-clichéing to enhance cadence variety
    and eliminate synthetic hallmarks.
    """

    def __init__(
        self,
        analyzer: Optional[StyleAnalyzer] = None,
        llm_client: Optional[LLMClient] = None,
    ) -> None:
        """
        Initializes the StyleNaturalizer.

        Args:
            analyzer: StyleAnalyzer instance.
            llm_client: LLMClient instance for natural rephrasing.
        """
        self.analyzer = analyzer or StyleAnalyzer()
        self.llm_client = llm_client or LLMClient()

    def naturalize(self, text: str) -> str:
        """
        Re-rhythms and polishes the input text to achieve human cadence and eliminate clichés.

        Args:
            text: Raw input text.

        Returns:
            Polished naturalized string.
        """
        if not text or not text.strip():
            return text

        analysis: StyleAnalysisResult = self.analyzer.analyze(text)

        # If text is already natural with no clichés, return unchanged
        if (
            analysis.report.naturalness_grade == "Natural"
            and analysis.report.cliche_count == 0
        ):
            return text

        # Apply surgical cliché substitutions
        result = text
        sorted_suggestions = sorted(
            analysis.suggestions,
            key=lambda s: s.span.start_char,
            reverse=True,
        )

        for sugg in sorted_suggestions:
            start = sugg.span.start_char
            end = sugg.span.end_char
            if result[start:end] == sugg.span.original_text:
                result = result[:start] + sugg.suggestion + result[end:]

        return result
