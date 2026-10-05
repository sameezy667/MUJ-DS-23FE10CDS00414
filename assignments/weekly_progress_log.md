# Batch E — Weekly Progress & Milestone Logs

## Project Metadata
- **Project Title:** Orto — Neurosymbolic Grammatical Error Correction & Diagnostic Engine
- **Student Name:** SAMEER DHIR
- **Registration Number:** 23FE10CDS00414
- **Branch:** Department of Data Science
- **Batch:** Batch E
- **Track:** Natural Language Processing (NLP) Capstone

---

## Weekly Milestone Tracker

| Week / Sprint | Focus Area | Deliverables & Progress | Status |
|---|---|---|---|
| **Week 1** | Problem Formulation & Dataset Sourcing | Curated BEA-2019 and CoNLL-2014 M2 datasets; established ERRANT error taxonomy definitions. | ✅ Completed |
| **Week 2** | Syntactic Prior Extraction & Tokenizer | Developed `NonDestructiveTokenizer` with exact character span preservation; integrated spaCy Universal Dependency parsing. | ✅ Completed |
| **Week 3** | Constrained LLM Hypothesis Generation | Built structured prompt templates in `prompts/prompts.yaml`; implemented Pydantic schema validation for `DiagnosticEdit`. | ✅ Completed |
| **Week 4** | Symbolic Critic Invariant Engine | Implemented `SymbolicCritic` with in-memory virtual patching and morphosyntactic SVA invariant verification. | ✅ Completed |
| **Week 5** | Language Modeling & ML Routing | Built Laplace-smoothed N-Gram language model; trained Scikit-Learn `EditConfidenceClassifier` for precision reranking. | ✅ Completed |
| **Week 6** | Stylometry & AI Cadence De-Cliché | Implemented burstiness score ($B = \frac{\sigma}{\mu}$), passive voice density, and AI cliché lexical markers. | ✅ Completed |
| **Week 7** | Multi-Provider LLM Fallback & Linguistic Engine | Developed `UniversalLinguisticEngine` and instant multi-model cascade fallback guaranteeing 100% verified responses. | ✅ Completed |
| **Week 8** | Full-Stack UI, API & Comprehensive Evaluation | Integrated Streamlit interactive dashboard, FastAPI REST API, React UI, and 65-test automated Pytest suite. | ✅ Completed |

---

## Individual Contribution Matrix

- **Dataset & Syntax Engineering:** spaCy dependency extraction, morphology priors, M2 parsing, and tokenizer offset verification.
- **Model Development & LLM Integration:** Structured decoding, multi-provider cascading (OpenRouter/OpenAI/Gemini), prompt engineering, and offline linguistic fallback.
- **Symbolic Verification & Patcher:** Reverse-offset string patching algorithm, SVA invariant assertion, tree connectivity tests.
- **Backend & ML Pipeline:** FastAPI endpoints, security middlewares, rate-limiting, Scikit-learn logistic regression router.
- **Frontend & Visualization:** Streamlit dashboard, span highlight visualizer, interactive diagnostic cards, and stylometry charts.
