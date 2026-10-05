# Capstone System Architecture Specification

## 1. Architectural Layers

### A. Linguistic & Syntax Layer (`orto/core/`)
- **`SyntaxEngine`:** spaCy pipeline extracting Universal Dependency trees and morphology tags.
- **`NonDestructiveTokenizer`:** Tokenizes without modifying raw string slices.
- **`UniversalLinguisticEngine`:** Comprehensive rule, morphology, and dependency diagnostic engine for instant offline fallback.
- **`ReverseOffsetPatcher`:** Reverse start-offset patching algorithm.

### B. Neurosymbolic & LLM Layer (`orto/llm/`, `orto/critic/`)
- **`LLMClient`:** Structured JSON client supporting OpenRouter, OpenAI, and Gemini with automatic model cascading.
- **`SymbolicCritic`:** In-memory virtual buffer verifier asserting tree connectivity and morphosyntactic Subject-Verb Agreement.

### C. Language Modeling & Machine Learning (`orto/lm/`, `orto/ml/`)
- **`NGramLanguageModel`:** Laplace-smoothed word bigram fluency estimator.
- **`EditConfidenceClassifier`:** 8-feature Scikit-Learn Logistic Regression model.

### D. Stylometry & Naturalization (`orto/style/`)
- **`StyleAnalyzer`:** Burstiness ($B = \frac{\sigma}{\mu}$), passive voice density, AI cliché detection.
- **`StyleNaturalizer`:** Cadence re-rhythmer and de-cliché generator.

### E. Application & Presentation Layer
- **`app.py`:** Streamlit visual dashboard.
- **`backend/server.py`:** FastAPI REST API with CORS, rate limiting, and security headers.
- **`frontend/`:** React + Vite diagnostic web client.
