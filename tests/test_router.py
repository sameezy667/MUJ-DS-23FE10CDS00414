"""
@file test_router.py
@description Unit tests for FeatureExtractor, EditConfidenceClassifier, and InvocationRouter
@module tests
"""

import os
import tempfile
import numpy as np
import pytest

from orto.critic.verifier import CriticResult
from orto.lm.ngram import NGramLanguageModel
from orto.llm.schemas import DiagnosticEdit, SpanCoordinate
from orto.ml.features import FeatureExtractor
from orto.ml.router import EditConfidenceClassifier, InvocationRouter
from orto.ml.train_router import train_router_model


def test_feature_extractor_vector_shape():
    """Verifies feature extraction output dimensions and scalar values."""
    lm = NGramLanguageModel(order=2)
    lm.train(["The box was heavy."])

    extractor = FeatureExtractor(ngram_model=lm)
    text = "The box of records were dropped."
    edit = DiagnosticEdit(
        span=SpanCoordinate(start_char=19, end_char=23, original_text="were"),
        replacement="was",
        errant_type="R:VERB:SVA",
        linguistic_rule="SVA Rule",
        explanation="Subject head is singular.",
        counterfactual_example="The records were heavy.",
        confidence=0.95,
        critic_verified=True,
    )

    vec = extractor.extract_vector(text, edit)
    feat_list = vec.to_list()

    assert len(feat_list) == 10
    assert feat_list[0] == 0.0  # R:VERB:SVA index
    assert feat_list[1] == 4.0  # len('were')
    assert feat_list[2] == 3.0  # len('was')
    assert feat_list[5] == 1.0  # critic_passed


def test_train_and_predict_edit_classifier():
    """Verifies end-to-end training, serialization, and classification inference."""
    with tempfile.NamedTemporaryFile(mode="w", suffix=".joblib", delete=False) as f:
        model_path = f.name

    # Train model
    bundle = train_router_model(
        output_path=model_path,
        model_type="logistic_regression",
    )
    assert os.path.exists(model_path)
    assert bundle["validation_metrics"]["accuracy"] > 0.50

    # Load into classifier
    classifier = EditConfidenceClassifier(model_path=model_path, threshold=0.40)
    text = "The box of records were dropped."
    edit = DiagnosticEdit(
        span=SpanCoordinate(start_char=19, end_char=23, original_text="were"),
        replacement="was",
        errant_type="R:VERB:SVA",
        linguistic_rule="SVA",
        explanation="Fix SVA.",
        counterfactual_example="The records were dropped.",
        confidence=0.90,
        critic_verified=True,
    )

    results = classifier.classify_edits(text, [edit])
    assert len(results) == 1
    assert 0.0 <= results[0].prob_valid <= 1.0
    assert results[0].errant_type == "R:VERB:SVA"

    filtered = classifier.filter_and_rerank(text, [edit])
    assert len(filtered) <= 1


def test_invocation_router_decisions():
    """Verifies complexity scoring and routing decisions for simple vs complex sentences."""
    router = InvocationRouter(complexity_threshold=0.50)

    simple_sentence = "Good morning."
    simple_decision = router.route(simple_sentence)
    assert simple_decision.route_to_llm is False
    assert simple_decision.predicted_complexity < 0.50

    complex_sentence = (
        "Although the research scientists who were studying the climate patterns published their initial findings, "
        "the governmental committee whose members disagreed would not accept the conclusions."
    )
    priors = {
        "anomalies": ["Unresolved token 'whose' with dep='dep'"],
        "subject_verb_pairs": [
            {"subject": {"text": "scientists"}, "verb": {"text": "were"}},
            {"subject": {"text": "committee"}, "verb": {"text": "would"}},
        ],
    }
    complex_decision = router.route(complex_sentence, syntax_priors=priors)
    assert complex_decision.route_to_llm is True
    assert complex_decision.predicted_complexity >= 0.50
