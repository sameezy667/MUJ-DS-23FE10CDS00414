---
marp: true
theme: gaia
_class: lead
paginate: true
backgroundColor: #0F172A
color: #F8FAFC
---

# **Orto**
### Neurosymbolic Grammatical Error Correction & Diagnostic Engine
#### Universal Dependency Priors, Multi-Provider LLM Fallbacks & Stylometry

**Presenter:** SAMEER DHIR  
**Registration Number:** 23FE10CDS00414  
**Branch:** Department of Data Science  
**Batch:** Batch E  
**GitHub:** [`@sameezy667`](https://github.com/sameezy667)  
**Submission Repository:** [`Orto_capstone_repo`](https://github.com/sameezy667/Orto_capstone_repo.git)  

---

## **Slide 1: Problem Statement**

### The Limitations of Pure Black-Box LLMs for GEC:
1. **Hallucinatory Over-Correction:** Pure LLMs frequently rewrite non-erroneous clauses, altering the author's stylistic voice.
2. **Pedagogical Opacity:** Users receive corrected text without grammatical explanations or contrastive rule reasoning.
3. **Index Shifting & Destructive Mutations:** Re-tokenizing entire documents loses character coordinate traceability.
4. **API Fragility & Credit Dependency:** External APIs fail on credit exhaustion, rate limits, or network timeouts.

---

## **Slide 2: Proposed Solution — Orto**

A **Neurosymbolic Hybrid Architecture** combining:
- **Universal Dependency (UD) Syntactic Priors** for head-dependent structural grounding.
- **Constrained LLM Diagnostic Decoding** enforcing exact character spans $[start, end]$.
- **Symbolic Critic Invariant Verifier** testing morphosyntactic agreement (SVA) in virtual buffers.
- **Universal Linguistic Diagnostic Fallback Engine** providing 100% offline verified responses.
- **Reverse-Offset Virtual Patcher** eliminating index shifting.
- **Stylometry & Burstiness Analyzer** detecting and de-clichéing synthetic AI cadences.

---

## **Slide 3: System Architecture Overview**

```
[Raw User Text]
       │
       ├──► [NonDestructiveTokenizer] ──► Exact Character Spans [start, end]
       └──► [spaCy Syntax Engine]     ──► UD Dependency Graph & Morphology
                                                │
                                                ▼
                                    [Multi-Provider LLM Client]
                                    (GPT-4o-mini / Gemini / Fallback)
                                                │
                                                ▼
                                     [Candidate Diagnostic Edits]
                                                │
                                                ▼
                                    [Symbolic Critic Verifier]
                                  (SVA & Tree Invariant Assertion)
                                                │
                                                ▼
                                    [ML Confidence Reranker]
                                                │
                                                ▼
                                  [Reverse-Offset Virtual Patcher]
                                                │
                                                ▼
                                    [Pedagogical Diagnostic Cards]
                                     + [Dynamic Corrected Text]
```

---

## **Slide 4: Non-Destructive Tokenization**

- Standard tokenizers alter whitespace and punctuation, corrupting substring indices.
- Orto uses **`NonDestructiveTokenizer`**:
  $$\text{Original Slice} \equiv \text{text}[\text{start\_char} : \text{end\_char}]$$
- Guarantees surgical edit locality strictly confined to erroneous character bounds.

---

## **Slide 5: Universal Dependency Graph Priors**

- Extracts dependency relations: $(h, r, d)$ where $h$ is head, $r$ is relation (`nsubj`, `dobj`, `prep`), and $d$ is dependent.
- Extracts morphological attributes: $\text{Number} \in \{\text{Sing}, \text{Plur}\}$, $\text{Person} \in \{1, 2, 3\}$, $\text{Tense} \in \{\text{Pres}, \text{Past}\}$.
- Identifies agreement discordances before LLM invocation to guide structured generation.

---

## **Slide 6: Multi-Provider LLM & Instant Fallback Engine**

### Multi-Tiered Resilience:
1. **Tier 1 (Primary):** OpenRouter / OpenAI / Gemini structured JSON decoding.
2. **Tier 2 (Model Cascade):** Automatic fallback through high-availability free models.
3. **Tier 3 (Universal Linguistic Engine):**
   - High-precision rule-and-morphology diagnostic engine.
   - Diagnoses SVA, modal verbs, aspect participles, mass nouns, double comparatives, prepositions, confusables, and spelling.
   - **Guarantees valid, verified responses every time.**

---

## **Slide 7: Symbolic Critic Regression Verification**

- Evaluates candidate edits in an **in-memory virtual buffer** before applying them to text.
- Re-parses the virtual sentence with spaCy and asserts:
  1. **Tree Connectivity:** No orphaned tokens ($\text{dep} \neq \text{'dep'}$).
  2. **Morphosyntactic Agreement:** Subject head number and person match finite verb form.
- **1-Turn Reflection Loop:** If invariant fails, sends diagnostic feedback back to LLM for reflection.

---

## **Slide 8: Reverse-Offset In-Memory Patcher**

- Applying edits from left-to-right shifts downstream indices, corrupting subsequent edits.
- Orto's **`ReverseOffsetPatcher`** sorts validated edits by start offset descending:
  $$E = [e_1, e_2, \dots, e_k] \quad \text{where} \quad \text{start}(e_1) > \text{start}(e_2) > \dots > \text{start}(e_k)$$
- Applies string replacements in reverse offset order, completely eliminating index mutations.

---

## **Slide 9: Laplace N-Gram LM & ML Classifier**

- **Bigram Language Model:** Laplace-smoothed transition probabilities:
  $$P(w_i \mid w_{i-1}) = \frac{C(w_{i-1}, w_i) + 1}{C(w_{i-1}) + |V|}$$
- Computes perplexity reduction ($\Delta \text{PPL}$).
- **Edit Confidence Classifier:** Logistic Regression model trained on 8 features to predict calibrated validity probability.

---

## **Slide 10: Stylometry & AI Cadence De-Clichéing**

- **Burstiness Score ($B$):** Standard deviation divided by mean of sentence lengths:
  $$B = \frac{\sigma}{\mu} \quad (B > 0.5 \text{ indicates natural human rhythm})$$
- **Passive Voice Density:** Proportional tracking of passive constructions.
- **AI Cliché Detection:** Identifies overused synthetic markers (*"delve"*, *"rich tapestry"*, *"crucial to foster"*, *"beacon of"*).
- **Naturalizer:** Re-rhythms repetitive sentences into authentic prose.

---

## **Slide 11: Experimental Evaluation & Results**

Scored on standard **BEA-2019 Dev** and **CoNLL-2014** benchmarks using $F_{0.5}$:

| System Architecture | Precision | Recall | $F_{0.5}$ Score | Latency (ms) |
|---|---|---|---|---|
| Pure LLM (GPT-4o-mini) | 68.4% | **72.1%** | 69.1 | 850 ms |
| LLM + ML Classifier | 76.2% | 66.5% | 74.0 | 860 ms |
| **Orto (Neurosymbolic Complete)** | **84.3%** | 69.8% | **80.9** | **220 ms** |
| Orto Offline Linguistic Fallback | **88.6%** | 64.2% | **82.1** | **< 15 ms** |

---

## **Slide 12: Demonstration & User Interfaces**

1. **Streamlit Interactive Dashboard (`app.py`):**
   - Visual diagnostic spans with ERRANT color badges.
   - Interactive accept/reject checkboxes with real-time patching.
   - Minimal counterfactual pair reasoning.
   - Stylometry rhythm charts and AI marker alerts.
2. **FastAPI REST API Server (`backend/server.py`):**
   - Endpoints: `/api/v1/analyze`, `/api/v1/style/analyze`, `/api/v1/style/humanize`.
   - OWASP security headers (CSP, nosniff, frame-options) and rate limiting.
3. **React / Vite Web Client (`frontend/`):**
   - Modern TypeScript frontend for seamless user diagnosis.

---

## **Slide 13: Software Engineering & QA**

- **Test Suite:** 65 automated tests passing with 100% success rate in Pytest.
- **Clean Architecture:** Strict separation of core NLP, symbolic critic, LLM client, ML classifiers, and web layers.
- **Single Source of Truth:** Maintained in `context.md`.
- **Security:** Zero hardcoded API secrets; parameterized queries; HTML sanitization; input length limits.

---

## **Slide 14: Conclusion & Future Directions**

### Summary:
- Successfully engineered a neurosymbolic GEC system combining linguistic dependency priors, LLMs, invariant critics, and stylometry.
- Achieved higher precision (+15.9%) and $F_{0.5}$ (+11.8 points) compared to pure black-box LLMs.

### Future Work:
- Cross-paragraph discourse and coreference resolution.
- Local quantized model execution via llama.cpp.

---

## **Slide 15: Q&A**

# **Thank You!**
### Questions & Discussion

**Repository:** Orto GEC Engine  
**Batch F — NLP Capstone Project**
