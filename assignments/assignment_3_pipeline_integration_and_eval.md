# Assignment 3: Pipeline Integration, Evaluation & Stylometry

## 1. Overview & Objective
This assignment details the end-to-end integration of the Orto GEC Engine, multi-model cascading fallback, stylometric naturalization, REST API server, interactive Streamlit frontend, and benchmarking evaluation across BEA-2019 and CoNLL-2014.

## 2. End-to-End Pipeline Orchestration
- `OrtoEngine` (`orto/pipeline.py`) coordinates:
  1. Syntax Prior Extraction
  2. LLM Hypothesis Generation with Multi-Provider Fallback
  3. Universal Linguistic Fallback Engine
  4. Symbolic Critic Invariant Check & 1-Turn Reflection
  5. ML Reranking & Conflict Resolution
  6. Reverse-Offset In-Memory Patching
  7. Telemetry & Stylometry Analysis

## 3. Stylometry & AI Cadence Analysis
- `StyleAnalyzer` (`orto/style/analyzer.py`):
  - **Burstiness Score ($B$):** Measures sentence length variation:
    $$B = \frac{\sigma}{\mu} = \frac{\sqrt{\frac{1}{N}\sum (L_i - \mu)^2}}{\frac{1}{N}\sum L_i}$$
    ($B > 0.5$ indicates authentic human sentence cadence; $B < 0.2$ indicates uniform synthetic rhythm).
  - **Passive Voice Ratio:** Computes proportion of clauses with passive auxiliaries (`auxpass`).
  - **Synthetic AI Markers:** Detects overused LLM clichés (e.g., *"delve"*, *"rich tapestry"*, *"crucial to foster"*, *"beacon of"*, *"vital role"*).

## 4. Evaluation Metrics
Evaluated with official $F_{0.5}$ metric (weighting precision twice as heavily as recall, standard for GEC):
$$F_{0.5} = \frac{(1 + 0.5^2) \cdot P \cdot R}{0.5^2 \cdot P + R} = \frac{1.25 \cdot P \cdot R}{0.25 \cdot P + R}$$

## 5. Automated Test Suite
- 65 comprehensive unit and integration tests passing in Pytest across all modules.
