# Dataset Dictionary & M2 Schema Specification

## 1. M2 Format Overview
The M2 (MaxMatch) format is the standard gold-annotation format for Grammatical Error Correction benchmarks (such as BEA-2019 and CoNLL-2014).

### Record Structure
Each annotated sentence record consists of:
- **`S <sentence>`**: The original uncorrected sentence with tokens separated by single spaces.
- **`A <start> <end>|||<error_type>|||<correction>|||<required>|||<comment>|||<annotator_id>`**:
  - `start`: 0-indexed starting token offset (inclusive).
  - `end`: 0-indexed ending token offset (exclusive).
  - `error_type`: ERRANT taxonomy classification label (e.g. `R:VERB:SVA`, `R:SPELL`).
  - `correction`: The corrected replacement token string (or `-NONE-` for deletion).
  - `required`: `REQUIRED` if mandatory correction, `OPTIONAL` otherwise.
  - `comment`: Optional annotator commentary.
  - `annotator_id`: Numerical identifier of human expert annotator.

---

## 2. Dataset Benchmarks

| Dataset Name | Source Domain | Sentences | Annotators | Primary Usage |
|---|---|---|---|---|
| **BEA-2019 Dev** | Write & Improve / LOCNESS essays | 150 | Multi-annotator | Cross-domain evaluation & F0.5 scoring |
| **BEA-2019 Train** | Student English writing submissions | 500 | Single annotator | N-Gram LM & ML Router training |
| **CoNLL-2014 Test** | NUS Corpus of Learner English | 100 | Multi-annotator | Standard GEC test benchmark |
