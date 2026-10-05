"""
@file schemas.py
@description Pydantic models for structured linguistic diagnostics and error correction
@module orto/llm
"""

from typing import List, Literal, Optional
from pydantic import BaseModel, Field


class SpanCoordinate(BaseModel):
    """Represents a character-level span within the source text."""

    start_char: int = Field(
        ...,
        description="0-indexed start character offset in original text (inclusive)",
        ge=0,
    )
    end_char: int = Field(
        ...,
        description="0-indexed end character offset in original text (exclusive)",
        ge=0,
    )
    original_text: str = Field(
        ...,
        description="Exact substring in original text matching offsets",
    )


class DiagnosticEdit(BaseModel):
    """Represents a surgical diagnostic edit with pedagogical explanation and ERRANT classification."""

    span: SpanCoordinate
    replacement: str = Field(
        ...,
        description="Minimal replacement string (empty string for deletions)",
    )
    errant_type: Literal[
        "R:SPELL",
        "R:VERB:SVA",
        "R:VERB:TENSE",
        "R:NOUN:NUM",
        "R:PREP",
        "M:DET",
        "R:WO",
        "R:OTHER",
    ] = Field(
        ...,
        description="Official ERRANT taxonomy classification",
    )
    linguistic_rule: str = Field(
        ...,
        description="Formal grammatical rule name (e.g., 'Subject-Verb Agreement with Intervening Prepositional Phrase')",
    )
    explanation: str = Field(
        ...,
        description="Concise diagnostic explanation of why the original text is erroneous",
    )
    counterfactual_example: str = Field(
        ...,
        description="A syntactically valid paired sentence illustrating correct usage of the replaced/original item",
    )
    confidence: float = Field(
        ...,
        ge=0.0,
        le=1.0,
        description="Model confidence score between 0.0 and 1.0",
    )
    critic_verified: bool = Field(
        default=False,
        description="Flag indicating if the edit passed the symbolic morphosyntactic verifier",
    )


class OrtoAnalysis(BaseModel):
    """Structured response container emitted by the LLM diagnostic engine."""

    edits: List[DiagnosticEdit] = Field(
        default_factory=list,
        description="List of proposed minimal diagnostic edits",
    )


class PipelineTelemetry(BaseModel):
    """Telemetry data capturing latency and processing metrics."""

    latency_ms: float = Field(..., description="Total pipeline latency in milliseconds")
    input_tokens: int = Field(default=0, description="Approximate or actual prompt tokens")
    refinement_cycles: int = Field(
        default=0,
        description="Number of symbolic critic refinement retry turns performed",
    )
    critic_passed: bool = Field(
        default=True,
        description="True if all retained edits passed symbolic verification",
    )
    engine_tier: Optional[str] = Field(
        default="LLM (Primary)",
        description="Name of the model or engine tier that produced the diagnostic hypothesis",
    )


class OrtoResponse(BaseModel):
    """Full API and pipeline response payload."""

    original_text: str = Field(..., description="Original unedited input string")
    corrected_text: str = Field(..., description="String after applying verified edits")
    edits: List[DiagnosticEdit] = Field(
        default_factory=list,
        description="List of verified diagnostic edits",
    )
    telemetry: Optional[PipelineTelemetry] = Field(
        default=None,
        description="Execution telemetry metrics",
    )
