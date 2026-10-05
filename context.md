# Orto Single Source of Truth (context.md)

## 1. Project Overview
Orto is a production-grade Neurosymbolic Grammatical Error Correction (GEC) and Diagnostic Engine. It combines Universal Dependency syntactic graph priors, constrained Large Language Model (LLM) structured hypothesis generation, multi-provider model cascading, a guaranteed Universal Linguistic Fallback Engine, symbolic morphosyntactic verification via a Symbolic Critic, non-destructive reverse-offset virtual patching, and stylometric naturalness analysis.
- **Primary Development Repo:** `https://github.com/sameezy667/Orto.git`
- **Submission Mirror Repo:** `https://github.com/sameezy667/Orto_capstone_repo.git` (Created specifically for submission and grading)

## 2. Tech Stack
- **Language & Runtime:** Python 3.10+ (Anaconda/Conda / venv), TypeScript (Frontend).
- **Core NLP & Syntax:** spaCy (`en_core_web_sm`), Universal Dependencies (UD v2), ERRANT taxonomy.
- **LLM Integration:** OpenAI Python SDK with OpenRouter, OpenAI, Gemini API, and fallback model cascading.
- **Language Modeling & ML:** Laplace-smoothed N-gram Language Model, Scikit-learn Logistic Regression Classifier, Joblib serialization.
- **Backend API:** FastAPI with Pydantic v2 schemas, Starlette middleware, security headers (CSP, frame-options, nosniff, CORS), rate limiting.
- **Frontend / UI:** Streamlit interactive diagnostic dashboard (`app.py`), React + Vite frontend (`frontend/`).
- **Testing:** Pytest test suite with 65 comprehensive unit, integration, and ablation tests.

## 3. Architecture & Directory Structure
```
Orto/
├── assignments/               # Milestone progress logs, weekly logs, and contribution matrix
│   ├── weekly_progress_log.md
│   ├── assignment_1_dataset_and_preprocessing.md
│   ├── assignment_2_model_development_and_critic.md
│   └── assignment_3_pipeline_integration_and_eval.md
├── notebooks/                 # Interactive Jupyter Notebook demonstrations
│   ├── 01_dataset_exploration.ipynb
│   ├── 02_ngram_language_model.ipynb
│   ├── 03_ml_confidence_classifier.ipynb
│   ├── 04_orto_pipeline_demo.ipynb
│   └── 05_stylometry_naturalization.ipynb
├── code/                      # Direct executable scripts and entry points
│   ├── README.md
│   ├── run_pipeline.py
│   ├── run_server.py
│   └── run_app.py
├── resources/                 # Diagrams, technical specifications, and dataset dictionaries
│   ├── README.md
│   ├── architecture_diagram.mermaid
│   ├── pipeline_flow.mermaid
│   ├── dataset_dictionary.md
│   └── errant_taxonomy_reference.md
├── presentations/             # Capstone presentation deck, speaker notes, and one-pager
│   ├── README.md
│   ├── capstone_presentation_slides.md
│   ├── speaker_notes_and_script.md
│   └── project_summary_one_pager.md
├── capstone/                  # Master Capstone documentation, charter, and full technical report
│   ├── README.md
│   ├── final_capstone_report.md
│   ├── project_charter.md
│   ├── system_architecture.md
│   └── results_and_evaluation.md
├── orto/                      # Core Neurosymbolic GEC Python Package
│   ├── core/                  # Syntax engine, tokenizer, reverse-offset patcher, linguistic fallback
│   │   ├── patcher.py
│   │   ├── syntax_engine.py
│   │   ├── tokenizer.py
│   │   └── linguistic_fallback.py
│   ├── critic/                # Symbolic Critic (SVA invariants, tree connectivity, reflection)
│   │   └── verifier.py
│   ├── fewshot/               # Dynamic exemplar bank & semantic retrieval
│   │   ├── bank.py
│   │   └── retriever.py
│   ├── llm/                   # LLM Client, prompt builders, structured schemas, model cascading
│   │   ├── client.py
│   │   ├── prompts.py
│   │   └── schemas.py
│   ├── lm/                    # N-gram fluency & perplexity scoring
│   │   └── ngram.py
│   ├── ml/                    # Confidence classifiers, feature extraction, invocation routing
│   │   ├── features.py
│   │   ├── router.py
│   │   ├── schemas.py
│   │   └── train_router.py
│   ├── pipeline.py            # OrtoEngine Pipeline Orchestrator
│   └── style/                 # Stylometry analyzer & AI cadence naturalizer
│       ├── analyzer.py
│       ├── metrics.py
│       ├── naturalizer.py
│       └── schemas.py
├── backend/                   # FastAPI REST API Server
│   ├── __init__.py
│   └── server.py              # Endpoints: /api/v1/analyze, /style/analyze, /style/humanize, /health
├── frontend/                  # React + Vite Diagnostic Client
├── prompts/                   # Externalized prompt templates
│   └── prompts.yaml
├── data/                      # Models, caches, and test fixtures
├── tests/                     # 65 Pytest tests
├── context.md                 # Single source of truth (this file)
├── README.md                  # Master repository documentation & submission details
├── app.py                     # Streamlit Interactive Diagnostic Frontend
└── requirements.txt           # Python dependencies
```

## 4. Feature Status Checklist
- [x] Universal Dependency Syntax Prior Extraction (`SyntaxEngine`)
- [x] Non-Destructive Character Offset Tokenization (`NonDestructiveTokenizer`)
- [x] Multi-Provider LLM Structured Client with Model Cascading (`LLMClient`)
- [x] Deep Universal Linguistic & Morphosyntax Diagnostic Engine (`UniversalLinguisticEngine`)
- [x] Symbolic Critic Morphosyntactic Verification & 1-Turn Reflection (`SymbolicCritic`)
- [x] Reverse-Offset In-Memory Virtual Patcher (`ReverseOffsetPatcher`)
- [x] Laplace-Smoothed N-Gram Language Model (`NGramLanguageModel`)
- [x] ML Confidence Classifier & Invocation Router (`EditConfidenceClassifier`, `InvocationRouter`)
- [x] Dynamic Few-Shot Exemplar Retrieval (`ExemplarRetriever`)
- [x] Stylometry Analyzer & AI Cadence Naturalizer (`StyleAnalyzer`, `StyleNaturalizer`)
- [x] FastAPI REST API with OWASP Headers & Rate Limiting (`backend/server.py`)
- [x] Streamlit Diagnostic Dashboard with Model Selector & Real-Time Patching (`app.py`)
- [x] 65 Comprehensive Pytest Tests Passing (`tests/`)
- [x] All Guidelines & Submission Deliverables Created (`assignments/`, `notebooks/`, `code/`, `resources/`, `presentations/`, `capstone/`, `README.md`)

## 5. Data Models
### DiagnosticEdit
```typescript
interface DiagnosticEdit {
  span: {
    start_char: number;
    end_char: number;
    original_text: string;
  };
  replacement: string;
  errant_type: "R:SPELL" | "R:VERB:SVA" | "R:VERB:TENSE" | "R:NOUN:NUM" | "R:PREP" | "M:DET" | "R:WO" | "R:OTHER";
  linguistic_rule: string;
  explanation: string;
  counterfactual_example: string;
  confidence: number;
  critic_verified: boolean;
}
```

### OrtoResponse
```typescript
interface OrtoResponse {
  original_text: string;
  corrected_text: string;
  edits: DiagnosticEdit[];
  telemetry: {
    latency_ms: number;
    input_tokens: number;
    refinement_cycles: number;
    critic_passed: boolean;
    engine_tier?: string;
  };
}
```

## 6. API Contracts
- `POST /api/v1/analyze`: Returns `AnalyzeResponse` with original text, corrected text, diagnostic edits, syntax priors, stylometry report, and telemetry.
- `POST /api/v1/style/analyze`: Returns `StyleAnalysisResult` with burstiness, sentence lengths, passive ratio, and detected clichés.
- `POST /api/v1/style/humanize`: Returns `HumanizeResponse` with de-clichéd humanized text and stylometry comparison.
- `GET /api/v1/health`: Service health status.
