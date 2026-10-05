# Capstone Project Charter

## 1. Project Title & Metadata
- **Project Title:** Orto: Neurosymbolic Grammatical Error Correction & Diagnostic Engine
- **Domain:** Natural Language Processing (NLP)
- **Repository:** [https://github.com/sameezy667/Orto.git](https://github.com/sameezy667/Orto.git)

---

## 2. Project Vision & Problem Statement
To build an explainable, high-precision, neurosymbolic GEC system that eliminates LLM hallucinations, maintains character coordinate alignment, enforces morphosyntactic grammatical invariants, provides multi-provider fallback resilience, and evaluates stylometric burstiness.

---

## 3. Scope & Key Deliverables
- **Core Algorithms:** Non-destructive tokenizer, Universal Dependency extraction, Symbolic Critic invariant verifier, Reverse-Offset Patcher, Laplace N-gram LM, Logistic Regression classifier, and Universal Linguistic Diagnostic Engine.
- **Interfaces:** Streamlit interactive diagnostic dashboard, FastAPI REST service, React/Vite web application.
- **Evaluation & Benchmarking:** Scored on BEA-2019 and CoNLL-2014 M2 datasets with $F_{0.5}$ metric.
- **Documentation & QA:** 65 automated tests, slide deck, final report, and weekly milestones.

---

## 4. Success Criteria
1. **$F_{0.5} \ge 78.0$** on standard GEC benchmarks.
2. **Precision $\ge 82.0\%$** to prevent false-alarm overcorrections.
3. **100% Test Pass Rate** across unit and integration suites.
4. **Resilience:** 100% verified response availability during API downtime.
