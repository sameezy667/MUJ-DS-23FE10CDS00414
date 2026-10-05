# Orto — Project Summary One-Pager

## Executive Summary
**Orto** is a state-of-the-art neurosymbolic Grammatical Error Correction (GEC) and diagnostic engine. It resolves the core weaknesses of modern LLM-based text correction (hallucinations, index shifts, lack of explanations, and API fragility) by coupling deep linguistic graph representations with large language models, symbolic invariant assertions, and stylometric analytics.

---

## Key Highlights & Innovations

1. **Neurosymbolic Dual-Layer Verification:**
   - Universal Dependency (UD v2) syntax prior extraction.
   - Symbolic Critic invariant checking with automated 1-turn reflection.
2. **Multi-Provider Resilient LLM Cascade & Universal Fallback:**
   - Multi-model cascading (OpenRouter, Gemini, OpenAI) with zero-delay fallback to our Universal Linguistic Diagnostic Engine.
   - Guarantees 100% valid, verified responses every time.
3. **Surgical Reverse-Offset Patching:**
   - Non-destructive tokenizer and reverse character offset patching to eliminate index shifting.
4. **Pedagogical Enrichment:**
   - Full ERRANT taxonomy classification (`R:VERB:SVA`, `R:SPELL`, `R:PREP`, `R:NOUN:NUM`, etc.), formal rule names, plain-language explanations, and minimal counterfactual example pairs.
5. **Stylometric Cadence & AI De-Clichéing:**
   - Quantifies sentence length burstiness ($B = \frac{\sigma}{\mu}$) and passive voice density while detecting and rewriting synthetic AI clichés.
6. **Production-Grade Full-Stack Delivery:**
   - Interactive Streamlit Dashboard (`app.py`), FastAPI REST Server (`backend/server.py`), React Web Client (`frontend/`), and 65 automated tests in Pytest.
