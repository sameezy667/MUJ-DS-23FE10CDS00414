# Assignment 2: Model Development, Symbolic Critic & Language Modeling

## 1. Overview & Objective
This assignment details the implementation of the core neurosymbolic pipeline components: the constrained LLM diagnostic engine, the symbolic regression critic, the Laplace-smoothed N-gram fluency model, and the ML confidence classifier.

## 2. Constrained LLM Hypothesis Generation
- **Structured Decoding:** Enforces Pydantic `OrtoAnalysis` JSON schema.
- **ERRANT Classification:** Every proposed edit is classified into standard ERRANT categories: `R:SPELL`, `R:VERB:SVA`, `R:VERB:TENSE`, `R:NOUN:NUM`, `R:PREP`, `M:DET`, `R:WO`, `R:OTHER`.
- **Pedagogical Enrichment:** Every edit must include the `linguistic_rule`, a clear `explanation`, and a paired `counterfactual_example`.

## 3. Symbolic Critic Invariant Verification
The `SymbolicCritic` (`orto/critic/verifier.py`) performs:
1. **Virtual Patching:** Applies candidate edits into an in-memory buffer using reverse offset indexing.
2. **Re-parsing:** Re-parses the virtual sentence with spaCy.
3. **Tree Connectivity Assertion:** Asserts no orphaned unresolved tokens (`dep_ == 'dep'`).
4. **Morphosyntactic Agreement:** Enforces number and person concord between subject heads and verb heads across 1st, 2nd, and 3rd person subjects.
5. **Self-Refinement Reflection:** On invariant violation, triggers a structured reflection cycle back to the generator.

## 4. Laplace-Smoothed N-Gram Language Model
- `NGramLanguageModel` (`orto/lm/ngram.py`) models word bigram conditional probabilities with add-1 (Laplace) smoothing:
  $$P(w_i \mid w_{i-1}) = \frac{C(w_{i-1}, w_i) + 1}{C(w_{i-1}) + |V|}$$
- Computes sentence perplexity and fluency delta ($\Delta \text{PPL} = \text{PPL}_{\text{orig}} - \text{PPL}_{\text{corr}}$).

## 5. ML Confidence Classifier & Routing
- `EditConfidenceClassifier` (`orto/ml/router.py`) extracts an 8-dimensional feature vector per candidate edit (span length, edit distance, ERRANT category, critic verdict, fluency score, token frequency) and predicts calibrated posterior probability of correctness.
