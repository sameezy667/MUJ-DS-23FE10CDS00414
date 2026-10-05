"""
@file client.py
@description LLM Client orchestrating structured decoding, model cascading, multi-provider fallbacks, persistent disk caching, and offline universal linguistic analysis
@module orto/llm
"""

import hashlib
import json
import os
import re
from typing import Any, Dict, List, Optional, Tuple

from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

from orto.core.linguistic_fallback import UniversalLinguisticEngine
from orto.core.tokenizer import NonDestructiveTokenizer
from orto.llm.prompts import (
    SYSTEM_PROMPT,
    build_analysis_prompt,
    build_refinement_prompt,
)
from orto.llm.schemas import DiagnosticEdit, OrtoAnalysis, SpanCoordinate


CACHE_FILE = "data/cache/llm_cache.json"

# Fast working fallback models on OpenRouter
FALLBACK_FREE_MODELS = [
    "nvidia/nemotron-3.5-lightning:free",
    "qwen/qwen3.8-27b:free",
    "liquid/lfm-2.5-2.6b:free",
]


def normalize_errant_type(raw_type: str) -> str:
    """Normalizes informal error descriptions into official ERRANT taxonomy strings."""
    t = raw_type.strip().upper()
    if t in ("R:SPELL", "R:VERB:SVA", "R:VERB:TENSE", "R:NOUN:NUM", "R:PREP", "M:DET", "R:WO", "R:OTHER"):
        return t
    if t.startswith(("R:", "M:", "U:")):
        if "SVA" in t or "AGREE" in t:
            return "R:VERB:SVA"
        if "TENSE" in t or "FORM" in t or "INF" in t or "PART" in t:
            return "R:VERB:TENSE"
        if "SPELL" in t or "ORTH" in t:
            return "R:SPELL"
        if "NUM" in t or "MASS" in t or "COUNT" in t:
            return "R:NOUN:NUM"
        if "PREP" in t:
            return "R:PREP"
        if "DET" in t or "ART" in t:
            return "M:DET"
        if "WO" in t or "ORDER" in t:
            return "R:WO"
        return "R:OTHER"

    t_lower = raw_type.lower()
    if "agreement" in t_lower or "sva" in t_lower or "singular/plural verb" in t_lower or "subject-verb" in t_lower:
        return "R:VERB:SVA"
    if "spell" in t_lower or "typo" in t_lower or "orthograph" in t_lower or "capital" in t_lower:
        return "R:SPELL"
    if "tense" in t_lower or "past" in t_lower or "participle" in t_lower or "modal" in t_lower or "infinitive" in t_lower:
        return "R:VERB:TENSE"
    if "article" in t_lower or "determiner" in t_lower or "missing 'a'" in t_lower or "missing 'the'" in t_lower:
        return "M:DET"
    if "preposition" in t_lower or "prep" in t_lower or "collocation" in t_lower:
        return "R:PREP"
    if "countab" in t_lower or "mass noun" in t_lower or "plural noun" in t_lower or "number" in t_lower:
        return "R:NOUN:NUM"
    if "word order" in t_lower:
        return "R:WO"
    if "verb" in t_lower:
        return "R:VERB:TENSE"
    if "noun" in t_lower:
        return "R:NOUN:NUM"
    return "R:OTHER"


def extract_clean_json(raw_text: str) -> Optional[Dict[str, Any]]:
    """
    Robustly extracts and parses JSON dictionary from LLM response text,
    stripping reasoning blocks (<think>...</think>), markdown code fences, and whitespace.
    """
    if not raw_text:
        return None

    # Strip thinking / reasoning tags (e.g. Nemotron, DeepSeek R1)
    text = re.sub(r"<think>.*?</think>", "", raw_text, flags=re.DOTALL).strip()

    # Try direct parse
    try:
        data = json.loads(text)
        if isinstance(data, dict):
            return data
    except Exception:
        pass

    # Try extracting from markdown code fences
    fence_match = re.search(r"```(?:json)?\s*(\{.*?\})\s*```", text, flags=re.DOTALL)
    if fence_match:
        try:
            data = json.loads(fence_match.group(1))
            if isinstance(data, dict):
                return data
        except Exception:
            pass

    # Try finding outermost JSON object braces
    brace_match = re.search(r"(\{.*\})", text, flags=re.DOTALL)
    if brace_match:
        try:
            data = json.loads(brace_match.group(1))
            if isinstance(data, dict):
                return data
        except Exception:
            pass

    return None


class LLMClient:
    """
    Production-grade LLM Client orchestrating structured decoding,
    multi-provider model cascading, persistent disk caching, and seamless
    instant fallback to the Universal Linguistic Diagnostic Engine.
    """

    def __init__(
        self,
        api_key: Optional[str] = None,
        base_url: Optional[str] = None,
        model: Optional[str] = None,
        temperature: float = 0.0,
        seed: int = 42,
        mock_mode: bool = False,
        cache_path: str = CACHE_FILE,
    ) -> None:
        """
        Initializes the LLMClient.

        Args:
            api_key: OpenAI, OpenRouter, or Gemini API key.
            base_url: Custom base URL.
            model: Model identifier.
            temperature: Sampling temperature (pinned to 0.0 for deterministic outputs).
            seed: Random seed.
            mock_mode: If True, bypasses API and uses UniversalLinguisticEngine directly.
            cache_path: Path to persistent disk cache JSON.
        """
        self.api_key = (
            api_key
            or os.environ.get("OPENROUTER_API_KEY")
            or os.environ.get("OPENAI_API_KEY")
            or os.environ.get("GEMINI_API_KEY")
            or os.environ.get("GOOGLE_API_KEY")
        )

        detected_base_url = base_url or os.environ.get("OPENAI_BASE_URL")
        if not detected_base_url and self.api_key and self.api_key.startswith("sk-or-v1-"):
            detected_base_url = "https://openrouter.ai/api/v1"
        self.base_url = detected_base_url

        default_model = (
            os.environ.get("OPENROUTER_MODEL")
            or os.environ.get("OPENAI_MODEL")
            or ("openai/gpt-4o-mini" if self.base_url and "openrouter" in self.base_url else "gpt-4o-mini")
        )
        self.model = model or default_model
        if self.base_url and "openrouter" in self.base_url and not ("/" in self.model):
            self.model = f"openai/{self.model}"

        self.temperature = temperature
        self.seed = seed
        self.mock_mode = mock_mode or not bool(self.api_key)
        self.cache_path = cache_path

        # Universal Linguistic Engine fallback
        self.linguistic_engine = UniversalLinguisticEngine()

        # Telemetry info
        self.last_engine_tier: str = "Uninitialized"

        # In-memory and disk cache
        self._cache: Dict[str, Any] = self._load_cache()

        # Track credit status to avoid repeated 402 delays
        self._credits_exhausted = False

        # Build OpenAI client
        self._openai_client: Optional[OpenAI] = None
        if not self.mock_mode and self.api_key:
            client_kwargs: Dict[str, Any] = {
                "api_key": self.api_key,
                "timeout": 3.0,
                "max_retries": 0,
            }
            if self.base_url:
                client_kwargs["base_url"] = self.base_url
            try:
                self._openai_client = OpenAI(**client_kwargs)
            except Exception:
                self._openai_client = None

    def _load_cache(self) -> Dict[str, Any]:
        """Loads disk cache JSON."""
        if os.path.exists(self.cache_path):
            try:
                with open(self.cache_path, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception:
                return {}
        return {}

    def _save_cache(self) -> None:
        """Persists cache to disk."""
        os.makedirs(os.path.dirname(self.cache_path), exist_ok=True)
        try:
            with open(self.cache_path, "w", encoding="utf-8") as f:
                json.dump(self._cache, f, indent=2)
        except Exception:
            pass

    def _get_cache_key(self, text: str, mode: str = "analyze") -> str:
        """Computes deterministic cache key."""
        raw = f"{self.model}:{mode}:{text}"
        return hashlib.sha256(raw.encode("utf-8")).hexdigest()

    def analyze(self, text: str, syntax_priors: Dict[str, Any]) -> OrtoAnalysis:
        """
        Submits text and syntactic priors to the LLM with structured output constraints,
        multi-model cascading fallback, disk caching, and universal linguistic fallback.
        """
        if self.mock_mode or self._openai_client is None:
            self.last_engine_tier = "Universal Linguistic Engine (Offline)"
            return self.linguistic_engine.analyze(text, syntax_priors)

        cache_key = self._get_cache_key(text, mode="analyze")
        if cache_key in self._cache:
            self.last_engine_tier = f"Disk Cache ({self.model})"
            return self._parse_json_dict_to_analysis(text, self._cache[cache_key])

        # If previous call indicated exhausted credits on this key, use high-speed linguistic fallback
        if self._credits_exhausted:
            self.last_engine_tier = "Universal Linguistic Engine (Offline Fallback)"
            return self.linguistic_engine.analyze(text, syntax_priors)

        prompt = build_analysis_prompt(text, syntax_priors)

        # Build candidate models cascade: [Primary Model]
        models_to_try = [self.model]

        for candidate_model in models_to_try:
            try:
                req_kwargs: Dict[str, Any] = {
                    "model": candidate_model,
                    "temperature": self.temperature,
                    "max_tokens": 1200,
                    "seed": self.seed,
                    "messages": [
                        {"role": "system", "content": SYSTEM_PROMPT},
                        {"role": "user", "content": prompt},
                    ],
                }
                if "gpt" in candidate_model or "claude" in candidate_model:
                    req_kwargs["response_format"] = {"type": "json_object"}

                response = self._openai_client.chat.completions.create(**req_kwargs)
                raw_content = response.choices[0].message.content or "{}"
                parsed_dict = extract_clean_json(raw_content)

                if parsed_dict is not None and "edits" in parsed_dict:
                    analysis = self._parse_json_dict_to_analysis(text, parsed_dict)
                    self._cache[cache_key] = parsed_dict
                    self._save_cache()
                    self.last_engine_tier = f"LLM ({candidate_model})"
                    return analysis
            except Exception as e:
                err_str = str(e)
                if "402" in err_str or "credits" in err_str.lower():
                    self._credits_exhausted = True
                continue

        # If LLM failed, immediately fall back to Universal Linguistic Engine
        self.last_engine_tier = "Universal Linguistic Engine (Fallback)"
        return self.linguistic_engine.analyze(text, syntax_priors)

    def refine(
        self,
        text: str,
        failed_edits: List[DiagnosticEdit],
        critic_diagnostics: List[str],
    ) -> OrtoAnalysis:
        """
        Issues a single-turn reflection prompt to the LLM with symbolic critic error feedback.
        """
        if self.mock_mode or self._openai_client is None or self._credits_exhausted:
            return self._deterministic_offline_refine(text, failed_edits, critic_diagnostics)

        refine_key_text = f"{text}|||" + "|||".join(
            f"{e.span.original_text}->{e.replacement}:{d}"
            for e, d in zip(failed_edits, critic_diagnostics)
        )
        cache_key = self._get_cache_key(refine_key_text, mode="refine")
        if cache_key in self._cache:
            return self._parse_json_dict_to_analysis(text, self._cache[cache_key])

        prompt = build_refinement_prompt(text, failed_edits, critic_diagnostics)

        try:
            req_kwargs: Dict[str, Any] = {
                "model": self.model,
                "temperature": self.temperature,
                "max_tokens": 1200,
                "seed": self.seed,
                "messages": [
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": prompt},
                ],
            }
            if "gpt" in self.model or "claude" in self.model:
                req_kwargs["response_format"] = {"type": "json_object"}

            response = self._openai_client.chat.completions.create(**req_kwargs)
            raw_content = response.choices[0].message.content or "{}"
            parsed_dict = extract_clean_json(raw_content)

            if parsed_dict is not None and "edits" in parsed_dict:
                analysis = self._parse_json_dict_to_analysis(text, parsed_dict)
                self._cache[cache_key] = parsed_dict
                self._save_cache()
                return analysis
        except Exception as e:
            err_str = str(e)
            if "402" in err_str or "credits" in err_str.lower():
                self._credits_exhausted = True

        return self._deterministic_offline_refine(text, failed_edits, critic_diagnostics)

    def _parse_json_dict_to_analysis(self, text: str, data: Dict[str, Any]) -> OrtoAnalysis:
        """Parses a raw JSON dictionary into validated DiagnosticEdit objects with exact character spans."""
        edits_data = data.get("edits", [])
        diagnostic_edits: List[DiagnosticEdit] = []

        for item in edits_data:
            orig = item.get("original_text", "")
            rep = item.get("replacement", "")
            err_type = normalize_errant_type(item.get("errant_type", "R:OTHER"))
            rule = item.get("linguistic_rule", "Grammatical Correction")
            exp = item.get("explanation", "Standard usage correction.")
            cf = item.get("counterfactual_example", f"Example with {orig} if applicable.")
            conf = float(item.get("confidence", 0.95))

            start_char = item.get("start_char")
            end_char = item.get("end_char")

            if (
                start_char is not None
                and end_char is not None
                and 0 <= start_char < end_char <= len(text)
                and text[start_char:end_char] == orig
            ):
                pass
            else:
                if orig and orig in text:
                    pattern = re.compile(rf"\b{re.escape(orig)}\b")
                    match = pattern.search(text)
                    if match:
                        start_char, end_char = match.span()
                    else:
                        idx = text.find(orig)
                        start_char, end_char = idx, idx + len(orig)
                else:
                    continue

            span = SpanCoordinate(
                start_char=start_char,
                end_char=end_char,
                original_text=text[start_char:end_char],
            )

            diagnostic_edits.append(
                DiagnosticEdit(
                    span=span,
                    replacement=rep,
                    errant_type=err_type,
                    linguistic_rule=rule,
                    explanation=exp,
                    counterfactual_example=cf,
                    confidence=conf,
                    critic_verified=False,
                )
            )

        diagnostic_edits.sort(key=lambda e: e.span.start_char)
        return OrtoAnalysis(edits=diagnostic_edits)

    def _deterministic_offline_refine(
        self,
        text: str,
        failed_edits: List[DiagnosticEdit],
        critic_diagnostics: List[str],
    ) -> OrtoAnalysis:
        """
        Deterministic refinement fallback: corrects or filters out edits rejected by the critic.
        """
        refined_edits: List[DiagnosticEdit] = []
        for edit, diag in zip(failed_edits, critic_diagnostics):
            if edit.errant_type == "R:VERB:SVA":
                if edit.replacement.endswith("s"):
                    new_rep = edit.replacement[:-1]
                elif edit.replacement == "was":
                    new_rep = "were"
                elif edit.replacement == "were":
                    new_rep = "was"
                elif edit.replacement == "is":
                    new_rep = "are"
                elif edit.replacement == "are":
                    new_rep = "is"
                else:
                    new_rep = edit.replacement

                if new_rep != edit.span.original_text:
                    refined_edits.append(
                        DiagnosticEdit(
                            span=edit.span,
                            replacement=new_rep,
                            errant_type=edit.errant_type,
                            linguistic_rule=edit.linguistic_rule,
                            explanation=f"Refined after critic feedback: {diag}",
                            counterfactual_example=edit.counterfactual_example,
                            confidence=0.90,
                            critic_verified=False,
                        )
                    )
        return OrtoAnalysis(edits=refined_edits)
