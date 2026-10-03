Product Requirements Document (PRD): OrtoProject Name: Orto (Neurosymbolic Grammatical Error Correction & Diagnostic Engine)Document Version: 1.0.0Target Milestone: Academic Benchmark & Open-Source Production ReleaseStatus: Approved for Implementation1. Executive Summary & Problem Definition1.1 Executive SummaryOrto is a neurosymbolic Grammatical Error Correction (GEC) and diagnostic engine designed to bridge the gap between classical linguistic dependency parsers and large language model (LLM) contextual reasoning. Standard LLM writing assistants frequently introduce stylistic drift, rewrite non-erroneous clauses, hallucinate grammatical justifications, and fail to track exact character-level offsets. Orto solves this by pairing Universal Dependency tree extraction with constrained, span-level LLM decoding and an automated symbolic critic that catches regressions before edits are rendered.1.2 Problem DefinitionExisting writing assistants operate at two flawed extremes:Classical Heuristic Systems (e.g., Rule-based engines, SymSpell, early LanguageTool): Fast and deterministic, but fragile against long-range dependencies, real-word confusables (affect/effect, principal/principle), and structural syntactic ambiguities.End-to-End LLM Prompting (e.g., "Fix the grammar in this text"): Prone to over-correcting natural authorial voice, unable to guarantee deterministic character-offset coordinates for diff UIs, and incapable of explaining why an edit was made using formal linguistic taxonomies.The GEC Diagnostic Gap: State-of-the-art neural sequence-tagging models (e.g., GECToR) output corrected token streams without human-interpretable linguistic explanations or counterfactual examples for language learners.1.3 Solution VisionOrto establishes a hybrid architecture where:Classical NLP (spaCy Universal Dependencies) handles structural feature extraction and programmatic constraint validation.An LLM API handles contextual ambiguity resolution, lexical selection, error taxonomy labeling, and counterfactual pedagogical feedback.A post-generation Symbolic Critic asserts grammatical validity, eliminating hallucinations and ensuring zero parser regressions.2. Product Goals, KPIs, & Evaluation Metrics2.1 Strategic GoalsSurgical Edit Locality: Confine text mutations strictly to invalid spans while keeping all surrounding authorial voice and sentence structure intact.Non-Destructive Offset Alignment: Generate exact character-coordinate intervals [start_char, end_char] that align directly with the original string for reliable client-side rendering.Pedagogical Transparency: Classify every edit against the official ERRANT (Error Annotation Toolkit) taxonomy accompanied by formal rule citations and counterfactual minimal pairs.Neurosymbolic Robustness: Prevent LLM hallucinations by subjecting every proposed edit to an automated morphosyntactic regression test.2.2 Quantitative KPIs & TargetsMetricTarget ValueMeasurement ProtocolGEC Quality ($F_{0.5}$)$\ge 68.0$Evaluated on the BEA-2019 (W&I-dev) benchmark via ERRANT / $M^2$ ScorerStylistic Drift Ratio$< 3.0\%$Fraction of non-erroneous tokens altered across test corporaSpan Alignment Accuracy$100\%$Programmatic check verifying that original*text == input_text[start:end]End-to-End Latency$\le 1.8\text{s}$ (p95)Per standard paragraph ($\approx 60\text{–}100$ words) using commercial LLM APIsSymbolic Critic Catch Rate$> 92.0\%$Verification pass against artificially perturbed test sets (induced agreement flaws)$$\text{Precision} = \frac{TP}{TP + FP}, \quad \text{Recall} = \frac{TP}{TP + FN}$$$$F*{0.5} = \frac{(1 + 0.5^2) \cdot \text{Precision} \cdot \text{Recall}}{(0.5^2 \cdot \text{Precision}) + \text{Recall}}$$(Note: $F_{0.5}$ weights precision twice as heavily as recall, reflecting standard GEC practice where false positives degrade user trust significantly more than missed errors).3. User Personas & User Journeys3.1 Target PersonasPersona A: NLP Researcher & Academic Evaluator: Needs access to standardized benchmark scripts, reproducible ablations against public baselines (BEA-2019, CoNLL-2014), and metric reporting over ERRANT error classes.Persona B: Language Learner / Second-Language Writer: Needs minimal corrections that fix errors without rewriting whole sentences, paired with clear explanations of grammatical rules and counterfactual pairs showing when their word choice would actually apply.Persona C: Application / Product Developer: Needs a typed Python library and REST/JSON API that emits deterministic character spans to drive web text editors, browser extensions, or automated grading pipelines.3.2 End-to-End User Journey[User enters text via Web UI / API]
                 │
                 ▼
[Tokenization & Syntactic Prior Extraction]
                 │
                 ▼
[Constrained LLM Diagnostics & Span Proposal]
                 │
                 ▼
[Symbolic Critic Validation & In-Memory Patching]
                 │
        ┌────────┴────────┐
     (Passed)          (Failed)
        │                 │
        │                 ▼
        │        [LLM Hypothesis Refinement]
        │                 │
        ├─────────────────┘
        ▼
[Interactive Diff View Displayed]
        │
        ├── User hovers over span ──► Views Rule, Diagnosis, Counterfactual
        └── User accepts/rejects  ──► Dynamic in-memory text update
4. System Architecture & Information FlowOrto uses a multi-stage neurosymbolic cascade consisting of three decoupled layers:                            ┌────────────────────────────────┐
                            │        Raw User String         │
                            └───────────────┬────────────────┘
                                            │
                                            ▼
                            ┌────────────────────────────────┐
                            │    Stage 1: Feature Engine     │
                            │   (spaCy Universal Dependency)  │
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
                            │ (Structured Constrained Output)│
                            │  • Exact character spans       │
                            │  • Minimal token replacement   │
                            │  • ERRANT classification       │
                            │  • Pedagogical explanation     │
                            │  • Minimal counterfactual pair │
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
┌──────────────┐                            │ Yes
│ 1x Feedback  │                            ▼
│ Refinement   │            ┌────────────────────────────────┐
│ Loop         │            │   Stage 4: Verified Payload    │
└──────────────┘            │  • Validated character diffs   │
                            │  • Categorized error badges    │
                            │  • JSON / Web UI consumption   │
                            └────────────────────────────────┘
5. Functional Requirements (FR)Module 1: Preprocessing & Syntactic Prior ExtractionFR-1.1 (Non-Destructive Tokenization): The engine must ingest raw Unicode text without altering whitespace, line breaks, indentation, or punctuation, returning absolute character offsets [start, end] for every token.FR-1.2 (Universal Dependency Extraction): The engine must run en_core_web_sm (or en_core_web_trf) to generate:Directed syntactic edges: (governor_token, dependency_label, dependent_token).Core relation tags: Nominal subject (nsubj, nsubjpass), Root verb (ROOT), Direct object (dobj), Prepositional modifier (prep, pobj).Morphological feature bundles: Number (Sing, Plur), Person (1, 2, 3), Tense (Pres, Past), VerbForm (Fin, Inf, Part).FR-1.3 (Prior Serialization): Extracted features must be compressed into a lightweight JSON payload and injected into the LLM system prompt to ground attention on structural dependencies.Module 2: LLM Diagnostic Engine & Constrained DecodingFR-2.1 (Strict Schema Decoding): The LLM API call must use formal structured outputs (e.g., OpenAI JSON Schema mode or Instructor/Pydantic) to force compliance with the OrtoAnalysis model. Unstructured text or markdown wrappers (```json) are rejected at the client boundary.FR-2.2 (Surgical Locality): Edits must be restricted to minimal sub-phrases. The model must not rewrite adjacent clauses or rephrase stylistic choices that do not violate grammar.FR-2.3 (ERRANT Taxonomy Mapping): Every proposed edit must assign exactly one standard ERRANT category:R:SPELL (Spelling / Typographic / Phonetic error)R:VERB:SVA (Subject-Verb Agreement violation)R:VERB:TENSE (Verb Tense / Aspect error)R:NOUN:NUM (Noun Number / Countability error)R:PREP (Preposition substitution / deletion)M:DET (Missing Determiner / Article)R:WO (Word Order permutation)R:OTHER (Idiomatic, lexical choice, or uncategorized)FR-2.4 (Pedagogical Metadata Generation): Every proposed edit must produce:linguistic_rule: Formal grammatical designation (e.g., "Intervening Prepositional Phrase SVA").explanation: Concise diagnosis without conversational fillers (e.g., "The subject head 'box' is singular; the verb must not agree with the plural object of preposition 'records'").counterfactual_example: A syntactically valid paired sentence illustrating the correct usage of the replaced word.Module 3: Symbolic Critic & Self-Refinement LoopFR-3.1 (Virtual Patching): The engine must apply proposed replacements to an in-memory buffer using reverse offset ordering (from highest start_char to lowest) to prevent index shifting.FR-3.2 (Morphosyntactic Agreement Verification): For any edit classified as R:VERB:SVA or modifying a finite verb node:The patched sentence is re-parsed through spaCy.The system verifies:$$\text{Number}(\text{SubjectHead}) == \text{Number}(\text{PatchedVerb})$$If a mismatch occurs, the check fails.FR-3.3 (Syntactic Integrity Assertions): The critic asserts that the proposed edit does not introduce orphaned tokens (dep_ == "dep") or orphan clauses.FR-3.4 (Automated Refinement): If the critic detects an invariant violation, it issues a single targeted retry request to the LLM containing the failed candidate and the exact parser failure message.Module 4: Evaluation Suite & Benchmark RunnerFR-4.1 (Standard Corpus Ingestion): The test harness must support BEA-2019 (W&I+LOCNESS) and CoNLL-2014 datasets formatted in standard M2 or JSONL.FR-4.2 (Metric Computation): The runner must compute Precision, Recall, and $F_{0.5}$ globally and broken down across all ERRANT categories.FR-4.3 (Ablation Matrix): The suite must evaluate and report three distinct pipeline configurations:Baseline A: Pure Zero-Shot LLM (raw rewrite prompt).Baseline B: Pure Classical Rules (SymSpell + spaCy dependency heuristics).Proposed: Orto Hybrid (Syntactic priors + Constrained LLM + Symbolic Critic).Module 5: User Interface (Streamlit Visualizer)FR-5.1 (Interactive Span Highlighting): The frontend must display source text with colored badge overlays corresponding to error categories.FR-5.2 (Diagnostic Sidebar/Card): Clicking an error badge must open a diagnostic card presenting the proposed replacement, ERRANT badge, linguistic rule, explanation, and counterfactual pair.FR-5.3 (Interactive Accept/Reject State): Users must be able to toggle individual edits on or off, with the preview pane dynamically reflecting accepted modifications in real time.6. Technical & Non-Functional Requirements (NFR)NFR-1 (Deterministic Inference): All LLM API calls must be pinned to temperature=0.0 and seed=42 to guarantee reproducible span identification across runs.NFR-2 (Provider-Agnostic LLM Client): The LLM abstraction layer must use an adapter pattern supporting OpenAI API, Anthropic API, LiteLLM, or local vLLM endpoints.NFR-3 (Memory Footprint): The core engine must run locally on $\le 2\text{ GB}$ of RAM using en_core_web_sm, allowing operation on basic compute instances.NFR-4 (Robust Error Handling): If the LLM API times out or exceeds rate limits, the system must gracefully fall back to classical Tier-1/Tier-2 heuristic checks without crashing.NFR-5 (Code Quality & Packaging): The codebase must conform to PEP 8, maintain strict typing via mypy, achieve $\ge 85\%$ test coverage on core modules, and install cleanly via pip install -e ..7. Data Models, Type Specifications, & API Contracts7.1 Pydantic Core Models (orto/llm/schemas.py)Pythonfrom typing import List, Literal
from pydantic import BaseModel, Field

class SpanCoordinate(BaseModel):
start_char: int = Field(..., description="0-indexed start character offset in original text")
end_char: int = Field(..., description="0-indexed end character offset in original text")
original_text: str = Field(..., description="Exact substring in original text matching offsets")

class DiagnosticEdit(BaseModel):
span: SpanCoordinate
replacement: str = Field(..., description="Minimal replacement string")
errant_type: Literal[
"R:SPELL",
"R:VERB:SVA",
"R:VERB:TENSE",
"R:NOUN:NUM",
"R:PREP",
"M:DET",
"R:WO",
"R:OTHER"
] = Field(..., description="Official ERRANT taxonomy classification")
linguistic_rule: str = Field(..., description="Formal grammatical rule name")
explanation: str = Field(..., description="Clear diagnostic explanation")
counterfactual_example: str = Field(..., description="Example where original word is used correctly")
confidence: float = Field(..., ge=0.0, le=1.0, description="Model confidence score")

class OrtoAnalysis(BaseModel):
edits: List[DiagnosticEdit] = Field(default*factory=list, description="List of proposed edits")
7.2 API Specification: REST ContractEndpoint: POST /api/v1/analyzeRequest Headers:HTTPContent-Type: application/json
Authorization: Bearer <API_KEY>
Request Body:JSON{
"text": "The box of old vintage vinyl records were dropped by the movers.",
"options": {
"enable_critic": true,
"max_refinements": 1,
"model": "gpt-4o-mini"
}
}
Response Body (HTTP 200 OK):JSON{
"original_text": "The box of old vintage vinyl records were dropped by the movers.",
"corrected_text": "The box of old vintage vinyl records was dropped by the movers.",
"edits": [
{
"span": {
"start_char": 37,
"end_char": 41,
"original_text": "were"
},
"replacement": "was",
"errant_type": "R:VERB:SVA",
"linguistic_rule": "Subject-Verb Agreement with Intervening Prepositional Phrase",
"explanation": "The grammatical subject head is 'box' (singular), separated by the prepositional phrase 'of old vintage vinyl records'. The verb must take the singular form.",
"counterfactual_example": "The records were dropped by the movers.",
"confidence": 0.98,
"critic_verified": true
}
],
"telemetry": {
"latency_ms": 642,
"input_tokens": 12,
"refinement_cycles": 0
}
} 8. Repository Layout & Deliverable StructurePlaintextorto/
├── README.md # Architecture diagram, setup guide, benchmark results
├── requirements.txt # Pinned dependencies
├── pyproject.toml # Build & package configuration
├── Makefile # dev tasks: test, lint, benchmark, run-ui
├── data/
│ ├── sample_benchmark.jsonl # Mini validation set from BEA-2019 / CoNLL-2014
│ └── confusion_sets.json # Reference confusable word pairs
├── orto/
│ ├── **init**.py
│ ├── core/
│ │ ├── **init**.py
│ │ ├── tokenizer.py # Non-destructive offset-preserving tokenizer
│ │ ├── syntax_engine.py # spaCy dependency and morphological feature extractor
│ │ └── patcher.py # Reverse-order virtual string patcher
│ ├── llm/
│ │ ├── **init**.py
│ │ ├── client.py # LLM API adapter (OpenAI / LiteLLM)
│ │ ├── schemas.py # Pydantic data models
│ │ └── prompts.py # Morphosyntactically grounded prompt templates
│ ├── critic/
│ │ ├── **init**.py
│ │ └── verifier.py # Symbolic morphosyntax regression checker
│ └── pipeline.py # End-to-end Orto orchestrator
├── benchmarks/
│ ├── **init**.py
│ ├── evaluate.py # Official F_0.5 and ERRANT scoring harness
│ └── run_ablations.py # Automated comparison across baseline pipelines
├── app.py # Streamlit interactive diagnostic frontend
└── tests/
├── test_tokenizer.py # Offset integrity tests
├── test_syntax_engine.py # Dependency extraction tests
├── test_critic.py # SVA and regression verification tests
└── test_pipeline.py # Full mock integration tests 9. Risk Assessment, Failure Modes, & MitigationsRisk / Failure ModeLikelihoodImpactMitigation StrategyOffset Drift / Index MisalignmentMediumHighImplement strict post-decoding assertion: assert text[start:end] == span.original_text. Discard and flag any edit failing character-level alignment.LLM Output Hallucination / Regressive FixMediumHighPass all proposed replacements through the in-memory spaCy Symbolic Critic. If agreement is broken, trigger automatic rejection or single-turn refinement.API Rate Limits / Latency SpikesHighMediumImplement exponential backoff retry in client.py. Provide cached evaluation runs for local demonstration and benchmarking.Extreme Sentence Complexity (Parsing Errors)LowMediumWhen the dependency parser returns low tree confidence or unresolved root nodes, fall back to pure LLM diagnostics without strict critic gating.10. Implementation Plan & MilestonesPhase 1: Core Foundation & Symbolic Parser (Days 1–4)Implement non-destructive tokenizer (orto/core/tokenizer.py).Implement spaCy syntactic feature and dependency extractor (orto/core/syntax_engine.py).Build in-memory string patcher with reverse index shifting (orto/core/patcher.py).Unit test token and character offset alignment across irregular whitespace and punctuation.Phase 2: LLM Integration & Structured Schema (Days 5–8)Define Pydantic models for structured outputs (orto/llm/schemas.py).Implement OpenAI / LiteLLM API client wrapper with JSON enforcement (orto/llm/client.py).Construct linguistically conditioned system and user prompts injecting dependency priors (orto/llm/prompts.py).Verify zero formatting errors via automated schema validation tests.Phase 3: Neurosymbolic Critic & Refinement Loop (Days 9–12)Implement automated Morphosyntactic Agreement verifier (orto/critic/verifier.py).Implement tree integrity and orphan-clause detection.Build automated 1-turn retry reflection loop feeding parser assertion errors back to the LLM.Test against synthetic regression sets (e.g., singular subject + plural verb edge cases).Phase 4: Evaluation Suite & Interactive Frontend (Days 13–16)Implement the $F*{0.5}$ metric and ERRANT category evaluation script (benchmarks/evaluate.py).Run baseline ablations (Zero-shot vs. Classical vs. Orto) on sample_benchmark.jsonl.Build Streamlit visualizer (app.py) with clickable color-coded error badges and diagnostic cards.Complete README, publish GitHub repository, and verify clean single-command deployment.
