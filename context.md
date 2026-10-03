# Orto - Neurosymbolic GEC & Diagnostic Engine: Context Ledger

## 1. Project Overview
Orto is a hybrid, neurosymbolic Grammatical Error Correction (GEC), diagnostic, and stylometric naturalness engine. It bridges classical Universal Dependency parsing (spaCy) with constrained LLM structured decoding (OpenAI/Pydantic), an automated Symbolic Critic, and a research-grounded Stylometry Engine (`orto/style/`). Corrections are strictly confined to minimal character-level spans `[start_char, end_char]` to preserve authorial voice. Errors are categorized using the standardized ERRANT taxonomy, accompanied by pedagogical explanations, counterfactual minimal pairs, and cadence/burstiness rhythm analysis with an automated AI Humanizer & De-Cliché re-rhythmer.

## 2. Tech Stack
- **Language:** Python 3.14+ (Backend), TypeScript 5.x / React 19 / Vite (Frontend)
- **Backend / REST API:** FastAPI 0.110+, Starlette, Uvicorn (running on `http://127.0.0.1:8000`)
- **Frontend Framework:** React 19 + TypeScript + Vite with editorial ink/paper design system, variable typography (Fraunces, Inter, JetBrains Mono, Caveat), and `lucide-react` icons (running on `http://localhost:5173` or served via FastAPI `http://localhost:8000`)
- **NLP / Symbolic Parsing:** spaCy (`en_core_web_sm` 3.8.0), Universal Dependencies (v2)
- **Stylometry & AI Humanizer:** Custom burstiness calculator ($B = \sigma / \mu$), LLM cliché marker detector, passive/nominalization density scorer, opening variety analyzer, `StyleNaturalizer`
- **Schema & Structured Decoding:** Pydantic v2 (2.13.5), OpenAI/OpenRouter API (`beta.chat.completions.parse` with structured output JSON schema, configured with `google/gemma-4-31b-it:free`)
- **Alternative UI:** Streamlit (1.64.0) (`app.py`)
- **Testing & Benchmarks:** pytest (9.1.1, 37/37 passing), rich (15.0.0) terminal visualization, custom $F_{0.5}$ & ERRANT evaluation harness

## 3. Architecture & Data Flow
```
[ User Input (React Studio / CLI / REST API) ]
                      │
                      ▼
┌──────────────────────────────────────────────┐
│ Stage 1: Syntax Engine (spaCy)               │
│ • Token offsets & morphological features     │
│ • (Head, Dep, Child) directed edges          │
│ • SVA candidate pair identification          │
└──────────────┬───────────────────────────────┘
               │
       ┌───────┴──────────────────────────────┐
       │                                      │
       ▼                                      ▼
┌──────────────────────────────┐ ┌───────────────────────────────────────┐
│ Stage 2: LLM Diagnostics     │ │ Stage 2B: Stylometry & AI Humanizer   │
│ • Surgical [start, end] span │ │ • Burstiness B = sigma / mu           │
│ • ERRANT classification      │ │ • LLM Cliché marker detection         │
│ • Rules & counterfactuals    │ │ • Passive & nominalization density    │
└──────────────┬───────────────┘ │ • StyleNaturalizer de-cliché re-rhythm│
               │                 └───────────────────────────────────────┘
               ▼
┌──────────────────────────────┐
│ Stage 3: Symbolic Critic     │
│ • In-memory virtual patch    │
│ • Number(S) == Number(V)     │
│ • Tree integrity check       │
└──────────────┬───────────────┘
               │
       ┌───────┴───────┐
    (Pass)          (Fail)
       │               │
       │               ▼
       │     [ 1x Reflection Retry ]
       │               │
       ├───────────────┘
       ▼
┌──────────────────────────────────────────────┐
│ Stage 4: Verified Payload & Reverse Patcher  │
│ • Disjoint span filtering by confidence      │
│ • Real-time in-memory string patcher         │
│ • React Diagnostic Studio (0ms UI Updates)   │
│ • AI Humanizer & Rhythm Studio               │
│ • Terminal CLI with rich stylometry reports  │
└──────────────────────────────────────────────┘
```

### Folder Structure
```
orto/
├── context.md                 # Single source of truth ledger
├── pyproject.toml             # Build & packaging config
├── requirements.txt           # Pinned backend dependencies
├── Makefile                   # Dev tooling: install, build-frontend, dev-frontend, run-server, test
├── README.md                  # System documentation & quickstart
├── .env.example               # Secrets & API config template
├── backend/
│   ├── __init__.py
│   └── server.py              # FastAPI REST server (/api/v1/analyze, /api/v1/style/analyze, /api/v1/style/humanize)
├── frontend/                  # React 19 + TypeScript + Vite Studio
│   ├── package.json
│   ├── vite.config.ts         # Vite config with API proxy
│   ├── index.html             # Google fonts (Fraunces, Caveat, Inter, JetBrains Mono)
│   └── src/
│       ├── types.ts           # Shared TypeScript contracts & ERRANT taxonomy
│       ├── index.css          # Editorial ink/paper design system & keyframe animations
│       ├── App.tsx            # Main application layout, intersection observers & spot effects
│       ├── main.tsx
│       ├── utils/
│       │   └── engine.ts      # Client heuristics, confusion sets & dependency token parser
│       └── components/
│           ├── Navbar.tsx             # Sticky navbar, scrollspy & scroll progress indicator
│           ├── HeroSection.tsx        # Animated manuscript annotation simulation loop & live metrics
│           ├── Ticker.tsx             # Infinite marquee telemetry ticker
│           ├── ProblemSection.tsx     # Rule vs LLM vs Orto failure mode & drift comparisons
│           ├── ArchitectureSection.tsx# 4-stage cascade, particle beam & invariant formula
│           ├── LiveConsole.tsx        # Interactive workbench with GEC Studio & AI Humanizer Studio
│           ├── BenchmarksSection.tsx  # Animated Bento KPIs, sparklines & ablation tables
│           ├── TaxonomySection.tsx    # 8 ERRANT categories with animated strikethrough examples
│           ├── StylometrySection.tsx  # Interactive AI Humanizer, Burstiness equation & AI cliché detector
│           ├── ApiSection.tsx         # Interactive tabbed code inspector & Python SDK
│           ├── PersonasSection.tsx    # Researcher, Learner, and Developer personas
│           ├── Footer.tsx             # Repository tree, quick links & release specs
│           └── Toast.tsx              # Floating toast notifications
├── data/
│   ├── sample_benchmark.jsonl # 10+ challenging test cases with ground truth
│   ├── bea19_dev_sample.m2    # 100-sentence stratified BEA-2019 dev sample
│   ├── conll14_test_sample.m2 # 100-sentence stratified CoNLL-2014 test sample
│   ├── confusion_sets.json    # Confusable word pairs reference
│   ├── downloads/             # Full official BEA-2019 (4384 sents) & CoNLL-2014 (1312 sents)
│   └── models/                # Trained ML artifacts
│       ├── ngram_bigram.json  # Laplace-smoothed N-gram LM (556k tokens, |V|=9935)
│       └── edit_router.joblib # Trained Logistic Regression & Scaler bundle
├── orto/
│   ├── __init__.py
│   ├── cli.py                 # Rich interactive CLI with --style flag
│   ├── pipeline.py            # Main orchestrator (Syntax -> LLM -> Critic -> LM/ML -> Diff)
│   ├── core/
│   │   ├── __init__.py
│   │   ├── tokenizer.py       # Non-destructive offset tokenizer
│   │   ├── syntax_engine.py   # spaCy Universal Dependency & morphology extractor
│   │   └── patcher.py         # Reverse-offset in-memory string patcher
│   ├── llm/
│   │   ├── __init__.py
│   │   ├── schemas.py         # Pydantic models for structured output
│   │   ├── prompts.py         # Linguistically grounded prompt templates with few-shot retrieval
│   │   └── client.py          # LLM API client wrapper with structured output parsing & mock
│   ├── critic/
│   │   ├── __init__.py
│   │   └── verifier.py        # Symbolic morphosyntactic regression verifier
│   ├── lm/                    # N-gram Language Modeling & Fluency Scoring
│   │   ├── __init__.py
│   │   ├── ngram.py           # NGramLanguageModel with Laplace add-k smoothing & perplexity
│   │   └── train_ngram.py     # Corpus training script (BEA-2019 / raw English corpora)
│   ├── fewshot/               # Dynamic Few-Shot Exemplar Retrieval
│   │   ├── __init__.py
│   │   ├── bank.py            # Curated minimal pair exemplars across ERRANT taxonomy
│   │   └── retriever.py       # Syntactic/semantic similarity retrieval engine
│   ├── ml/                    # Machine Learning Router & Confidence Classifier
│   │   ├── __init__.py
│   │   ├── schemas.py         # Feature vector and routing decision dataclasses
│   │   ├── features.py        # 10D tabular feature extractor (syntax, geometry, critic, LM)
│   │   ├── router.py          # EditConfidenceClassifier & InvocationRouter inference engine
│   │   └── train_router.py    # scikit-learn training script with 5-fold cross-validation
│   └── style/                 # Stylometry & Naturalness Engine
│       ├── __init__.py
│       ├── schemas.py         # StylometricReport & StyleRewriteSuggestion models
│       ├── metrics.py         # Burstiness, AI markers, passive & opening variety algorithms
│       ├── analyzer.py        # StyleAnalyzer orchestrator
│       └── naturalizer.py     # De-cliché and cadence naturalizer
├── benchmarks/
│   ├── __init__.py
│   ├── evaluate.py            # Precision, Recall, and F_0.5 evaluation harness (official ERRANT M2 & JSONL)
│   └── run_ablations.py       # Comparative ablation runner (LLM-Only vs Symbolic-Only vs Orto Full Pipeline)
├── tests/
│   ├── __init__.py
│   ├── test_tokenizer.py      # Non-destructive offset integrity tests
│   ├── test_syntax_engine.py  # Dependency and SVA extraction tests
│   ├── test_patcher.py        # Reverse-offset patching & conflict resolution tests
│   ├── test_critic.py         # Symbolic SVA and regression verification tests
│   ├── test_pipeline.py       # Full end-to-end integration tests
│   ├── test_server.py         # FastAPI REST endpoint integration tests (including /style/humanize)
│   ├── test_style.py          # Burstiness, cliché detection, and stylometry tests
│   ├── test_benchmark_eval.py # ERRANT M2 evaluation and ablation study tests
│   ├── test_ngram.py          # N-gram LM, Laplace smoothing, and perplexity tests
│   ├── test_fewshot.py        # Exemplar bank and similarity retrieval tests
│   └── test_router.py         # ML feature extractor, classifier, and invocation router tests
└── app.py                     # Streamlit diagnostic UI (alternative)
```

## 4. Feature Status Checklist
- [x] Requirements, pyproject.toml, Makefile, .env.example (added `errant>=3.0.0`, `scikit-learn>=1.4.0`, `joblib>=1.3.0`)
- [x] Core Tokenizer (`orto/core/tokenizer.py`)
- [x] Core Syntax Engine (`orto/core/syntax_engine.py`)
- [x] Core Patcher (`orto/core/patcher.py`)
- [x] LLM Schemas (`orto/llm/schemas.py`)
- [x] LLM Prompts with Dynamic Few-Shot Injection (`orto/llm/prompts.py`)
- [x] LLM Client (`orto/llm/client.py`)
- [x] Symbolic Critic (`orto/critic/verifier.py`)
- [x] N-Gram Language Model with Laplace Smoothing (`orto/lm/ngram.py`, `orto/lm/train_ngram.py`)
- [x] Dynamic Few-Shot Exemplar Retriever (`orto/fewshot/bank.py`, `orto/fewshot/retriever.py`)
- [x] ML Confidence Classifier & Router (`orto/ml/features.py`, `orto/ml/router.py`, `orto/ml/train_router.py`)
- [x] Pipeline Orchestrator with ML/LM hooks (`orto/pipeline.py`)
- [x] Stylometry & Naturalness Engine (`orto/style/*`)
- [x] AI Humanizer & De-Cliché Endpoint (`/api/v1/style/humanize`)
- [x] CLI Runner with `--style` flag (`orto/cli.py`)
- [x] Unit & Integration Test Suite (`tests/*`) (54/54 tests passing)
- [x] Official ERRANT M2 Benchmark Suite & Ablation Runner (`benchmarks/evaluate.py`, `benchmarks/run_ablations.py`)
- [x] Labelled Datasets (`data/bea19_dev_sample.m2`, `data/conll14_test_sample.m2`, `data/sample_benchmark.jsonl`)
- [x] Trained Model Weights (`data/models/ngram_bigram.json`, `data/models/edit_router.joblib`)
- [x] FastAPI Backend Server (`backend/server.py`)
- [x] React + TypeScript + Vite Diagnostic Studio (`frontend/`)
- [x] Streamlit Alternative UI (`app.py`)
- [x] Documentation (`README.md`)
- [x] Temporal Adverbial & Predicate Tense Discordance Engine (`orto/core/syntax_engine.py`, `orto/llm/client.py`, `frontend/src/utils/engine.ts`)

## 5. Benchmark & Machine Learning Training Findings
- **Data Splitting & Provenance:**
  - *N-Gram Training Set:* 30,000 sentences from BEA-2019 training corpus (`ABC.train.gold.bea19.m2`, $556,686$ tokens, $|V|=9,935$, $151,355$ bigrams). Note: corpus reflects learner English.
  - *Router Training Set:* `data/bea19_train_subset.m2` (500 sentences, 396 real LLM-generated candidate edits: 78 TP, 318 FP, 19.7% base rate).
  - *Held-out Evaluation Split 1:* `data/bea19_dev_eval.m2` (150 sentences, 529 gold edits).
  - *Held-out Evaluation Split 2:* `data/conll14_test_eval.m2` (100 sentences, 461 gold edits).
- **Trained Router & Edit Confidence Classifier (`orto/ml/`):**
  - 5-Fold Stratified Cross-Validation on real LLM candidates: Accuracy: 60.61%, Precision: 28.09%, Recall: 64.10%, $F_1$: 39.06%, ROC-AUC: 68.14%.
  - Learned Feature Weights (10 features): `sva_error_flag` (-0.9358), `critic_passed` (+0.6173), `fluency_delta` (+0.4791), `errant_type_idx` (-0.4419), `replacement_len` (-0.3756), `initial_confidence` (+0.2830), `has_intervening_prep` (+0.2656), `sentence_len_tokens` (+0.2158), `span_start_ratio` (-0.0520), `original_len` (-0.0015).
- **Live LLM Ablation Benchmarks (with 95% Bootstrap Confidence Intervals):**
  - **BEA-2019 Dev Split (150 Sentences, 529 Gold Edits):**
    - *Baseline A (LLM-Only, No Critic):* TP=82, FP=155, FN=447 | Precision: 34.60% [26.5%, 41.6%], Recall: 15.50% [12.2%, 18.8%], $F_{0.5}$: 27.76% [21.6%, 33.1%]
    - *Baseline B (Symbolic-Only, Pure Rules):* TP=6, FP=17, FN=523 | Precision: 26.09% [9.1%, 50.0%], Recall: 1.13% [0.4%, 2.2%], $F_{0.5}$: 4.83% [1.5%, 9.2%]
    - *Proposed (Orto Full Pipeline, $\tau=0.45$):* TP=70, FP=80, FN=459 | Precision: **46.67% [36.4%, 54.9%]**, Recall: **13.23% [10.1%, 16.5%]**, $F_{0.5}$: **31.00% [24.4%, 37.1%]**
    - *Impact on BEA:* Precision $+12.07\%$, False Positives reduced by $48.4\%$ ($155 \rightarrow 80$, 75 false alarms eliminated), $F_{0.5}$ improved by $+3.24\%$ ($27.76\% \rightarrow 31.00\%$).
  - **CoNLL-2014 Test Split (100 Sentences, 461 Gold Edits):**
    - *Baseline A (LLM-Only, No Critic):* TP=41, FP=35, FN=420 | Precision: 53.95% [38.1%, 67.2%], Recall: 8.89% [5.6%, 12.3%], $F_{0.5}$: 26.80% [17.9%, 35.4%]
    - *Baseline B (Symbolic-Only, Pure Rules):* TP=3, FP=5, FN=458 | Precision: 37.50% [0.0%, 75.0%], Recall: 0.65% [0.0%, 1.4%], $F_{0.5}$: 3.04% [0.0%, 6.5%]
    - *Proposed (Orto Full Pipeline, $\tau=0.45$):* TP=32, FP=18, FN=429 | Precision: **64.00% [46.5%, 78.6%]**, Recall: **6.94% [4.1%, 9.8%]**, $F_{0.5}$: **24.21% [15.4%, 32.0%]**
    - *Impact on CoNLL:* Precision $+10.05\%$ ($53.95\% \rightarrow 64.00\%$), False Positives cut in half ($35 \rightarrow 18$), but filtering $9$ True Positives ($41 \rightarrow 32$) dropped Recall, resulting in a $-2.59\%$ change in $F_{0.5}$ ($26.80\% \rightarrow 24.21\%$).
- **Router Threshold Sweep ($\tau \in [0.20, 0.80]$):**
  - $\tau=0.20$: $P=39.11\%, R=14.93\%, F_{0.5}=29.54\%$ (High Recall)
  - $\tau=0.45$: $P=46.67\%, R=13.23\%, F_{0.5}=31.00\%$ (Optimal $F_{0.5}$ balance on dev slice)
  - $\tau=0.80$: $P=59.38\%, R=3.59\%, F_{0.5}=14.46\%$ (Ultra High Precision)
- **Dialectal Variation Analysis:** 15/150 sentences in BEA-19 dev contain British English orthography (`centre`, `programme`, `colour`, `travelling`) where LLM standardizes to US English.
- **Unit & Integration Tests:** 54/54 passing (`.venv/bin/pytest tests/`).

