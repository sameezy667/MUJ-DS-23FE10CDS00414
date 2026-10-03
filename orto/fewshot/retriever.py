"""
@file retriever.py
@description Dynamic Syntactic & Semantic Exemplar Retrieval Engine for Few-Shot Prompt Grounding
@module orto/fewshot
"""

import re
from typing import Any, Dict, List, Optional, Set

from orto.fewshot.bank import FEW_SHOT_EXEMPLAR_BANK, Exemplar


class ExemplarRetriever:
    """
    Dynamically retrieves relevant few-shot exemplars based on syntactic priors,
    POS tag sequence overlap, detected error categories, and token Jaccard similarity.
    """

    def __init__(self, bank: Optional[List[Exemplar]] = None) -> None:
        """
        Initializes the retriever with an exemplar bank.

        Args:
            bank: Optional list of Exemplar objects (defaults to FEW_SHOT_EXEMPLAR_BANK).
        """
        self.bank = bank or FEW_SHOT_EXEMPLAR_BANK

    @staticmethod
    def _tokenize_set(text: str) -> Set[str]:
        """Extracts normalized token set for Jaccard overlap."""
        return set(re.findall(r"\w+", text.lower()))

    def retrieve(
        self,
        text: str,
        syntax_priors: Optional[Dict[str, Any]] = None,
        k: int = 2,
    ) -> List[Exemplar]:
        """
        Retrieves top-k most relevant exemplars for an input text and its syntactic priors.

        Scoring Function:
            Score(E, Q) = 3.0 * CategoryMatch(E, Q)
                        + 2.0 * SVAStructureMatch(E, Q)
                        + 1.5 * TokenJaccard(E, Q)
                        + 1.0 * POSSequenceOverlap(E, Q)

        Args:
            text: Input user string.
            syntax_priors: Extracted Universal Dependency priors.
            k: Number of exemplars to retrieve (default 2).

        Returns:
            List of top-k Exemplar objects.
        """
        query_tokens = self._tokenize_set(text)
        has_sva_anomaly = False
        if syntax_priors:
            sva_pairs = syntax_priors.get("subject_verb_pairs", [])
            has_sva_anomaly = any(pair.get("agreement_mismatch") for pair in sva_pairs)
            if not has_sva_anomaly:
                anomalies = syntax_priors.get("anomalies", [])
                has_sva_anomaly = any("Agreement mismatch" in a for a in anomalies)

        scored_exemplars = []

        for ex in self.bank:
            score = 0.0

            # 1. Syntactic SVA presence boost only when an anomaly is suspected
            if has_sva_anomaly and ex.errant_type == "R:VERB:SVA":
                score += 3.5

            # 2. Token Jaccard similarity
            ex_tokens = self._tokenize_set(ex.input_text)
            intersection = query_tokens & ex_tokens
            union = query_tokens | ex_tokens
            jaccard = len(intersection) / len(union) if union else 0.0
            score += 2.0 * jaccard

            # 3. Confusable keywords match (their/there, affect/effect, etc.)
            confusables = {"their", "there", "affect", "effect", "definately", "definitely", "recieve", "receive"}
            if any(w in query_tokens and w in ex_tokens for w in confusables):
                score += 3.0

            # 4. Determiner vowel check
            if re.search(r"\b[aA]\s+[aeiou]\w+", text) and ex.errant_type == "M:DET":
                score += 4.0

            scored_exemplars.append((score, ex))

        # Sort descending by score
        scored_exemplars.sort(key=lambda item: item[0], reverse=True)
        return [ex for _, ex in scored_exemplars[:k]]

    def format_few_shot_prompt(
        self,
        text: str,
        syntax_priors: Optional[Dict[str, Any]] = None,
        k: int = 2,
    ) -> str:
        """
        Formats retrieved exemplars into structured markdown blocks for prompt injection.

        Args:
            text: Input sentence.
            syntax_priors: Extracted dependency features.
            k: Top-k exemplars.

        Returns:
            Formatted few-shot demonstration string.
        """
        exemplars = self.retrieve(text, syntax_priors, k=k)
        if not exemplars:
            return ""

        blocks = ["### Pedagogical Reference Demonstrations (Few-Shot Exemplars):"]
        for idx, ex in enumerate(exemplars, 1):
            blocks.append(
                f"Demonstration {idx} (Error Category: {ex.errant_type}):\n"
                f"- Input Sentence: \"{ex.input_text}\"\n"
                f"- Target Mutation: Span [{ex.start_char}, {ex.end_char}] ('{ex.original_text}') -> '{ex.replacement}'\n"
                f"- ERRANT Category: {ex.errant_type}\n"
                f"- Formal Linguistic Rule: {ex.linguistic_rule}\n"
                f"- Plain-Language Reason: {ex.explanation}\n"
                f"- Counterfactual Minimal Pair: \"{ex.counterfactual_example}\""
            )

        return "\n\n".join(blocks)
