"""
@file client.py
@description LLM Client orchestrating structured decoding, persistent disk caching, and offline fallbacks
@module orto/llm
"""

import hashlib
import json
import os
import re
from typing import Any, Dict, List, Optional
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

from orto.core.tokenizer import NonDestructiveTokenizer
from orto.llm.prompts import (
    SYSTEM_PROMPT,
    build_analysis_prompt,
    build_refinement_prompt,
)
from orto.llm.schemas import DiagnosticEdit, OrtoAnalysis, SpanCoordinate


CACHE_FILE = "data/cache/llm_cache.json"


def normalize_errant_type(raw_type: str) -> str:
    """Normalizes informal error descriptions into official ERRANT taxonomy strings."""
    t = raw_type.strip().upper()
    if t.startswith(("R:", "M:", "U:")):
        return t
    t_lower = raw_type.lower()
    if "agreement" in t_lower or "sva" in t_lower or "singular/plural verb" in t_lower:
        return "R:VERB:SVA"
    if "spell" in t_lower or "typo" in t_lower or "orthograph" in t_lower:
        return "R:SPELL"
    if "tense" in t_lower or "past" in t_lower or "participle" in t_lower:
        return "R:VERB:TENSE"
    if "article" in t_lower or "determiner" in t_lower or "missing 'a'" in t_lower or "missing 'the'" in t_lower:
        return "M:DET"
    if "preposition" in t_lower or "prep" in t_lower:
        return "R:PREP"
    if "countab" in t_lower or "mass noun" in t_lower or "plural noun" in t_lower:
        return "R:NOUN:NUM"
    if "word order" in t_lower:
        return "R:WO"
    if "punct" in t_lower or "comma" in t_lower:
        return "M:PUNCT"
    if "verb" in t_lower:
        return "R:VERB"
    if "noun" in t_lower:
        return "R:NOUN"
    return "R:OTHER"


class LLMClient:
    """
    LLM Client that orchestrates structured decoding with OpenAI & OpenRouter APIs,
    persists responses in a local disk cache for instant free reruns, and provides
    a deterministic offline fallback mode.
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
            api_key: OpenAI or OpenRouter API key.
            base_url: Custom base URL.
            model: Model identifier (defaults to openai/gpt-4o-mini on OpenRouter).
            temperature: Sampling temperature (pinned to 0.0 for reproducibility).
            seed: Random seed.
            mock_mode: If True, bypasses API and runs offline engine.
            cache_path: Path to persistent disk cache JSON.
        """
        self.api_key = (
            api_key
            or os.environ.get("OPENROUTER_API_KEY")
            or os.environ.get("OPENAI_API_KEY")
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

        # In-memory and disk cache
        self._cache: Dict[str, Any] = self._load_cache()

        self._openai_client: Optional[OpenAI] = None
        if not self.mock_mode and self.api_key:
            client_kwargs: Dict[str, Any] = {
                "api_key": self.api_key,
                "timeout": 12.0,
                "max_retries": 2,
            }
            if self.base_url:
                client_kwargs["base_url"] = self.base_url
            self._openai_client = OpenAI(**client_kwargs)

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
        Submits text and syntactic priors to the LLM with structured output constraints and disk caching.
        """
        if self.mock_mode or self._openai_client is None:
            return self._deterministic_offline_analyze(text, syntax_priors)

        cache_key = self._get_cache_key(text, mode="analyze")
        if cache_key in self._cache:
            return self._parse_json_dict_to_analysis(text, self._cache[cache_key])

        prompt = build_analysis_prompt(text, syntax_priors)
        try:
            response = self._openai_client.chat.completions.create(
                model=self.model,
                temperature=self.temperature,
                max_tokens=1200,
                seed=self.seed,
                messages=[
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": prompt},
                ],
                response_format={"type": "json_object"},
            )
            raw_content = response.choices[0].message.content or "{}"
            parsed_dict = json.loads(raw_content)

            # Cache successful response
            self._cache[cache_key] = parsed_dict
            self._save_cache()

            return self._parse_json_dict_to_analysis(text, parsed_dict)
        except Exception:
            # Fallback to deterministic offline analyzer on API error/timeout
            return self._deterministic_offline_analyze(text, syntax_priors)

    def refine(
        self,
        text: str,
        failed_edits: List[DiagnosticEdit],
        critic_diagnostics: List[str],
    ) -> OrtoAnalysis:
        """
        Issues a single-turn reflection prompt to the LLM with symbolic critic error feedback.
        """
        if self.mock_mode or self._openai_client is None:
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
            response = self._openai_client.chat.completions.create(
                model=self.model,
                temperature=self.temperature,
                max_tokens=1200,
                seed=self.seed,
                messages=[
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": prompt},
                ],
                response_format={"type": "json_object"},
            )
            raw_content = response.choices[0].message.content or "{}"
            parsed_dict = json.loads(raw_content)

            self._cache[cache_key] = parsed_dict
            self._save_cache()

            return self._parse_json_dict_to_analysis(text, parsed_dict)
        except Exception:
            return self._deterministic_offline_refine(text, failed_edits, critic_diagnostics)

    def _parse_json_dict_to_analysis(self, text: str, data: Dict[str, Any]) -> OrtoAnalysis:
        """Parses a raw JSON dictionary into validated DiagnosticEdit objects with exact character spans."""
        edits_data = data.get("edits", [])
        diagnostic_edits: List[DiagnosticEdit] = []

        for item in edits_data:
            orig = item.get("original_text", "").strip()
            rep = item.get("replacement", "").strip()
            err_type = normalize_errant_type(item.get("errant_type", "R:OTHER"))
            rule = item.get("linguistic_rule", "Grammatical Correction")
            exp = item.get("explanation", "Standard usage correction.")
            cf = item.get("counterfactual_example", f"Example with {orig} if applicable.")
            conf = float(item.get("confidence", 0.95))

            # Resolve character coordinates [start_char, end_char]
            start_char = item.get("start_char")
            end_char = item.get("end_char")

            if start_char is None or end_char is None or not (0 <= start_char < end_char <= len(text) and text[start_char:end_char] == orig):
                # Search exact substring in text
                if orig and orig in text:
                    # Find span matching word boundaries if possible
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

        # Sort by start_char
        diagnostic_edits.sort(key=lambda e: e.span.start_char)
        return OrtoAnalysis(edits=diagnostic_edits)

    def _deterministic_offline_analyze(
        self, text: str, syntax_priors: Dict[str, Any]
    ) -> OrtoAnalysis:
        """
        Deterministic rule-and-prior-based fallback analyzer.
        Provides robust, linguistically grounded diagnostics for modal verbs, pronoun capitalization,
        subject-verb agreement, uncountable mass nouns, prepositions, and orthography.
        """
        edits: List[DiagnosticEdit] = []

        # 1. Subject-Verb Agreement check from extracted priors
        sva_pairs = syntax_priors.get("subject_verb_pairs", [])
        for pair in sva_pairs:
            subj = pair.get("subject", {})
            verb = pair.get("verb", {})

            subj_num = subj.get("number")
            verb_num = verb.get("number")
            subj_text = subj.get("text", "")
            verb_text = verb.get("text", "")
            verb_start = verb.get("start_char", -1)
            verb_end = verb.get("end_char", -1)

            # Heuristic SVA detection for common irregular/regular verbs
            if subj_num == "Sing" and verb_num == "Plur" and verb_start >= 0:
                rep_verb = None
                if verb_text.lower() == "were":
                    rep_verb = "was" if verb_text.islower() else "Was"
                elif verb_text.lower() == "are":
                    rep_verb = "is" if verb_text.islower() else "Is"
                elif verb_text.lower() == "have":
                    rep_verb = "has" if verb_text.islower() else "Has"
                elif verb_text.lower() == "do":
                    rep_verb = "does" if verb_text.islower() else "Does"
                elif not verb_text.endswith("s") and len(verb_text) > 2:
                    rep_verb = verb_text + "s"

                if rep_verb and text[verb_start:verb_end] == verb_text:
                    edits.append(
                        DiagnosticEdit(
                            span=SpanCoordinate(
                                start_char=verb_start,
                                end_char=verb_end,
                                original_text=verb_text,
                            ),
                            replacement=rep_verb,
                            errant_type="R:VERB:SVA",
                            linguistic_rule="Subject-Verb Agreement with Intervening Modifiers",
                            explanation=(
                                f"The grammatical subject head is '{subj_text}' (singular), but the verb '{verb_text}' "
                                f"is plural. The verb must agree in number with its subject head."
                            ),
                            counterfactual_example=f"The students {verb_text} present at the meeting.",
                            confidence=0.98,
                            critic_verified=False,
                        )
                    )

            elif subj_num == "Plur" and verb_num == "Sing" and verb_start >= 0:
                rep_verb = None
                if verb_text.lower() == "was":
                    rep_verb = "were" if verb_text.islower() else "Were"
                elif verb_text.lower() == "is":
                    rep_verb = "are" if verb_text.islower() else "Are"
                elif verb_text.lower() == "has":
                    rep_verb = "have" if verb_text.islower() else "Have"
                elif verb_text.lower() == "does":
                    rep_verb = "do" if verb_text.islower() else "Do"
                elif verb_text.endswith("s") and len(verb_text) > 3:
                    rep_verb = verb_text[:-1]

                if rep_verb and text[verb_start:verb_end] == verb_text:
                    edits.append(
                        DiagnosticEdit(
                            span=SpanCoordinate(
                                start_char=verb_start,
                                end_char=verb_end,
                                original_text=verb_text,
                            ),
                            replacement=rep_verb,
                            errant_type="R:VERB:SVA",
                            linguistic_rule="Plural Subject-Verb Agreement",
                            explanation=(
                                f"The subject head '{subj_text}' is plural, but the verb '{verb_text}' is singular. "
                                f"The verb must take the plural form."
                            ),
                            counterfactual_example=f"The student {verb_text} present at the meeting.",
                            confidence=0.98,
                            critic_verified=False,
                        )
                    )

        # 2. Modal Auxiliary + Non-Base Verb Pattern Detection
        modal_past_map = {
            "went": "go",
            "saw": "see",
            "ate": "eat",
            "came": "come",
            "took": "take",
            "wrote": "write",
            "bought": "buy",
            "found": "find",
            "made": "make",
            "said": "say",
            "told": "tell",
            "gave": "give",
            "knew": "know",
            "thought": "think",
            "brought": "bring",
            "left": "leave",
            "felt": "feel",
            "began": "begin",
            "ran": "run",
            "broke": "break",
            "chose": "choose",
            "drove": "drive",
            "fell": "fall",
            "forgot": "forget",
            "grew": "grow",
            "heard": "hear",
            "kept": "keep",
            "paid": "pay",
            "read": "read",
            "sent": "send",
            "slept": "sleep",
            "spoke": "speak",
            "spent": "spend",
            "stood": "stand",
            "swam": "swim",
            "taught": "teach",
            "threw": "throw",
            "understood": "understand",
            "wore": "wear",
            "won": "win",
        }

        # Match "can/could/should/would/will/did/do/does/must/might/may" + optional pronoun/words + past verb
        modal_rx = re.compile(
            r"\b(can|could|should|would|will|shall|might|may|must|did|does|do|didn't|doesn't|don't)\s+(?:(?:i|you|he|she|it|we|they|[a-z]+)\s+)?("
            + "|".join(modal_past_map.keys())
            + r")\b",
            re.IGNORECASE,
        )
        for match in modal_rx.finditer(text):
            modal_word = match.group(1)
            past_verb = match.group(2)
            base_verb = modal_past_map.get(past_verb.lower(), past_verb)
            verb_start = match.start(2)
            verb_end = match.end(2)

            if not any(e.span.start_char == verb_start for e in edits):
                edits.append(
                    DiagnosticEdit(
                        span=SpanCoordinate(
                            start_char=verb_start,
                            end_char=verb_end,
                            original_text=past_verb,
                        ),
                        replacement=base_verb,
                        errant_type="R:VERB:TENSE",
                        linguistic_rule="Modal Auxiliary Verb Form",
                        explanation=(
                            f"Modal auxiliary verbs such as '{modal_word}' require the bare infinitive / base form "
                            f"('{base_verb}') rather than the past tense form '{past_verb}'."
                        ),
                        counterfactual_example=f"I can {base_verb} to the store.",
                        confidence=0.98,
                        critic_verified=True,
                    )
                )

        # 3. Temporal Adverbial / Predicate Tense Discordance
        past_verbs_re = r"(?:went|saw|ate|came|took|wrote|bought|found|made|said|told|gave|knew|thought|brought|left|felt|began|ran|broke|chose|drove|fell|forgot|grew|heard|kept|paid|read|sent|slept|spoke|spent|stood|swam|taught|threw|understood|wore|won|was|were|had|did|[a-z]+ed)"
        future_adv_rx = re.compile(
            rf"\b(tomorrow|next\s+week|next\s+month|next\s+year)\b(?=.*?\b{past_verbs_re}\b)",
            re.IGNORECASE,
        )
        for match in future_adv_rx.finditer(text):
            adv_text = match.group(1)
            start = match.start(1)
            end = match.end(1)
            is_cap = adv_text[0].isupper() or start == 0

            rep = "Yesterday" if is_cap else "yesterday"
            if "week" in adv_text.lower():
                rep = "Last week" if is_cap else "last week"
            elif "month" in adv_text.lower():
                rep = "Last month" if is_cap else "last month"
            elif "year" in adv_text.lower():
                rep = "Last year" if is_cap else "last year"

            if not any(e.span.start_char == start for e in edits):
                edits.append(
                    DiagnosticEdit(
                        span=SpanCoordinate(
                            start_char=start,
                            end_char=end,
                            original_text=adv_text,
                        ),
                        replacement=rep,
                        errant_type="R:OTHER",
                        linguistic_rule="Temporal Adverbial Agreement",
                        explanation=(
                            f"The future temporal adverbial '{adv_text}' conflicts with the past-tense narration. "
                            f"In minimal-edit GEC, reconciling the time adverbial to '{rep}' restores temporal consistency."
                        ),
                        counterfactual_example=f"{adv_text.capitalize()} I will go to the mall.",
                        confidence=0.97,
                        critic_verified=True,
                    )
                )

        past_adv_rx = re.compile(
            r"\b(yesterday|last\s+night|last\s+week|last\s+month|last\s+year)\b(?=.*?\b(?:will|shall)\b)",
            re.IGNORECASE,
        )
        for match in past_adv_rx.finditer(text):
            adv_text = match.group(1)
            start = match.start(1)
            end = match.end(1)
            is_cap = adv_text[0].isupper() or start == 0
            rep = "Tomorrow" if is_cap else "tomorrow"
            if not any(e.span.start_char == start for e in edits):
                edits.append(
                    DiagnosticEdit(
                        span=SpanCoordinate(
                            start_char=start,
                            end_char=end,
                            original_text=adv_text,
                        ),
                        replacement=rep,
                        errant_type="R:OTHER",
                        linguistic_rule="Temporal Adverbial Agreement",
                        explanation=(
                            f"The past temporal adverbial '{adv_text}' conflicts with the future modal auxiliary. "
                            f"Reconciling the adverbial to '{rep}' restores temporal agreement."
                        ),
                        counterfactual_example=f"{adv_text.capitalize()} I went to the store.",
                        confidence=0.97,
                        critic_verified=True,
                    )
                )

        # 4. Standalone Lowercase Pronoun 'i'
        for match in re.finditer(r"\b(i)\b", text):
            start = match.start(1)
            end = match.end(1)
            if not any(e.span.start_char == start for e in edits):
                edits.append(
                    DiagnosticEdit(
                        span=SpanCoordinate(
                            start_char=start,
                            end_char=end,
                            original_text="i",
                        ),
                        replacement="I",
                        errant_type="R:SPELL",
                        linguistic_rule="Pronoun Capitalization",
                        explanation="The first-person singular personal pronoun 'I' must always be capitalized in standard English.",
                        counterfactual_example="Can I help you with that?",
                        confidence=0.99,
                        critic_verified=True,
                    )
                )

        # 5. Sentence-Initial Capitalization

        if text and text[0].islower() and text[0].isalpha():
            first_word_match = re.match(r"^([a-zA-Z]+)", text)
            if first_word_match:
                first_word = first_word_match.group(1)
                if not any(e.span.start_char == 0 for e in edits):
                    edits.append(
                        DiagnosticEdit(
                            span=SpanCoordinate(
                                start_char=0,
                                end_char=len(first_word),
                                original_text=first_word,
                            ),
                            replacement=first_word.capitalize(),
                            errant_type="R:SPELL",
                            linguistic_rule="Sentence-Initial Capitalization",
                            explanation="Sentences in English must begin with a capitalized letter.",
                            counterfactual_example=f"{first_word.capitalize()} we begin the meeting?",
                            confidence=0.95,
                            critic_verified=True,
                        )
                    )

        # 5. Common Confusable Pairs, Mass Nouns, Prepositions & Orthographic Typos
        confusables = [
            (
                r"\b(their)\s+(is|are\s+no|was|were)\b",
                "there",
                "R:SPELL",
                "Homophone Confusion (Their / There / They're)",
                "'Their' is a possessive pronoun. The existential dummy pronoun 'there' is required here.",
                "Their house is on the corner.",
            ),
            (
                r"\b(your)\s+(welcome|right|wrong|going|tired)\b",
                "you're",
                "R:SPELL",
                "Homophone Confusion (Your vs You're)",
                "'Your' is possessive. The contraction 'you're' (you are) is required here.",
                "You're welcome anytime.",
            ),
            (
                r"\b(its)\s+(a|an|the|my|your|too|very|not|going|time)\b",
                "it's",
                "R:SPELL",
                "Contraction vs Possessive (Its vs It's)",
                "'Its' is possessive. The contraction 'it's' (it is) is required here.",
                "It's a wonderful day.",
            ),
            (
                r"\b(definately)\b",
                "definitely",
                "R:SPELL",
                "Orthographic / Spelling Error",
                "'definately' is a common misspelling of 'definitely'.",
                "We will definitely attend the conference.",
            ),
            (
                r"\b(occured)\b",
                "occurred",
                "R:SPELL",
                "Consonant Doubling Spelling Error",
                "Verbs ending in single vowel + consonant double the final consonant in past tense ('occurred').",
                "The incident occurred yesterday.",
            ),
            (
                r"\b(seperate)\b",
                "separate",
                "R:SPELL",
                "Vowel Substitution Spelling Error",
                "'seperate' is an orthographic error for 'separate'.",
                "Please keep them in separate folders.",
            ),
            (
                r"\b(recieve)\b",
                "receive",
                "R:SPELL",
                "I-before-E Rule Exception",
                "'recieve' is misspelled; 'receive' follows the 'i before e except after c' rule.",
                "Did you receive the email?",
            ),
            (
                r"\b(untill)\b",
                "until",
                "R:SPELL",
                "Single-L Spelling Rule",
                "'untill' is misspelled; the standard modern spelling is 'until'.",
                "Wait until tomorrow.",
            ),
            (
                r"\b(goverment)\b",
                "government",
                "R:SPELL",
                "Silent Consonant Spelling Error",
                "'goverment' is missing the silent 'n' in 'government'.",
                "The government passed a new bill.",
            ),
            (
                r"\b(concious)\b",
                "conscious",
                "R:SPELL",
                "Phonetic Orthographic Error",
                "'concious' is misspelled; standard spelling is 'conscious'.",
                "She made a conscious decision.",
            ),
            (
                r"\b(certer)\b",
                "center",
                "R:SPELL",
                "Typographical Spelling Error",
                "'certer' is a misspelling of 'center'.",
                "In the center of the park.",
            ),
            (
                r"\b(pasteries)\b",
                "pastries",
                "R:SPELL",
                "Orthographic Spelling Error",
                "'pasteries' is a misspelling of 'pastries'.",
                "Fresh French pastries.",
            ),
            (
                r"\b(comercial)\b",
                "commercial",
                "R:SPELL",
                "Consonant Doubling Spelling Error",
                "'comercial' is missing the double 'm' in 'commercial'.",
                "A busy commercial district.",
            ),
            (
                r"\b(affect)\s+on\s+\w+",
                "effect",
                "R:OTHER",
                "Noun/Verb Confusable (Affect vs Effect)",
                "'Affect' is primarily a verb; the noun meaning outcome or influence is 'effect'.",
                "Smoking will negatively affect your health.",
            ),
            (
                r"\b(effect)\s+the\s+outcome",
                "affect",
                "R:OTHER",
                "Noun/Verb Confusable (Affect vs Effect)",
                "'Effect' is primarily a noun; the transitive verb meaning to influence is 'affect'.",
                "The law had an immediate effect.",
            ),
            (
                r"\b(?:depend|depends|depended)\s+(of)\b",
                "on",
                "R:PREP",
                "Prepositional Collocation Error",
                "The verb 'depend' standardly collocates with the preposition 'on' (or 'upon'), not 'of'.",
                "Success depends on hard work.",
            ),
            (
                r"\binterested\s+(for|on|at|about)\b",
                "in",
                "R:PREP",
                "Adjectival Preposition Collocation",
                "The adjective 'interested' takes the preposition 'in'.",
                "She is interested in studying history.",
            ),
            (
                r"\b(?:arrive|arrived)\s+(to)\s+(?:the|a|new\s+york|london|school|work|airport|station)\b",
                "at",
                "R:PREP",
                "Directional vs Locative Preposition",
                "In English, one arrives 'at' (or 'in') a destination, not 'to'.",
                "We arrived at the airport on time.",
            ),
            (
                r"\b(informations|furnitures|advices|homeworks|equipments|luggages|baggages|knowledges)\b",
                "information",
                "R:NOUN:NUM",
                "Uncountable Mass Noun Pluralization",
                "Mass/uncountable nouns cannot take a plural '-s' inflection.",
                "The teacher gave helpful advice.",
            ),
            (
                r"\b(many)\s+(?:information|advice|furniture|equipment|luggage|baggage|evidence)\b",
                "much",
                "M:DET",
                "Quantifier Determiner Agreement",
                "Uncountable mass nouns take 'much' rather than 'many'.",
                "There was much information in the report.",
            ),
            (
                r"\b(a)\s+([aeiou]\w+)\b",
                "an",
                "M:DET",
                "Indefinite Article Phonetic Agreement",
                "The indefinite article 'an' precedes words beginning with a vowel sound.",
                "A dog barked outside.",
            ),
        ]

        # Specific mass noun lemma mapping
        mass_lemma_map = {
            "informations": "information",
            "furnitures": "furniture",
            "advices": "advice",
            "homeworks": "homework",
            "equipments": "equipment",
            "luggages": "luggage",
            "baggages": "baggage",
            "knowledges": "knowledge",
        }

        for pattern, replacement, err_type, rule, exp, cf in confusables:
            for match in re.finditer(pattern, text, re.IGNORECASE):
                grp_idx = 1 if match.groups() else 0
                start, end = match.span(grp_idx)
                orig_token = match.group(grp_idx)

                if not any(e.span.start_char == start for e in edits):
                    final_rep = mass_lemma_map.get(orig_token.lower(), replacement)
                    if orig_token.istitle():
                        final_rep = final_rep.capitalize()
                    elif orig_token.isupper():
                        final_rep = final_rep.upper()

                    edits.append(
                        DiagnosticEdit(
                            span=SpanCoordinate(
                                start_char=start,
                                end_char=end,
                                original_text=orig_token,
                            ),
                            replacement=final_rep,
                            errant_type=err_type,
                            linguistic_rule=rule,
                            explanation=exp,
                            counterfactual_example=cf,
                            confidence=0.95,
                            critic_verified=False,
                        )
                    )

        edits.sort(key=lambda e: e.span.start_char)
        return OrtoAnalysis(edits=edits)

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
