"""
@file test_style.py
@description Unit and integration tests for stylometry metrics, burstiness calculation, and style naturalizer
@module tests
"""

import pytest
from starlette.testclient import TestClient

from backend.server import app
from orto.core.syntax_engine import SyntaxEngine
from orto.style.analyzer import StyleAnalyzer
from orto.style.metrics import (
    compute_burstiness,
    compute_naturalness_grade,
    compute_opening_variety,
    compute_passive_and_nominalization,
    detect_cliche_markers,
)
from orto.style.naturalizer import StyleNaturalizer


@pytest.fixture(scope="module")
def syntax_engine() -> SyntaxEngine:
    """Provides a shared SyntaxEngine instance."""
    return SyntaxEngine()


@pytest.fixture(scope="module")
def style_analyzer(syntax_engine: SyntaxEngine) -> StyleAnalyzer:
    """Provides a StyleAnalyzer instance."""
    return StyleAnalyzer(syntax_engine)


@pytest.fixture(scope="module")
def client() -> TestClient:
    """Provides a TestClient for testing style API endpoints."""
    return TestClient(app)


def test_compute_burstiness_uniform() -> None:
    """Tests that uniform sentence lengths yield 0.0 burstiness."""
    lengths = [12, 12, 12, 12]
    b, mean_len, std_dev = compute_burstiness(lengths)
    assert b == 0.0
    assert mean_len == 12.0
    assert std_dev == 0.0


def test_compute_burstiness_diverse() -> None:
    """Tests that diverse sentence lengths yield high burstiness (> 0.50)."""
    # Short punchy sentences mixed with long multi-clause sentences
    lengths = [4, 28, 5, 34, 6, 22]
    b, mean_len, std_dev = compute_burstiness(lengths)
    assert b > 0.50
    assert mean_len > 0
    assert std_dev > 0


def test_compute_burstiness_edge_cases() -> None:
    """Tests burstiness with single sentence or empty list."""
    assert compute_burstiness([]) == (0.0, 0.0, 0.0)
    assert compute_burstiness([15]) == (0.0, 15.0, 0.0)


def test_detect_cliche_markers() -> None:
    """Tests detection of common overused LLM markers and rigid transitions."""
    text = (
        "Let us delve into this topic. Moreover, the rich tapestry of cultures "
        "is a testament to human resilience. It is crucial to foster collaboration."
    )
    count, unique_markers, spans = detect_cliche_markers(text)

    assert count >= 4
    assert "delve" in unique_markers
    assert "moreover" in unique_markers
    assert "tapestry" in unique_markers
    assert "testament" in unique_markers

    for s in spans:
        assert text[s["start_char"] : s["end_char"]].lower() in s["matched_text"].lower()


def test_passive_and_nominalization(syntax_engine: SyntaxEngine) -> None:
    """Tests computation of passive voice and nominalization density."""
    text = "The preliminary investigation and examination was conducted by the committee."
    doc = syntax_engine.parse(text)
    passive_ratio, nominal_ratio = compute_passive_and_nominalization(doc)

    assert passive_ratio > 0.0  # 'was conducted' is passive
    assert nominal_ratio > 0.0  # 'investigation', 'examination' are nominalizations


def test_opening_variety(syntax_engine: SyntaxEngine) -> None:
    """Tests syntactic opening variety computation."""
    # Sentences starting with different POS patterns
    diverse_text = "She walked to school. In the morning, it was cold. Running quickly, he caught the bus."
    doc = syntax_engine.parse(diverse_text)
    variety = compute_opening_variety(doc)
    assert variety >= 0.60


def test_naturalness_grading() -> None:
    """Tests naturalness grade assignments."""
    assert (
        compute_naturalness_grade(burstiness=0.60, cliche_count=0, passive_ratio=0.1, opening_variety=0.8)
        == "Natural"
    )
    assert (
        compute_naturalness_grade(burstiness=0.15, cliche_count=0, passive_ratio=0.1, opening_variety=0.8)
        == "Monotonous"
    )
    assert (
        compute_naturalness_grade(burstiness=0.40, cliche_count=3, passive_ratio=0.1, opening_variety=0.8)
        == "Heavily Synthetic"
    )


def test_style_analyzer_full_report(style_analyzer: StyleAnalyzer) -> None:
    """Tests full end-to-end StyleAnalyzer result on synthetic text."""
    synthetic_text = (
        "Moreover, we must delve into the rich tapestry of modern education. "
        "Furthermore, this underscores the vital role of innovative technologies."
    )
    result = style_analyzer.analyze(synthetic_text)

    assert result.report.cliche_count >= 3
    assert result.report.naturalness_grade == "Heavily Synthetic"
    assert len(result.suggestions) >= 3


def test_style_naturalizer(style_analyzer: StyleAnalyzer) -> None:
    """Tests that StyleNaturalizer substitutes clichés with organic idioms."""
    text = "We will delve into this problem to foster a better solution."
    naturalizer = StyleNaturalizer(analyzer=style_analyzer)
    polished = naturalizer.naturalize(text)

    assert "explore" in polished.lower() or "delve" not in polished.lower()
    assert "encourage" in polished.lower() or "build" in polished.lower() or "foster" not in polished.lower()


def test_style_api_endpoint(client: TestClient) -> None:
    """Tests standalone /api/v1/style/analyze endpoint."""
    payload = {
        "text": "Let us delve into this rich tapestry of ideas. Moreover, it is crucial to act."
    }
    response = client.post("/api/v1/style/analyze", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert "report" in data
    assert data["report"]["cliche_count"] >= 2
    assert "suggestions" in data
