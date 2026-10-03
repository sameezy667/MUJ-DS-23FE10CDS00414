"""
@file features.py
@description Tabular feature extractor converting linguistic, syntactic, critic, and fluency signals into feature vectors
@module orto/ml
"""

from typing import Any, Dict, List, Optional

from orto.critic.verifier import CriticResult
from orto.lm.ngram import NGramLanguageModel
from orto.llm.schemas import DiagnosticEdit
from orto.ml.schemas import EditFeatureVector


ERRANT_TYPE_TO_INDEX: Dict[str, int] = {
    "R:VERB:SVA": 0,
    "R:SPELL": 1,
    "R:PREP": 2,
    "M:DET": 3,
    "R:NOUN:NUM": 4,
    "R:VERB:TENSE": 5,
    "R:OTHER": 6,
    "R:WO": 7,
    "R:NOUN": 8,
    "R:VERB": 9,
    "M:PUNCT": 10,
    "R:ORTH": 11,
    "M:VERB:FORM": 12,
    "U:DET": 13,
    "UNKNOWN": 14,
}

FEATURE_NAMES = [
    "errant_type_idx",
    "original_len",
    "replacement_len",
    "span_start_ratio",
    "sentence_len_tokens",
    "critic_passed",
    "sva_error_flag",
    "fluency_delta",
    "initial_confidence",
    "has_intervening_prep",
]


class FeatureExtractor:
    """
    Extracts tabular features for candidate DiagnosticEdits combining:
    1. ERRANT error taxonomy categorical encoding
    2. Character and token span geometry
    3. Symbolic Critic verdict assertions
    4. N-Gram language model fluency delta
    5. Syntactic dependency tree properties
    """

    def __init__(self, ngram_model: Optional[NGramLanguageModel] = None) -> None:
        """
        Initializes the feature extractor.

        Args:
            ngram_model: Optional pre-trained N-gram language model for fluency delta scoring.
        """
        self.ngram_model = ngram_model

    def extract_vector(
        self,
        text: str,
        edit: DiagnosticEdit,
        syntax_priors: Optional[Dict[str, Any]] = None,
        critic_result: Optional[CriticResult] = None,
    ) -> EditFeatureVector:
        """
        Converts a candidate edit into an EditFeatureVector.

        Args:
            text: Raw original sentence string.
            edit: The candidate DiagnosticEdit.
            syntax_priors: Extracted Universal Dependency priors.
            critic_result: Outcome of the Symbolic Critic verification.

        Returns:
            EditFeatureVector instance.
        """
        text_len = max(len(text), 1)
        tokens = text.split()
        token_count = len(tokens)

        # 1. Taxonomy index
        err_type = edit.errant_type
        type_idx = ERRANT_TYPE_TO_INDEX.get(err_type, ERRANT_TYPE_TO_INDEX["UNKNOWN"])

        # 2. Geometry
        orig_len = len(edit.span.original_text)
        rep_len = len(edit.replacement)
        start_ratio = edit.span.start_char / text_len

        # 3. Critic verdict
        critic_passed = 1 if (critic_result is not None and critic_result.passed) or edit.critic_verified else 0
        sva_flag = 1 if edit.errant_type == "R:VERB:SVA" else 0

        # 4. N-gram Fluency delta
        fluency_delta = 0.0
        if self.ngram_model is not None:
            patched = (
                text[: edit.span.start_char]
                + edit.replacement
                + text[edit.span.end_char :]
            )
            fluency_delta = self.ngram_model.score_edit_fluency_delta(text, patched)

        # 5. Intervening preposition heuristic
        has_prep = 0
        if syntax_priors:
            sva_pairs = syntax_priors.get("subject_verb_pairs", [])
            for pair in sva_pairs:
                v_start = pair.get("verb", {}).get("start_char", -1)
                s_end = pair.get("subject", {}).get("end_char", -1)
                if s_end < edit.span.start_char <= v_start:
                    has_prep = 1
                    break

        return EditFeatureVector(
            errant_type_idx=type_idx,
            original_len=orig_len,
            replacement_len=rep_len,
            span_start_ratio=round(start_ratio, 4),
            sentence_len_tokens=token_count,
            critic_passed=critic_passed,
            sva_error_flag=sva_flag,
            fluency_delta=round(fluency_delta, 4),
            initial_confidence=round(edit.confidence, 4),
            has_intervening_prep=has_prep,
        )

    def extract_matrix(
        self,
        text: str,
        edits: List[DiagnosticEdit],
        syntax_priors: Optional[Dict[str, Any]] = None,
        critic_results: Optional[List[CriticResult]] = None,
    ) -> List[List[float]]:
        """Extracts 2D feature matrix (N_edits x D_features) for scikit-learn."""
        rows = []
        for i, edit in enumerate(edits):
            c_res = critic_results[i] if critic_results and i < len(critic_results) else None
            vec = self.extract_vector(text, edit, syntax_priors, c_res)
            rows.append(vec.to_list())
        return rows
