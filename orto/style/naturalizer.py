"""
@file naturalizer.py
@description Re-rhythms monotonous sentence cadences and replaces synthetic clichés with organic phrasing
@module orto/style
"""

from typing import List, Optional
from orto.llm.client import LLMClient
from orto.llm.prompts import load_prompts_config
from orto.style.analyzer import StyleAnalyzer
from orto.style.schemas import StyleAnalysisResult, StyleRewriteSuggestion


DEFAULT_NATURALIZER_SYSTEM_PROMPT = """You are Orto's Stylometry & Naturalness Re-Rhythmer.

Your task is to revise text flagged for synthetic monotony or cliché LLM markers.

STRICT PRINCIPLES:
1. CADENCE VARIATION (Burstiness): Mix short punchy clauses with longer explanatory ones to avoid robotic sentence length uniformity.
2. DE-CLICHÉ: Replace overused corporate/AI markers ("delve", "tapestry", "moreover", "beacon", "pivotal", "vital role", "testament") with organic, concrete words.
3. SEMANTIC FIDELITY: Never alter the author's underlying meaning, facts, or technical accuracy.
4. SURGICAL PRECISION: Avoid unnecessary rewrites.
"""

_PROMPTS_MAP = load_prompts_config()
NATURALIZER_SYSTEM_PROMPT: str = _PROMPTS_MAP.get(
    "naturalizer_system_prompt", DEFAULT_NATURALIZER_SYSTEM_PROMPT
).strip()



class StyleNaturalizer:
    """
    Applies stylometric re-rhythming and de-clichéing to enhance cadence variety
    and eliminate synthetic hallmarks.
    """

    def __init__(
        self,
        analyzer: Optional[StyleAnalyzer] = None,
        llm_client: Optional[LLMClient] = None,
    ) -> None:
        """
        Initializes the StyleNaturalizer.

        Args:
            analyzer: StyleAnalyzer instance.
            llm_client: LLMClient instance for natural rephrasing.
        """
        self.analyzer = analyzer or StyleAnalyzer()
        self.llm_client = llm_client or LLMClient()

    def naturalize(self, text: str) -> str:
        """
        Re-rhythms and polishes the input text to achieve human cadence and eliminate clichés.

        Args:
            text: Raw input text.

        Returns:
            Polished naturalized string.
        """
        if not text or not text.strip():
            return text

        # 1. Attempt LLM-powered dynamic naturalization if available
        if not self.llm_client.mock_mode and self.llm_client._openai_client is not None:
            cache_key = self.llm_client._get_cache_key(text, mode="humanize")
            if cache_key in self.llm_client._cache:
                cached = self.llm_client._cache[cache_key]
                if isinstance(cached, str) and cached.strip():
                    return cached.strip()

            prompt = f"""Target Text:
"{text}"

Task:
Re-rhythm and humanize this text.
1. Eliminate robotic, synthetic phrases and AI tropes (e.g., "by construction", "is defined by", "delve", "tapestry", "crucial", "testament to", "gates on", "surface that instead", etc.).
2. Vary sentence lengths with natural human burstiness (mix punchy short statements with clear explanatory sentences).
3. Transform stiff passive or repetitive copular chains ("X is Y. A is B.") into vivid, active, organic prose.
4. Maintain 100% of the factual accuracy, technical concepts, and logical points of the original author.
5. Return ONLY the rewritten text without conversational preamble or markdown backticks.
"""
            try:
                response = self.llm_client._openai_client.chat.completions.create(
                    model=self.llm_client.model,
                    temperature=0.3,
                    max_tokens=1000,
                    seed=self.llm_client.seed,
                    messages=[
                        {"role": "system", "content": NATURALIZER_SYSTEM_PROMPT},
                        {"role": "user", "content": prompt},
                    ],
                )
                output_text = (response.choices[0].message.content or "").strip()
                # Clean any outer quotes or code fences
                if output_text.startswith("```") and output_text.endswith("```"):
                    output_text = output_text.strip("`").strip()
                if output_text.startswith('"') and output_text.endswith('"'):
                    output_text = output_text[1:-1].strip()

                if output_text:
                    self.llm_client._cache[cache_key] = output_text
                    self.llm_client._save_cache()
                    return output_text
            except Exception:
                pass

        # 2. Rule-based / Offline Naturalization & De-clichéing
        analysis: StyleAnalysisResult = self.analyzer.analyze(text)

        # Apply surgical cliché substitutions
        result = text
        sorted_suggestions = sorted(
            analysis.suggestions,
            key=lambda s: s.span.start_char,
            reverse=True,
        )

        for sugg in sorted_suggestions:
            start = sugg.span.start_char
            end = sugg.span.end_char
            if result[start:end] == sugg.span.original_text:
                result = result[:start] + sugg.suggestion + result[end:]

        # If no clichés were matched but text has formulaic markers or stiff cadence
        if result == text:
            # Apply contextual phrase softening
            phrase_replacements = [
                (r"\bis defined by\b", "depends on"),
                (r"\bby construction\b", "by design"),
                (r"\bgates on\b", "filters on"),
                (r"\bfabricated number\b", "arbitrary number"),
                (r"\bsurface that instead\b", "highlight that instead"),
                (r"\bserves as a testament to\b", "demonstrates"),
                (r"\bplays a pivotal role in\b", "is essential for"),
                (r"\bdelving deep into\b", "exploring"),
                (r"\brich tapestry of\b", "landscape of"),
            ]
            import re
            for pat, repl in phrase_replacements:
                result = re.sub(pat, repl, result, flags=re.IGNORECASE)

        return result
