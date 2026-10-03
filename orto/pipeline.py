"""
@file pipeline.py
@description Main orchestrator coordinating Syntax Engine, LLM Diagnostics, Symbolic Critic, N-Gram Fluency, and ML Router
@module orto
"""

import os
import time
from typing import List, Optional

from orto.core.patcher import ReverseOffsetPatcher
from orto.core.syntax_engine import SyntaxEngine
from orto.core.tokenizer import NonDestructiveTokenizer
from orto.critic.verifier import SymbolicCritic
from orto.lm.ngram import NGramLanguageModel
from orto.llm.client import LLMClient
from orto.llm.schemas import (
    DiagnosticEdit,
    OrtoAnalysis,
    OrtoResponse,
    PipelineTelemetry,
)
from orto.ml.router import EditConfidenceClassifier, InvocationRouter


class OrtoEngine:
    """
    Main Neurosymbolic GEC and Diagnostic Engine.
    Combines Universal Dependency extraction, constrained LLM diagnostic generation,
    Symbolic Critic verification, N-gram fluency scoring, and ML Confidence Routing.
    """

    def __init__(
        self,
        syntax_engine: Optional[SyntaxEngine] = None,
        llm_client: Optional[LLMClient] = None,
        critic: Optional[SymbolicCritic] = None,
        ml_classifier: Optional[EditConfidenceClassifier] = None,
        invocation_router: Optional[InvocationRouter] = None,
        ngram_model: Optional[NGramLanguageModel] = None,
        enable_critic: bool = True,
        enable_ml_filter: bool = False,
        max_refinements: int = 1,
    ) -> None:
        """
        Initializes the OrtoEngine pipeline.

        Args:
            syntax_engine: spaCy dependency and morphology parser.
            llm_client: Constrained LLM client.
            critic: Symbolic morphosyntax regression verifier.
            ml_classifier: Trained ML confidence classifier / reranker.
            invocation_router: Fast symbolic vs LLM invocation router.
            ngram_model: Laplace-smoothed N-gram fluency language model.
            enable_critic: Whether to run symbolic assertions.
            enable_ml_filter: Whether to apply ML confidence filtering.
            max_refinements: Maximum reflection retries on critic failure (default 1).
        """
        self.syntax_engine = syntax_engine or SyntaxEngine()
        self.llm_client = llm_client or LLMClient()
        self.critic = critic or SymbolicCritic(self.syntax_engine)
        self.enable_critic = enable_critic
        self.enable_ml_filter = enable_ml_filter
        self.max_refinements = max_refinements

        # N-Gram Language Model
        if ngram_model is not None:
            self.ngram_model = ngram_model
        elif os.path.exists("data/models/ngram_bigram.json"):
            try:
                self.ngram_model = NGramLanguageModel.load("data/models/ngram_bigram.json")
            except Exception:
                self.ngram_model = None
        else:
            self.ngram_model = None

        # ML Router and Classifier
        self.ml_classifier = ml_classifier or EditConfidenceClassifier(
            ngram_path="data/models/ngram_bigram.json" if self.ngram_model else "",
        )
        self.invocation_router = invocation_router or InvocationRouter()

    def analyze(
        self,
        text: str,
        enable_critic: Optional[bool] = None,
        enable_ml_filter: Optional[bool] = None,
        max_refinements: Optional[int] = None,
    ) -> OrtoResponse:
        """
        Executes the full GEC diagnostic pipeline on the input string.

        Args:
            text: Raw input text.
            enable_critic: Optional override for symbolic verification.
            enable_ml_filter: Optional override for ML confidence filtering.
            max_refinements: Optional override for refinement retry count.

        Returns:
            OrtoResponse containing original text, corrected text, verified edits, and telemetry.
        """
        start_time = time.perf_counter()
        use_critic = self.enable_critic if enable_critic is None else enable_critic
        use_ml = self.enable_ml_filter if enable_ml_filter is None else enable_ml_filter
        refinement_budget = self.max_refinements if max_refinements is None else max_refinements

        # Handle empty/whitespace input
        if not text or text.strip() == "":
            return OrtoResponse(
                original_text=text,
                corrected_text=text,
                edits=[],
                telemetry=PipelineTelemetry(
                    latency_ms=0.0,
                    input_tokens=0,
                    refinement_cycles=0,
                    critic_passed=True,
                ),
            )

        # Stage 1: Syntactic Prior Extraction
        syntax_priors = self.syntax_engine.extract_priors(text)

        # Stage 2: LLM Diagnostic Hypothesis Generation
        analysis: OrtoAnalysis = self.llm_client.analyze(text, syntax_priors)
        candidate_edits = analysis.edits

        # Validate character offset alignment
        aligned_edits: List[DiagnosticEdit] = []
        for edit in candidate_edits:
            if NonDestructiveTokenizer.validate_span(text, edit.span):
                aligned_edits.append(edit)

        # Stage 3: Symbolic Critic Verification & Self-Refinement Loop
        verified_edits: List[DiagnosticEdit] = []
        refinement_cycles = 0

        if use_critic and aligned_edits:
            passed_edits: List[DiagnosticEdit] = []
            failed_edits: List[DiagnosticEdit] = []
            failed_reasons: List[str] = []

            for edit in aligned_edits:
                check = self.critic.verify_edit(text, edit)
                if check.passed:
                    edit.critic_verified = True
                    passed_edits.append(edit)
                else:
                    failed_edits.append(edit)
                    failed_reasons.append(check.diagnostic_message)

            # Single-turn retry loop if violations occurred and budget remains
            if failed_edits and refinement_budget > 0:
                refinement_cycles += 1
                refined_analysis = self.llm_client.refine(
                    text, failed_edits, failed_reasons
                )
                for r_edit in refined_analysis.edits:
                    if NonDestructiveTokenizer.validate_span(text, r_edit.span):
                        r_check = self.critic.verify_edit(text, r_edit)
                        if r_check.passed:
                            r_edit.critic_verified = True
                            passed_edits.append(r_edit)

            verified_edits = passed_edits
        else:
            # If critic disabled, mark all aligned edits as unverified
            for edit in aligned_edits:
                edit.critic_verified = False
            verified_edits = aligned_edits

        # Stage 3B: Trained ML Confidence Classification & Reranking
        if use_ml and verified_edits:
            verified_edits = self.ml_classifier.filter_and_rerank(
                text=text,
                edits=verified_edits,
                syntax_priors=syntax_priors,
            )

        # Resolve any overlapping spans among verified edits
        final_edits = ReverseOffsetPatcher.filter_conflicts(verified_edits)

        # Stage 4: In-Memory Virtual Patching
        corrected_text = ReverseOffsetPatcher.patch(text, final_edits)

        elapsed_ms = (time.perf_counter() - start_time) * 1000.0

        return OrtoResponse(
            original_text=text,
            corrected_text=corrected_text,
            edits=final_edits,
            telemetry=PipelineTelemetry(
                latency_ms=round(elapsed_ms, 2),
                input_tokens=len(text.split()),
                refinement_cycles=refinement_cycles,
                critic_passed=len(verified_edits) == len(aligned_edits),
            ),
        )
