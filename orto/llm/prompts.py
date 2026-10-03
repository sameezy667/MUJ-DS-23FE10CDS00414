"""
@file prompts.py
@description Linguistically grounded prompt templates for constrained GEC diagnostics
@module orto/llm
"""

import json
from typing import Any, Dict, List
from orto.llm.schemas import DiagnosticEdit


SYSTEM_PROMPT = """You are Orto, an expert computational linguist and neurosymbolic Grammatical Error Correction (GEC) diagnostic engine.

Your task is to analyze the user's text, identify genuine grammatical/orthographic errors, and propose minimal, surgical diagnostic edits.
You MUST output your response strictly as a valid JSON object with the key "edits" containing a list of diagnostic edit objects.

STRICT OPERATIONAL RULES:
1. CONSERVATIVE HIGH PRECISION: Only propose edits for genuine, unambiguous errors in grammar, spelling, agreement, verb form, punctuation, or word choice. If a sentence or clause is already grammatically correct (e.g. "I do not know", "what are you going to do", "I think"), NEVER alter it. Return "edits": [] when no true errors exist.
2. SURGICAL EDIT LOCALITY: Confine your edits strictly to the minimal erroneous character spans [start_char, end_char]. Do NOT rewrite non-erroneous clauses or alter the author's stylistic voice.
3. EXACT CHARACTER OFFSETS: start_char is 0-indexed inclusive, end_char is 0-indexed exclusive. You MUST guarantee that original_text == input_text[start_char:end_char].
4. ERRANT TAXONOMY: Every edit must be classified into exactly one of:
   - "R:SPELL": Spelling, typographical, or phonetic errors.
   - "R:VERB:SVA": Subject-Verb Agreement violations (e.g., "he know" -> "he knows", "they was" -> "they were").
   - "R:VERB:TENSE": Verb tense, aspect, or voice errors.
   - "R:NOUN:NUM": Noun number or countability errors.
   - "R:PREP": Incorrect preposition selection or extraneous preposition.
   - "M:DET": Missing determiner or article (e.g. "go to school" vs "a school").
   - "R:WO": Word order permutations.
   - "R:OTHER": Lexical confusion (e.g. affect/effect) or uncategorized errors.
5. PEDAGOGICAL GROUNDING:
   - linguistic_rule: State the formal grammatical rule.
   - explanation: Provide a concise, clear diagnosis explaining why the error occurred.
   - counterfactual_example: Provide a correct, natural sentence demonstrating how the original erroneous word would be correctly used.
6. EXPLOIT SYNTACTIC PRIORS: Use the provided Universal Dependency and Subject-Verb Agreement structural priors to verify head-dependent relationships. Note that standard English pronoun-verb pairings ("I do/am/have", "you are/were/have", "we are") are fully valid.
7. JSON OUTPUT FORMAT: Output a JSON object with:
   {
     "edits": [
       {
         "start_char": 0,
         "end_char": 4,
         "original_text": "were",
         "replacement": "was",
         "errant_type": "R:VERB:SVA",
         "linguistic_rule": "Subject-Verb Agreement",
         "explanation": "Subject is singular.",
         "counterfactual_example": "The students were present.",
         "confidence": 0.95
       }
     ]
   }
"""


def build_analysis_prompt(
    text: str,
    syntax_priors: Dict[str, Any],
    include_few_shot: bool = True,
    k_few_shot: int = 2,
) -> str:
    """
    Constructs the user prompt combining the raw text, extracted syntax priors,
    and dynamically retrieved few-shot minimal pair exemplars.

    Args:
        text: Raw input string.
        syntax_priors: Syntactic and morphological graph extracted by SyntaxEngine.
        include_few_shot: Whether to inject dynamically retrieved few-shot exemplars.
        k_few_shot: Number of few-shot demonstrations to retrieve.

    Returns:
        Formatted user prompt string.
    """
    priors_serialized = json.dumps(syntax_priors, indent=2)
    few_shot_block = ""

    if include_few_shot:
        try:
            from orto.fewshot.retriever import ExemplarRetriever

            retriever = ExemplarRetriever()
            few_shot_text = retriever.format_few_shot_prompt(text, syntax_priors, k=k_few_shot)
            if few_shot_text:
                few_shot_block = f"\n{few_shot_text}\n"
        except Exception:
            few_shot_block = ""

    return f"""Target Sentence:
"{text}"

Syntactic Dependency & Morphological Priors:
{priors_serialized}
{few_shot_block}
Instructions:
Analyze the target sentence for grammatical, spelling, and agreement errors.
Return your findings strictly conforming to the OrtoAnalysis schema with surgical [start_char, end_char] spans. If the text has no errors, return an empty edits list.
"""


def build_refinement_prompt(
    original_text: str,
    failed_edits: List[DiagnosticEdit],
    critic_diagnostics: List[str],
) -> str:
    """
    Constructs the 1-turn reflection prompt when the Symbolic Critic rejects candidate edits.

    Args:
        original_text: Raw input string.
        failed_edits: Edits that violated symbolic invariants.
        critic_diagnostics: Rejection error messages from the Symbolic Critic.

    Returns:
        Formatted retry prompt string.
    """
    failed_summary = []
    for edit, diag in zip(failed_edits, critic_diagnostics):
        failed_summary.append(
            f"- Edit: '{edit.span.original_text}' -> '{edit.replacement}' (at [{edit.span.start_char}:{edit.span.end_char}], type: {edit.errant_type})\n"
            f"  Critic Feedback: {diag}"
        )
    failed_text = "\n".join(failed_summary)

    return f"""Your previous diagnostic proposals for the target sentence failed symbolic morphosyntactic verification.

Target Sentence:
"{original_text}"

Symbolic Critic Violations:
{failed_text}

Instructions:
Refine your diagnostic edits to resolve the symbolic critic's violations while preserving minimal character spans and valid grammatical structure. Return the updated OrtoAnalysis schema.
"""
