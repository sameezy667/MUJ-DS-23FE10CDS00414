# Orto — Code Directory Structure & Execution Guide

## Module Organization
This folder provides direct entry points and execution scripts mapping to the core architecture:

1. **`orto/` — Core Python Package:**
   - `core/`: Universal Dependency Parser, Non-destructive Tokenizer, Reverse-Offset Patcher, Universal Linguistic Fallback Engine.
   - `critic/`: Symbolic Critic for invariant assertions (Subject-Verb Agreement, Tree Connectivity, Self-Refinement).
   - `llm/`: Structured decoding client, multi-provider model cascading (OpenRouter/OpenAI/Gemini), prompt templates.
   - `ml/`: Feature extractor, logistic regression confidence classifier, invocation router.
   - `lm/`: Laplace-smoothed N-Gram language model for perplexity & fluency delta scoring.
   - `style/`: Stylometric analyzer (Burstiness, Passive density) and AI cadence naturalizer.
   - `pipeline.py`: Main `OrtoEngine` orchestrator.

2. **`backend/` — REST API Service:**
   - `server.py`: FastAPI server serving endpoints `/api/v1/analyze`, `/api/v1/style/analyze`, `/api/v1/style/humanize`, `/api/v1/health` with OWASP security headers and rate limiting.

3. **`frontend/` — React / Vite Web Client:**
   - Modern React + TypeScript interface for real-time interactive diagnosis.

4. **`app.py` — Streamlit Diagnostic Dashboard:**
   - Interactive Streamlit dashboard with span highlight visualization, model selector, diagnostic cards, and stylometry analytics.

---

## Quick Execution Scripts

- **Run CLI Diagnosis:**
  ```bash
  python code/run_pipeline.py "The box of vintage records were heavy."
  ```

- **Run FastAPI REST Server:**
  ```bash
  python code/run_server.py
  ```

- **Run Streamlit Dashboard:**
  ```bash
  python code/run_app.py
  ```
