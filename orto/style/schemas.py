"""
@file schemas.py
@description Pydantic models for stylometry metrics, naturalness scoring, and style suggestions
@module orto/style
"""

from typing import List, Literal, Optional
from pydantic import BaseModel, Field

from orto.llm.schemas import SpanCoordinate


class StylometricReport(BaseModel):
    """Linguistic and statistical stylometry report assessing text naturalness and rhythm."""

    burstiness_score: float = Field(
        ...,
        description="Sentence-length variance ratio (std_dev / mean). Values < 0.3 indicate monotony; > 0.5 indicate natural cadence.",
        ge=0.0,
    )
    mean_sentence_length: float = Field(
        ...,
        description="Average number of tokens per sentence",
        ge=0.0,
    )
    std_sentence_length: float = Field(
        ...,
        description="Standard deviation of sentence lengths in tokens",
        ge=0.0,
    )
    cliche_count: int = Field(
        ...,
        description="Total occurrences of overrepresented AI markers and cliché transitions",
        ge=0,
    )
    detected_markers: List[str] = Field(
        default_factory=list,
        description="Distinct cliché markers detected in the text",
    )
    passive_ratio: float = Field(
        ...,
        description="Ratio of passive verb constructions (auxpass) to total verbs",
        ge=0.0,
        le=1.0,
    )
    nominalization_ratio: float = Field(
        ...,
        description="Ratio of nominalized nouns (-tion, -ment, -ance, etc.) to total tokens",
        ge=0.0,
        le=1.0,
    )
    opening_variety_score: float = Field(
        ...,
        description="Ratio of unique sentence opening POS patterns (1.0 = highly varied, < 0.6 = repetitive)",
        ge=0.0,
        le=1.0,
    )
    naturalness_grade: Literal["Natural", "Monotonous", "Heavily Synthetic"] = Field(
        ...,
        description="Overall qualitative stylometric assessment",
    )
    sentence_lengths: List[int] = Field(
        default_factory=list,
        description="List of word token counts for each parsed sentence",
    )
    summary: str = Field(
        ...,
        description="Pedagogical summary of the stylometric diagnosis",
    )


class StyleRewriteSuggestion(BaseModel):
    """Surgical style and cadence rewrite suggestion to remedy synthetic patterns."""

    span: SpanCoordinate
    original: str = Field(..., description="Original flagged phrase or sentence segment")
    suggestion: str = Field(..., description="More natural, human-cadence alternative")
    reason: str = Field(..., description="Stylistic rationale (e.g. cliché substitution, cadence variation)")


class StyleAnalysisResult(BaseModel):
    """Complete container holding stylometry report and actionable rewrite suggestions."""

    report: StylometricReport
    suggestions: List[StyleRewriteSuggestion] = Field(
        default_factory=list,
        description="List of proposed stylistic rephrasings",
    )
