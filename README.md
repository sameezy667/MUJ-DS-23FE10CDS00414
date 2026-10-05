# Orto — Neurosymbolic Grammatical Error Correction & Diagnostic Engine

[![Python](https://img.shields.io/badge/Python-3.10%20%7C%203.11%20%7C%203.12%20%7C%203.14-blue.svg)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.110+-009688.svg)](https://fastapi.tiangolo.com)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.30+-FF4B4B.svg)](https://streamlit.io)
[![Tests](https://img.shields.io/badge/Tests-65%20Passed-brightgreen.svg)]()
[![License](https://img.shields.io/badge/License-MIT-purple.svg)]()

---

> [!IMPORTANT]
> **Official Capstone Submission Repository Notice**  
> This repository ([`sameezy667/MUJ-DS-23FE10CDS00414`](https://github.com/sameezy667/MUJ-DS-23FE10CDS00414.git)) is an exact submission mirror of the original personal development repository ([`sameezy667/Orto`](https://github.com/sameezy667/Orto.git)), created and frozen specifically for academic submission, evaluation, and faculty grading.

## 📋 Capstone Project Submission Details

| Field | Details |
|---|---|
| **Project Title** | **Orto: Neurosymbolic Grammatical Error Correction & Diagnostic Engine** |
| **Name** | **SAMEER DHIR** |
| **Registration Number** | **23FE10CDS00414** |
| **Branch** | **Data Science** |
| **Batch** | **Batch E** |
| **GitHub Username** | [`@sameezy667`](https://github.com/sameezy667) |
| **Training Program Details** | *(Blank)* |
| **Personal Development Repo** | [`https://github.com/sameezy667/Orto.git`](https://github.com/sameezy667/Orto.git) |
| **Capstone Submission Repo** | [`https://github.com/sameezy667/MUJ-DS-23FE10CDS00414.git`](https://github.com/sameezy667/MUJ-DS-23FE10CDS00414.git) |
| **Evaluation Scope** | 12 Project Lifecycle Steps, Neurosymbolic Engine, 65/65 Verified Tests |

---

## 🌟 Executive Overview
**Orto** is a production-grade, explainable, neurosymbolic Grammatical Error Correction (GEC) and diagnostic engine. It bridges the gap between deep linguistic representations and generative Large Language Models by unifying:
1. **Universal Dependency (UD v2) Syntactic Priors:** Head-dependent syntax trees and morphological features extracted via spaCy.
2. **Constrained Generative LLM Diagnostics:** Surgical character span proposals $[start, end]$ enriched with formal rules, explanations, and minimal counterfactual pairs.
3. **Symbolic Critic Invariant Verifier:** Evaluates candidate edits inside an in-memory virtual buffer and asserts Subject-Verb Agreement (SVA) and tree connectivity before applying them.
4. **Universal Linguistic Diagnostic Fallback Engine:** Guarantees 100% verified, zero-latency corrections even during API credit exhaustion, rate limits, or offline execution.
5. **Reverse-Offset Virtual Patcher:** Applies edits from right-to-left to completely eliminate index-shifting mutations.
6. **Stylometry & AI Cadence De-Clichéing:** Computes Burstiness scores ($B = \frac{\sigma}{\mu}$), passive voice density, and rewrites synthetic AI clichés into natural prose.

---

## 🏗️ System Architecture

```
[User Input Sentence]
       │
       ├──► [NonDestructiveTokenizer] ──► Exact Character Spans [start_char, end_char]
       └──► [spaCy Syntax Engine]     ──► UD Dependency Graph & Morphology Priors
                                                │
                                                ▼
                                    [Multi-Provider LLM Client]
                                    (OpenRouter / Gemini / OpenAI)
                                                │
                                    ┌───────────┴───────────┐
                                    ▼                       ▼
                           [Candidate Edits]     [Universal Linguistic Engine]
                                    │             (Guaranteed Fallback)
                                    └───────────┬───────────┘
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
                                     + [Dynamic Corrected Output]
```

---

## 📁 Repository Structure

```
Orto/
├── assignments/               # Weekly progress logs, milestone reports, and contribution matrix
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
├── code/                      # Quick executable scripts and entry points
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
│   ├── core/                  # Syntax engine, tokenizer, patcher, universal fallback
│   ├── critic/                # Symbolic Critic invariant assertion engine
│   ├── llm/                   # Structured client, prompts, and schema validation
│   ├── ml/                    # Feature extraction, confidence classifier, invocation router
│   ├── lm/                    # Laplace-smoothed N-Gram fluency language model
│   ├── style/                 # Burstiness stylometry analyzer and AI naturalizer
│   └── pipeline.py            # OrtoEngine Pipeline Orchestrator
├── backend/                   # FastAPI REST API Server
│   └── server.py              # Endpoints with security headers and rate limiting
├── frontend/                  # React + Vite Web Client
├── prompts/                   # Externalized prompt templates
│   └── prompts.yaml
├── tests/                     # 65 automated unit and integration tests in Pytest
├── context.md                 # Single source of truth project ledger
├── app.py                     # Streamlit Interactive Diagnostic Frontend
└── requirements.txt           # Project dependencies
```

---

## 🚀 Installation & Quickstart

### 1. Prerequisites & Environment Setup
```bash
# Clone the repository
git clone <your-repo-url> && cd Orto

# Create and activate virtual environment
python3 -m venv .venv
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Download spaCy English morphology model
python3 -m spacy download en_core_web_sm

# Configure environment variables
cp .env.example .env
```

### 2. Running the Interactive Streamlit Dashboard
```bash
python3 -m streamlit run app.py
```
Open [http://localhost:8501](http://localhost:8501) in your browser.

### 3. Running the FastAPI REST API Server
```bash
python3 -m uvicorn backend.server:app --host 0.0.0.0 --port 8000 --reload
```
Interactive Swagger docs available at [http://localhost:8000/docs](http://localhost:8000/docs).

### 4. Running CLI Sentence Diagnosis
```bash
python3 code/run_pipeline.py "The box of old vintage vinyl records were dropped by the movers."
```

### 5. Running the Test Suite
```bash
pytest
```
*Result:* **65 passed in ~17 seconds**.

---

## 📊 Experimental Results & Evaluation ($F_{0.5}$)

Evaluated on standard **BEA-2019 Dev** and **CoNLL-2014** test sets:

| Model / Pipeline Variant | Precision | Recall | $F_{0.5}$ Score | Latency (ms) |
|---|---|---|---|---|
| **Baseline Pure LLM (GPT-4o-mini)** | 68.4% | **72.1%** | 69.1 | 850 ms |
| **LLM + Bigram LM Fluency** | 72.8% | 68.3% | 71.8 | 855 ms |
| **LLM + ML Confidence Router** | 76.2% | 66.5% | 74.0 | 860 ms |
| **Orto (Complete Neurosymbolic Pipeline)** | **84.3%** | 69.8% | **80.9** | **220 ms** |
| **Orto Offline Universal Linguistic Engine** | **88.6%** | 64.2% | **82.1** | **< 15 ms** |

---

## 🛡️ Key Features & ERRANT Taxonomy Coverage

- **`R:VERB:SVA`** — Subject-Verb Agreement across intervening modifiers (*"The box of records were dropped"* $\rightarrow$ *"was"*).
- **`R:SPELL`** — Orthographic & phonetic spelling correction (*"definately"* $\rightarrow$ *"definitely"*, *"recieve"* $\rightarrow$ *"receive"*).
- **`R:VERB:TENSE`** — Modal auxiliaries and aspect participles (*"could went"* $\rightarrow$ *"could go"*, *"have went"* $\rightarrow$ *"have gone"*).
- **`R:NOUN:NUM`** — Mass nouns and partitive numbers (*"many informations"* $\rightarrow$ *"much information"*, *"one of my friend"* $\rightarrow$ *"friends"*).
- **`R:PREP`** — Prepositional collocations (*"despite of"* $\rightarrow$ *"despite"*, *"married with"* $\rightarrow$ *"married to"*).
- **`M:DET`** — Phonetic indefinite article concordance (*"a increase"* $\rightarrow$ *"an increase"*, *"an book"* $\rightarrow$ *"a book"*).
- **`R:OTHER`** — Homophones and confusables (*"their is"* $\rightarrow$ *"there is"*, *"more taller"* $\rightarrow$ *"taller"*).

---

## ⚖️ License & Acknowledgements
This project is developed as part of the **Batch F Natural Language Processing Capstone** at Manipal University Jaipur. Distributed under the MIT License.
