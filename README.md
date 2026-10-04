# Orto — Neurosymbolic Grammar Error Correction

Orto corrects English grammar with minimal, explained edits. An LLM proposes
corrections, a symbolic critic checks them against the dependency parse, and a
small trained classifier filters likely false alarms.

## How it works
1. **Parse** the sentence with spaCy to get dependency and morphology features.
2. **Propose** edits with an LLM (`gpt-4o-mini` via OpenRouter), using prompts
   in `prompts/prompts.yaml`.
3. **Verify** each edit with the symbolic critic (e.g. subject-verb agreement).
4. **Filter** with a logistic-regression edit router and bigram fluency score.
5. **Patch** the original text with minimal character-span edits.

## Setup
    git clone <repo-url> && cd Orto
    python -m venv .venv && source .venv/bin/activate
    pip install -r requirements.txt
    python -m spacy download en_core_web_sm
    cp .env.example .env   # add your OPENROUTER_API_KEY

## Usage
    python -m orto.cli "The box of records were heavy."

## Configuration
- `config/config.yaml` — model, temperature, router threshold, paths
- `prompts/prompts.yaml` — system and task prompts

## What is trained vs. pre-trained
| Component | Type |
|---|---|
| Edit router | Trained by us (500 BEA-2019 train sentences) |
| Bigram LM | Trained by us (BEA-2019 train) |
| spaCy parser, GPT-4o-mini | Pre-trained |
| Symbolic critic, patcher | Rule-based |

## Evaluation
Scored on BEA-2019 dev (150 sentences) and CoNLL-2014 (100 sentences).
Orto reduces false positives versus LLM-only but lowers recall; F0.5 changes
are within confidence intervals. See `docs/evaluation.md` for tables and limits.

## Tests
    pytest

## Project layout
    orto/        core package    prompts/     prompt files
    config/      settings        benchmarks/  evaluation scripts
    tests/       unit tests
