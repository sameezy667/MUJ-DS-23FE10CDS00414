"""
@file router.py
@description Inference engine for Edit Confidence Classification and LLM vs Symbolic Invocation Routing
@module orto/ml
"""

import os
from typing import Any, Dict, List, Optional, Tuple

import joblib
import numpy as np

from orto.critic.verifier import CriticResult
from orto.lm.ngram import NGramLanguageModel
from orto.llm.schemas import DiagnosticEdit
from orto.ml.features import FEATURE_NAMES, FeatureExtractor
from orto.ml.schemas import EditClassificationResult, RoutingDecision


DEFAULT_MODEL_PATH = "data/models/edit_router.joblib"
DEFAULT_NGRAM_PATH = "data/models/ngram_bigram.json"


class EditConfidenceClassifier:
    """
    ML classifier that evaluates candidate DiagnosticEdits and predicts
    their calibrated posterior probability of being true grammatical corrections.
    """

    def __init__(
        self,
        model_path: str = DEFAULT_MODEL_PATH,
        ngram_path: str = DEFAULT_NGRAM_PATH,
        threshold: float = 0.45,
    ) -> None:
        """
        Initializes the EditConfidenceClassifier.

        Args:
            model_path: Path to serialized joblib model bundle.
            ngram_path: Path to pre-trained N-gram language model.
            threshold: Decision boundary probability threshold for accepting edits.
        """
        self.model_path = model_path
        self.ngram_path = ngram_path
        self.threshold = threshold

        # Load N-gram model
        self.ngram_model: Optional[NGramLanguageModel] = None
        if os.path.exists(ngram_path):
            try:
                self.ngram_model = NGramLanguageModel.load(ngram_path)
            except Exception:
                self.ngram_model = None

        self.feature_extractor = FeatureExtractor(ngram_model=self.ngram_model)

        # Load trained classifier bundle
        self.bundle: Optional[Dict[str, Any]] = None
        self.classifier = None
        self.scaler = None

        if os.path.exists(model_path):
            try:
                self.bundle = joblib.load(model_path)
                self.classifier = self.bundle.get("classifier")
                self.scaler = self.bundle.get("scaler")
            except Exception:
                self.bundle = None

    def classify_edits(
        self,
        text: str,
        edits: List[DiagnosticEdit],
        syntax_priors: Optional[Dict[str, Any]] = None,
        critic_results: Optional[List[CriticResult]] = None,
    ) -> List[EditClassificationResult]:
        """
        Computes calibrated confidence probabilities for a list of candidate edits.

        Args:
            text: Raw original sentence string.
            edits: Candidate edits from generator.
            syntax_priors: Universal Dependency priors.
            critic_results: Verification outcomes from Symbolic Critic.

        Returns:
            List of EditClassificationResult objects.
        """
        if not edits:
            return []

        # If no serialized model found, use rule/critic heuristic fallback
        if self.classifier is None or self.scaler is None:
            results = []
            for i, e in enumerate(edits):
                c_passed = (
                    (critic_results[i].passed if critic_results and i < len(critic_results) else e.critic_verified)
                )
                prob = 0.90 if c_passed else 0.20
                results.append(
                    EditClassificationResult(
                        edit_idx=i,
                        original_text=e.span.original_text,
                        replacement=e.replacement,
                        errant_type=e.errant_type,
                        prob_valid=prob,
                        is_accepted=prob >= self.threshold,
                        classifier_score=prob,
                    )
                )
            return results

        # Extract feature matrix
        X_raw = self.feature_extractor.extract_matrix(
            text, edits, syntax_priors, critic_results
        )
        X_arr = np.array(X_raw, dtype=np.float32)
        X_scaled = self.scaler.transform(X_arr)

        probs = self.classifier.predict_proba(X_scaled)[:, 1]
        decision_scores = (
            self.classifier.decision_function(X_scaled)
            if hasattr(self.classifier, "decision_function")
            else probs
        )

        results = []
        for i, (edit, p, s) in enumerate(zip(edits, probs, decision_scores)):
            results.append(
                EditClassificationResult(
                    edit_idx=i,
                    original_text=edit.span.original_text,
                    replacement=edit.replacement,
                    errant_type=edit.errant_type,
                    prob_valid=round(float(p), 4),
                    is_accepted=bool(p >= self.threshold),
                    classifier_score=round(float(s), 4),
                )
            )
        return results

    def filter_and_rerank(
        self,
        text: str,
        edits: List[DiagnosticEdit],
        syntax_priors: Optional[Dict[str, Any]] = None,
        critic_results: Optional[List[CriticResult]] = None,
    ) -> List[DiagnosticEdit]:
        """
        Applies the ML classifier to rerank and filter out low-confidence/false-alarm edits.

        Args:
            text: Original string.
            edits: Candidate edits.
            syntax_priors: Extracted priors.
            critic_results: Critic verdicts.

        Returns:
            Filtered list of high-confidence DiagnosticEdit objects.
        """
        if not edits:
            return []

        classifications = self.classify_edits(text, edits, syntax_priors, critic_results)
        accepted_edits: List[DiagnosticEdit] = []

        for edit, res in zip(edits, classifications):
            if res.is_accepted:
                # Update edit confidence with calibrated model probability
                edit.confidence = res.prob_valid
                accepted_edits.append(edit)

        return accepted_edits


class InvocationRouter:
    """
    Routes incoming user sentences between fast deterministic symbolic rules
    and full LLM structured decoding based on predicted grammatical complexity.
    """

    def __init__(self, complexity_threshold: float = 0.50) -> None:
        """
        Initializes the Invocation Router.

        Args:
            complexity_threshold: Cutoff above which sentence is routed to LLM.
        """
        self.complexity_threshold = complexity_threshold

    def route(
        self,
        text: str,
        syntax_priors: Optional[Dict[str, Any]] = None,
    ) -> RoutingDecision:
        """
        Decides whether an input text requires full LLM invocation.

        Routing Logic:
        1. Clean, trivial sentences -> Route to symbolic / pass directly.
        2. Simple single-clause SVA or exact confusables -> Handled efficiently by Tier-1/2.
        3. Multi-clause sentences, anomalous dependencies, or open lexical/tense errors -> Route to LLM.

        Args:
            text: Raw sentence.
            syntax_priors: Extracted dependency features.

        Returns:
            RoutingDecision object.
        """
        tokens = text.split()
        tok_len = len(tokens)

        if not text or tok_len <= 2:
            return RoutingDecision(
                sentence=text,
                route_to_llm=False,
                predicted_complexity=0.1,
                routing_rationale="Trivial or empty string; fast symbolic bypass.",
            )

        complexity = 0.0

        # Feature 1: Sentence length
        if tok_len > 15:
            complexity += 0.35
        elif tok_len > 8:
            complexity += 0.20

        # Feature 2: Dependency anomalies (e.g. unlinked clauses)
        if syntax_priors:
            anomalies = syntax_priors.get("anomalies", [])
            if anomalies:
                complexity += 0.40

            # Feature 3: Multiple subject-verb clauses
            sva_pairs = syntax_priors.get("subject_verb_pairs", [])
            if len(sva_pairs) > 1:
                complexity += 0.25

        # Feature 4: Open vocabulary prepositions or ambiguous modals
        ambiguous_markers = ["would", "could", "should", "might", "which", "whose", "whom", "although"]
        if any(w in text.lower() for w in ambiguous_markers):
            complexity += 0.20

        complexity = min(round(complexity, 2), 1.0)
        route_llm = complexity >= self.complexity_threshold

        rationale = (
            f"Syntactic complexity score={complexity:.2f} >= {self.complexity_threshold}; requires LLM reasoning."
            if route_llm
            else f"Syntactic complexity score={complexity:.2f} < {self.complexity_threshold}; handled via fast symbolic path."
        )

        return RoutingDecision(
            sentence=text,
            route_to_llm=route_llm,
            predicted_complexity=complexity,
            routing_rationale=rationale,
        )
