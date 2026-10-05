# Assignment 1: Dataset Collection, Sourcing & Preprocessing

## 1. Overview & Objective
The goal of this assignment is to establish standard NLP evaluation datasets for Grammatical Error Correction (GEC) and develop a non-destructive character-level offset tokenizer that preserves exact character indices across arbitrary punctuation and whitespace.

## 2. Dataset Sourcing
1. **BEA-2019 Shared Task Dataset (Write & Improve + LOCNESS):**
   - Source format: M2 annotation files containing source sentences and standard annotations:
     `A start_token end_token|||Error_Type|||Correction|||Required|||...|||Annotator_ID`
   - Data Split: 500 training sentences, 150 development evaluation sentences.
2. **CoNLL-2014 Shared Task Benchmark:**
   - 100 benchmark test sentences curated across grammatical, orthographic, and prepositional categories.

## 3. Non-Destructive Tokenization Architecture
Standard NLP tokenizers often modify whitespace or alter index alignments during string manipulation. Orto implements `NonDestructiveTokenizer` in `orto/core/tokenizer.py` with:
- Alphanumeric + contraction regex: `r"\w+(?:['’]\w+)?|[^\w\s]"`
- Exact coordinate guarantee: `text[token.start_char : token.end_char] == token.text`
- Validated span coordinates against original sentence buffers.

## 4. Syntactic Feature Extraction
Using spaCy's `en_core_web_sm` model, we extract:
- Universal Dependency Triples: `(Governor, Relation, Dependent)`
- Morphological features: `Number=Sing/Plur`, `Tense=Pres/Past`, `Person=1/2/3`, `VerbForm=Inf/Fin/Part`
- Subject-Verb Agreement pairs: extracted via `nsubj` / `nsubjpass` traversal to evaluate agreement mismatches.
