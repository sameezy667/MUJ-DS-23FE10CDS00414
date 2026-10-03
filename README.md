# ✨ Orto: Neurosymbolic Grammatical Error Correction & Diagnostic Engine

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/)
[![React 19](https://img.shields.io/badge/React-19-61DAFB.svg)](https://react.dev/)
[![TypeScript](https://img.shields.io/badge/TypeScript-5.x-3178C6.svg)](https://www.typescriptlang.org/)
[![License: Apache 2.0](https://img.shields.io/badge/License-Apache_2.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)
[![Tests: Pytest](https://img.shields.io/badge/tests-26%20passed-brightgreen.svg)](https://docs.pytest.org/)
[![GEC Metric: F0.5](https://img.shields.io/badge/F0.5%20Benchmark-73.3%25-green.svg)](benchmarks/)

**Orto** is a hybrid, neurosymbolic Grammatical Error Correction (GEC) and linguistic diagnostic engine paired with a **React + TypeScript Diagnostic Studio**. It bridges classical Universal Dependency parsing (via **spaCy**) with constrained LLM structured decoding (via **OpenAI / Pydantic**) and an automated **Symbolic Critic**.

Unlike generic LLM rewrite prompts that alter authorial voice and hallucinate grammar rules, Orto guarantees:
1. **Surgical Edit Locality:** Mutations are strictly confined to minimal character spans `[start_char, end_char]`.
2. **Deterministic Reverse-Offset Patching:** Edits apply in descending index order, completely preventing offset drift.
3. **ERRANT Taxonomy Compliance:** Every edit is classified into standard categories (`R:VERB:SVA`, `R:SPELL`, `R:NOUN:NUM`, `R:PREP`, `M:DET`, etc.).
4. **Pedagogical Explanations:** Emits formal rule citations, diagnostic explanations, and counterfactual minimal pairs.
5. **Symbolic Verification & 1-Turn Reflection:** Asserts morphosyntactic Subject-Verb Agreement on virtual patched sentences before presenting edits.
6. **React Diagnostic Studio:** High-performance interactive UI featuring real-time client-side patching, color-coded error badges, diagnostic cards, and dependency tree inspection.

---

## 🏗️ System Architecture

```text
                           ┌────────────────────────────────┐
                           │        Raw User String         │
                           └───────────────┬────────────────┘
                                           │
                                           ▼
                           ┌────────────────────────────────┐
                           │    Stage 1: Syntax Engine      │
                           │   (spaCy Universal Dependency) │
                           │  • Offset-preserving tokens    │
                           │  • (Head, Dep, Child) edges    │
                           │  • Morphological feature sets  │
                           └───────────────┬────────────────┘
                                           │
                               (Text + Syntactic Graph)
                                           │
                                           ▼
                           ┌────────────────────────────────┐
                           │    Stage 2: LLM Diagnostics   │
                           │ (Constrained Structured Schema)│
                           │  • Exact character spans       │
                           │  • Minimal token replacement   │
                           │  • ERRANT error taxonomy       │
                           │  • Counterfactual minimal pair │
                           └───────────────┬────────────────┘
                                           │
                              (Candidate Diagnostic Edits)
                                           │
                                           ▼
                           ┌────────────────────────────────┐
                    No     │    Stage 3: Symbolic Critic    │
      ┌────────────────────┤  (In-Memory Morphosyntax Check)│
      │                    │  • SVA head-number alignment   │
      │                    │  • Tree connectivity check     │
      ▼                    └───────────────┬────────────────┘
┌──────────────┐                           │ Yes
│  1x Feedback │                           ▼
│  Refinement  │           ┌────────────────────────────────┐
│  Retry Loop  │           │   Stage 3B: ML Router Filter   │
└──────────────┘           │  (Trained Logistic / GB Model) │
                           │  • Features: Critic, LM Delta, │
                           │    SVA flag, token lengths     │
                           └───────────────┬────────────────┘
                                           │
                                           ▼
                           ┌────────────────────────────────┐
                           │   Stage 4: Verified Payload    │
                           │  • In-memory reverse patcher   │
                           │  • React Diagnostic Studio     │
                           │  • REST API / CLI evaluation   │
                           └────────────────────────────────┘
```

---

## 🧩 System Components & Training Provenance

To clearly specify how each component is built and whether it is trained, pre-trained, or rule-based:

| Component | Provenance & Implementation | Training / Pre-Training Corpus | Role in Orto Pipeline |
| :--- | :--- | :--- | :--- |
| **Bigram/Trigram Language Model (`orto/lm/`)** | **Trained from Scratch** (MLE with Laplace Smoothing, $k=1.0$) | BEA-2019 Training Corpus (30,000 sentences, 556,686 tokens, $\|V\|=9,935$, 151,355 bigrams from `ABC.train.gold.bea19.m2`) | Evaluates sentence log-likelihood, computes edit fluency delta ($\Delta \text{LL}$), and flags degenerate token mutations. Note: the training corpus is authentic second-language learner text from the BEA dataset. |
| **Confidence Classifier & Router (`orto/ml/`)** | **Trained from Scratch** (`LogisticRegression` via `scikit-learn`) | BEA-2019 Train Split (`data/bea19_train_subset.m2`, 500 sentences, 396 real LLM candidates) | Supervised tabular classifier trained on 10 linguistic, structural, LM fluency, and critic verification features to predict $P(\text{Valid Edit})$ and filter false alarms. |
| **Dynamic Few-Shot Retriever (`orto/fewshot/`)** | **Heuristic Similarity Engine** (Jaccard + Syntactic SVA anomaly matching) | Curated Bank of Minimal-Pair Demonstrations (`orto/fewshot/bank.py`) | Dynamically indexes and retrieves top-$k$ pedagogical minimal pairs per sentence error type for few-shot prompt injection. |
| **Universal Dependency Parser (`orto/core/`)** | **Pre-Trained** (spaCy `en_core_web_sm` v3.8.0) | OntoNotes 5.0 / Universal Dependencies | Tokenization, part-of-speech tagging, morphological feature extraction, and directed dependency trees. |
| **Diagnostic LLM (`orto/llm/`)** | **Pre-Trained Model** (`openai/gpt-4o-mini` via OpenRouter) | General Web Pre-Training + Instruction Tuning | Generates structured diagnostic proposals with exact character spans, pedagogical explanations, and counterfactuals. |
| **Symbolic Critic (`orto/critic/`)** | **Deterministic Rule-Based Engine** | Universal Grammatical Invariants (Subject-Verb Agreement, Tree Connectivity) | Applies candidate edits virtually in-memory, asserts morphosyntactic invariants, and triggers 1-turn feedback reflection. |
| **Reverse-Offset Patcher (`orto/core/`)** | **Deterministic Algorithm** | Algorithmic (Descending Span Order) | Computes conflict-free non-overlapping string mutations and applies character replacement offsets without drift. |

---

## 📁 Repository Layout

```text
orto/
├── context.md                 # Single source of truth ledger
├── pyproject.toml             # Build & packaging configuration
├── requirements.txt           # Pinned production & dev dependencies
├── Makefile                   # Automation tasks (install, build-frontend, dev-frontend, test)
├── README.md                  # Comprehensive system documentation
├── .env.example               # Environment variable templates
├── backend/
│   ├── __init__.py
│   └── server.py              # FastAPI REST server & static build mount
├── frontend/                  # React + TypeScript + Vite Studio
│   ├── package.json
│   ├── vite.config.ts         # Vite configuration with API proxy
│   ├── index.html
│   └── src/
│       ├── types.ts           # TypeScript interfaces & contracts
│       ├── index.css          # Glassmorphic dark theme & ERRANT tokens
│       ├── App.tsx            # Main React Studio orchestrator
│       ├── main.tsx
│       └── components/
│           ├── Header.tsx                 # Brand bar & Symbolic Critic toggle
│           ├── InputWorkbench.tsx         # Raw text editor & quick presets
│           ├── SurgicalSpansViewer.tsx    # Color-coded interactive ERRANT span tokens
│           ├── PedagogicalCards.tsx       # Diagnostic cards with counterfactuals & toggles
│           ├── PatchedOutputViewer.tsx    # Real-time dynamically patched output & copy action
│           ├── SyntaxPriorsInspector.tsx  # spaCy dependency tree & SVA clause inspector
│           └── TelemetryFooter.tsx        # Pipeline latency & refinement metrics
├── data/
│   ├── sample_benchmark.jsonl # 10 challenging test cases across ERRANT classes
│   └── confusion_sets.json    # Confusable word pairs reference
├── orto/
│   ├── __init__.py
│   ├── pipeline.py            # Main orchestrator (Syntax -> LLM -> Critic -> Diff)
│   ├── core/
│   │   ├── __init__.py
│   │   ├── tokenizer.py       # Non-destructive offset tokenizer
│   │   ├── syntax_engine.py   # spaCy Universal Dependency & morphology extractor
│   │   └── patcher.py         # Reverse-offset in-memory string patcher
│   ├── llm/
│   │   ├── __init__.py
│   │   ├── schemas.py         # Pydantic models for structured output
│   │   ├── prompts.py         # Linguistically grounded prompt templates
│   │   └── client.py          # LLM API client wrapper (with offline fallback)
│   └── critic/
│       ├── __init__.py
│       └── verifier.py        # Symbolic morphosyntactic regression verifier
├── benchmarks/
│   ├── __init__.py
│   ├── evaluate.py            # Precision, Recall, and F_0.5 evaluation harness
│   └── run_ablations.py       # Baseline comparison (Zero-Shot vs Rules vs Hybrid)
├── tests/
│   ├── __init__.py
│   ├── test_tokenizer.py      # Non-destructive token and span tests
│   ├── test_syntax_engine.py  # Dependency & morphology extraction tests
│   ├── test_patcher.py        # Reverse-offset string patching tests
│   ├── test_critic.py         # SVA and regression verification tests
│   ├── test_pipeline.py       # End-to-end integration tests
│   └── test_server.py         # FastAPI REST endpoint tests
└── app.py                     # Streamlit alternative interface
```

---

## 🚀 Quickstart & Running the React Studio

### 1. Install Backend & Frontend Dependencies
```bash
make install
```

### 2. Option A: Run Backend Server with Built React Client
```bash
# Build React client bundle
make build-frontend

# Start FastAPI server on http://localhost:8000 (serves React app + API)
make run-server
```

### 3. Option B: Run React Dev Server with Hot Module Replacement
In terminal 1:
```bash
make run-server
```
In terminal 2:
```bash
make dev-frontend
# Opens Vite React dev studio on http://localhost:5173
```

---

## 🧪 Running Tests & Benchmarks

```bash
# Run full test suite (26 passing tests)
make test

# Run F_0.5 benchmark evaluation
make benchmark

# Run baseline ablation comparison
make ablations
```

---

## 📊 Benchmark & Empirical Evaluation (Official ERRANT $F_{0.5}$)

$$F_{0.5} = \frac{(1 + 0.5^2) \cdot \text{Precision} \cdot \text{Recall}}{(0.5^2 \cdot \text{Precision}) + \text{Recall}}$$

### A. BEA-2019 Dev Split (150 Sentences, 529 Gold Edits)
| Pipeline Configuration | $TP$ | $FP$ | $FN$ | Precision ($95\%$ CI) | Recall ($95\%$ CI) | $F_{0.5}$ ($95\%$ CI) | Latency |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **Baseline A: LLM-Only** | 82 | 155 | 447 | 34.60% [26.5%, 41.6%] | 15.50% [12.2%, 18.8%] | 27.76% [21.6%, 33.1%] | 338 ms |
| **Baseline B: Symbolic-Only** | 6 | 17 | 523 | 26.09% [9.1%, 50.0%] | 1.13% [0.4%, 2.2%] | 4.83% [1.5%, 9.2%] | 12 ms |
| **Proposed: Orto Full Pipeline** | **70** | **80** | **459** | **46.67% [36.4%, 54.9%]** | **13.23% [10.1%, 16.5%]** | **31.00% [24.4%, 37.1%]** | 362 ms |

### B. CoNLL-2014 Test Split (100 Sentences, 461 Gold Edits)
| Pipeline Configuration | $TP$ | $FP$ | $FN$ | Precision ($95\%$ CI) | Recall ($95\%$ CI) | $F_{0.5}$ ($95\%$ CI) | Latency |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **Baseline A: LLM-Only** | 41 | 35 | 420 | 53.95% [38.1%, 67.2%] | 8.89% [5.6%, 12.3%] | 26.80% [17.9%, 35.4%] | 315 ms |
| **Baseline B: Symbolic-Only** | 3 | 5 | 458 | 37.50% [0.0%, 75.0%] | 0.65% [0.0%, 1.4%] | 3.04% [0.0%, 6.5%] | 11 ms |
| **Proposed: Orto Full Pipeline** | **32** | **18** | **429** | **64.00% [46.5%, 78.6%]** | **6.94% [4.1%, 9.8%]** | **24.21% [15.4%, 32.0%]** | 344 ms |

---

## 🛡️ License
Distributed under the Apache 2.0 License.
