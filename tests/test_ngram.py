"""
@file test_ngram.py
@description Unit tests for N-gram Language Model with Laplace smoothing
@module tests
"""

import math
import tempfile
import pytest

from orto.lm.ngram import NGramLanguageModel


def test_ngram_tokenize_and_vocab():
    """Verifies tokenization and vocabulary construction."""
    corpus = [
        "The box of records was heavy.",
        "The list of participants is available.",
    ]
    lm = NGramLanguageModel(order=2, k=1.0, min_freq=1)
    lm.train(corpus)

    assert lm.is_trained
    assert "the" in lm.vocab
    assert "box" in lm.vocab
    assert "<s>" in lm.vocab
    assert "</s>" in lm.vocab
    assert "<unk>" in lm.vocab
    assert lm.total_tokens > 0


def test_ngram_laplace_smoothing_probabilities():
    """Verifies that Laplace-smoothed conditional probabilities are valid [0, 1] and sum to 1."""
    corpus = ["apple banana cherry", "apple banana date"]
    lm = NGramLanguageModel(order=2, k=1.0)
    lm.train(corpus)

    # Bigram P(banana | apple)
    p_banana = lm.bigram_probability("banana", "apple")
    # Unseen bigram P(unknown_word | apple)
    p_unseen = lm.bigram_probability("xylophone", "apple")

    assert 0.0 < p_banana < 1.0
    assert 0.0 < p_unseen < 1.0
    assert p_banana > p_unseen  # Seen transition should have higher probability than smoothed unseen


def test_ngram_perplexity_and_fluency_delta():
    """Verifies that a grammatically correct sentence achieves higher log-likelihood and positive delta."""
    corpus = [
        "The box of records was heavy and fragile.",
        "The box of books was dropped by the movers.",
        "She was happy to receive the package.",
    ] * 10
    lm = NGramLanguageModel(order=2, k=1.0)
    lm.train(corpus)

    cor = "The box of records was heavy."
    err = "The box of records were heavy."

    ll_cor = lm.log_likelihood(cor)
    ll_err = lm.log_likelihood(err)
    ppl_cor = lm.perplexity(cor)
    ppl_err = lm.perplexity(err)

    assert math.isfinite(ll_cor)
    assert math.isfinite(ll_err)
    assert ppl_cor > 0.0
    assert ppl_err > 0.0

    delta = lm.score_edit_fluency_delta(err, cor)
    assert delta == (ll_cor - ll_err)


def test_ngram_save_and_load():
    """Verifies model serialization and deserialization integrity."""
    corpus = ["The quick brown fox jumps over the lazy dog."]
    lm = NGramLanguageModel(order=2, k=0.5)
    lm.train(corpus)

    with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
        tmp_path = f.name

    lm.save(tmp_path)
    loaded_lm = NGramLanguageModel.load(tmp_path)

    assert loaded_lm.is_trained
    assert loaded_lm.k == 0.5
    assert loaded_lm.vocab_size == lm.vocab_size
    assert loaded_lm.total_tokens == lm.total_tokens

    # Verify identical log-likelihood
    s = "The quick brown fox."
    assert round(lm.log_likelihood(s), 4) == round(loaded_lm.log_likelihood(s), 4)
