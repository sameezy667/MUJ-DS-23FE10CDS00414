"""
@file __init__.py
@description Stylometry and Naturalness package for Orto
@module orto/style
"""

from orto.style.analyzer import StyleAnalyzer
from orto.style.metrics import (
    compute_burstiness,
    compute_naturalness_grade,
    compute_opening_variety,
    compute_passive_and_nominalization,
    detect_cliche_markers,
)
from orto.style.naturalizer import StyleNaturalizer
from orto.style.schemas import (
    StyleAnalysisResult,
    StyleRewriteSuggestion,
    StylometricReport,
)

__all__ = [
    "StylometricReport",
    "StyleRewriteSuggestion",
    "StyleAnalysisResult",
    "StyleAnalyzer",
    "StyleNaturalizer",
    "compute_burstiness",
    "detect_cliche_markers",
    "compute_passive_and_nominalization",
    "compute_opening_variety",
    "compute_naturalness_grade",
]
