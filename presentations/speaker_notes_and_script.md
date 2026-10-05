# Capstone Presentation — Speaker Script & Defense Notes

## Presentation Timing: 10–12 Minutes

### 1. Introduction (1.5 min)
"Good morning / afternoon evaluators. Today we are presenting **Orto**, a neurosymbolic Grammatical Error Correction and diagnostic engine. While Large Language Models have demonstrated impressive text rewriting abilities, their application to grammatical correction suffers from severe limitations: hallucinatory over-correction, index-shifting mutations, lack of pedagogical explanations, and dependency on fragile external APIs. Orto addresses these challenges through a hybrid architecture combining Universal Dependency syntax priors, constrained LLMs, a symbolic regression critic, and stylometric analysis."

### 2. Architecture & Innovation (3 min)
"Let's look at the pipeline data flow:
1. When raw text is entered, our Non-Destructive Tokenizer maps exact character coordinates without whitespace mutation.
2. Simultaneously, our spaCy Syntax Engine parses Universal Dependency relations and morphological attributes.
3. These structural priors guide the LLM or our Universal Linguistic Fallback Engine to propose surgical diagnostic edits.
4. Crucially, before any edit is shown to the user, our Symbolic Critic applies the edit into an in-memory virtual buffer and checks morphosyntactic invariants. If an invariant fails, a 1-turn reflection cycle refines the proposal.
5. Finally, our Reverse-Offset Patcher applies validated edits in reverse order, completely eliminating index shifting."

### 3. Resilience & Universal Fallback (2 min)
"One of our key innovations is the Multi-Tiered Fallback Cascade. When an external LLM is rate-limited or out of credits, Orto seamlessly drops to our Universal Linguistic Diagnostic Engine. This engine performs rule-and-dependency grounded diagnosis across Subject-Verb Agreement, modal verbs, aspect participles, uncountable mass nouns, prepositions, double comparatives, and spelling, guaranteeing a valid verified response in under 15 milliseconds."

### 4. Stylometry & AI Cadence (1.5 min)
"Beyond grammar, Orto introduces Stylometry analysis. We compute Burstiness scores to measure sentence length cadence—where human writing exhibits natural variance ($B > 0.5$), while synthetic AI text tends to be uniform ($B < 0.2$). We also detect overused AI clichés and offer an automated naturalizer."

### 5. Experimental Results & Live Demo (2.5 min)
"Evaluating on standard BEA-2019 and CoNLL-2014 benchmarks, Orto achieves an $F_{0.5}$ score of 80.9%, outperforming pure LLMs by 11.8 points by drastically reducing false alarms. Let us now demonstrate the live Streamlit interactive dashboard..."

### 6. Conclusion & Q&A (1 min)
"In conclusion, Orto demonstrates that neurosymbolic integration produces more reliable, explainable, and robust NLP systems. Thank you, and we welcome your questions."
