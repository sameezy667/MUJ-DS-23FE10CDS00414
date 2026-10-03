"""
@file schemas.py
@description Typed data models for ML classification, feature extraction, and routing decisions
@module orto/ml
"""

from dataclasses import dataclass
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


@dataclass
class EditFeatureVector:
    """Tabular feature vector extracted for a single candidate DiagnosticEdit."""

    errant_type_idx: int
    original_len: int
    replacement_len: int
    span_start_ratio: float
    sentence_len_tokens: int
    critic_passed: int
    sva_error_flag: int
    fluency_delta: float
    initial_confidence: float
    has_intervening_prep: int

    def to_list(self) -> List[float]:
        """Converts feature fields to float list for scikit-learn models."""
        return [
            float(self.errant_type_idx),
            float(self.original_len),
            float(self.replacement_len),
            float(self.span_start_ratio),
            float(self.sentence_len_tokens),
            float(self.critic_passed),
            float(self.sva_error_flag),
            float(self.fluency_delta),
            float(self.initial_confidence),
            float(self.has_intervening_prep),
        ]


class EditClassificationResult(BaseModel):
    """Prediction outcome for a candidate DiagnosticEdit."""

    edit_idx: int
    original_text: str
    replacement: str
    errant_type: str
    prob_valid: float = Field(..., ge=0.0, le=1.0, description="Calibrated probability that edit is a true correction")
    is_accepted: bool = Field(..., description="Whether edit passes the confidence router threshold")
    classifier_score: float = Field(..., description="Raw model decision function score")


class RoutingDecision(BaseModel):
    """Routing prediction for an incoming raw sentence."""

    sentence: str
    route_to_llm: bool = Field(..., description="True if sentence requires deep LLM reasoning; False if symbolic rules suffice")
    predicted_complexity: float = Field(..., ge=0.0, le=1.0)
    routing_rationale: str
