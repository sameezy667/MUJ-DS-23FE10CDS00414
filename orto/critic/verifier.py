"""
@file verifier.py
@description Symbolic morphosyntactic regression verifier and SVA assertion engine
@module orto/critic
"""

from dataclasses import dataclass
from typing import List, Optional
from orto.core.patcher import ReverseOffsetPatcher
from orto.core.syntax_engine import SyntaxEngine
from orto.llm.schemas import DiagnosticEdit


@dataclass
class CriticResult:
    """Outcome of symbolic morphosyntactic verification for a candidate edit."""

    passed: bool
    diagnostic_message: str


class SymbolicCritic:
    """
    Validates candidate edits by applying them to an in-memory virtual buffer,
    re-parsing the sentence with spaCy, and asserting linguistic invariants
    such as Subject-Verb Agreement and tree connectivity.
    """

    def __init__(self, syntax_engine: Optional[SyntaxEngine] = None) -> None:
        """
        Initializes the Symbolic Critic.

        Args:
            syntax_engine: An instance of SyntaxEngine (creates default if None).
        """
        self.syntax_engine = syntax_engine or SyntaxEngine()

    def verify_edit(self, original_text: str, edit: DiagnosticEdit) -> CriticResult:
        """
        Applies a single candidate edit virtually and verifies morphosyntactic integrity.

        Args:
            original_text: The unmodified source string.
            edit: The candidate DiagnosticEdit to verify.

        Returns:
            CriticResult indicating pass/fail with diagnostic rationale.
        """
        # 1. Virtual Patching
        try:
            patched_text = ReverseOffsetPatcher.patch(original_text, [edit])
        except Exception as e:
            return CriticResult(
                passed=False,
                diagnostic_message=f"Virtual patching failed: {str(e)}",
            )

        # 2. Re-parse virtual sentence
        doc = self.syntax_engine.parse(patched_text)

        # 3. Check for orphaned tokens (dep_ == 'dep', ignoring pure whitespace tokens)
        orphaned = [t for t in doc if t.dep_ == "dep" and t.text.strip() != ""]
        if orphaned:
            orphan_details = ", ".join(f"'{t.text}' (idx {t.i})" for t in orphaned)
            return CriticResult(
                passed=False,
                diagnostic_message=f"Syntactic tree connectivity broken: unresolved orphaned token(s) {orphan_details}",
            )

        # 4. Morphosyntactic Subject-Verb Agreement Assertion
        if edit.errant_type == "R:VERB:SVA":
            sva_check = self._verify_sva(doc, edit, patched_text)
            if not sva_check.passed:
                return sva_check

        return CriticResult(
            passed=True,
            diagnostic_message="All symbolic morphosyntactic invariants passed.",
        )

    def verify_all(
        self, original_text: str, edits: List[DiagnosticEdit]
    ) -> List[CriticResult]:
        """
        Verifies a list of candidate edits independently.

        Args:
            original_text: The unmodified source string.
            edits: List of candidate DiagnosticEdit objects.

        Returns:
            List of CriticResult objects corresponding to each edit.
        """
        return [self.verify_edit(original_text, edit) for edit in edits]

    def _verify_sva(
        self, doc, edit: DiagnosticEdit, patched_text: str
    ) -> CriticResult:
        """
        Verifies that the verb and its subject head share matching morphological Number.
        """
        # Find the patched token in the new doc
        patched_start = edit.span.start_char
        patched_end = patched_start + len(edit.replacement)

        # Locate token(s) covering the patched span
        matched_tokens = [
            t for t in doc if (t.idx < patched_end and (t.idx + len(t.text)) > patched_start)
        ]

        if not matched_tokens:
            return CriticResult(
                passed=True,
                diagnostic_message="No token matched patched span; skipping strict SVA.",
            )

        verb_tokens = [t for t in matched_tokens if t.pos_ in ("VERB", "AUX")]
        if not verb_tokens:
            verb_tokens = matched_tokens

        for v in verb_tokens:
            # Find nominal subjects attached directly or via parent head
            subj_tokens = [
                c for c in v.children if c.dep_ in ("nsubj", "nsubjpass", "csubj", "csubjpass")
            ]

            # If verb is an aux/auxpass, check subject of the parent head
            if not subj_tokens and v.head != v:
                subj_tokens = [
                    c
                    for c in v.head.children
                    if c.dep_ in ("nsubj", "nsubjpass", "csubj", "csubjpass")
                ]

            for subj in subj_tokens:
                subj_morph = subj.morph.to_dict()
                verb_morph = v.morph.to_dict()

                subj_number = subj_morph.get("Number")
                subj_person = subj_morph.get("Person", "3")
                s_lower = subj.text.lower()
                if s_lower == "i":
                    subj_number = "Sing"
                    subj_person = "1"
                elif s_lower == "you":
                    subj_number = "Plur"
                    subj_person = "2"
                elif not subj_number:
                    if subj.tag_ in ("NN", "NNP"):
                        subj_number = "Sing"
                        subj_person = "3"
                    elif subj.tag_ in ("NNS", "NNPS"):
                        subj_number = "Plur"
                        subj_person = "3"

                verb_number = verb_morph.get("Number")
                verb_person = verb_morph.get("Person", "Unspecified")
                v_lower = v.text.lower()
                if not verb_number:
                    if v_lower in ("is", "was", "has", "does") or v.tag_ == "VBZ":
                        verb_number = "Sing"
                        verb_person = "3"
                    elif v_lower in ("are", "were", "have", "do") or v.tag_ == "VBP":
                        verb_number = "Plur"

                # Assert Person & Number consistency
                if subj_person == "1":
                    # "I" requires am/was/have/do/VBP. Reject 3rd singular forms (is, does, has, VBZ).
                    if v.tag_ == "VBZ" or v_lower in ("is", "does", "has", "thinks"):
                        return CriticResult(
                            passed=False,
                            diagnostic_message=(
                                f"Subject-Verb Agreement violation: 1st person subject '{subj.text}' "
                                f"cannot take 3rd-person singular verb '{v.text}'."
                            ),
                        )
                elif subj_person == "2":
                    # "You" requires are/were/have/do/VBP. Reject 3rd singular forms (is, was, does, has, VBZ).
                    if v.tag_ == "VBZ" or v_lower in ("is", "was", "does", "has", "thinks"):
                        return CriticResult(
                            passed=False,
                            diagnostic_message=(
                                f"Subject-Verb Agreement violation: 2nd person subject '{subj.text}' "
                                f"cannot take 3rd-person singular verb '{v.text}'."
                            ),
                        )
                elif subj_person == "3":
                    if subj_number == "Sing":
                        if v.tag_ == "VBP" or v_lower in ("are", "were"):
                            return CriticResult(
                                passed=False,
                                diagnostic_message=(
                                    f"Subject-Verb Agreement violation: Singular subject '{subj.text}' "
                                    f"requires singular verb (got plural/base '{v.text}')."
                                ),
                            )
                    elif subj_number == "Plur":
                        if v.tag_ == "VBZ" or v_lower in ("is", "was", "does", "has"):
                            return CriticResult(
                                passed=False,
                                diagnostic_message=(
                                    f"Subject-Verb Agreement violation: Plural subject '{subj.text}' "
                                    f"requires plural verb (got 3rd singular '{v.text}')."
                                ),
                            )

        return CriticResult(
            passed=True,
            diagnostic_message="Subject-Verb Agreement verified successfully.",
        )
