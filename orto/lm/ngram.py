"""
@file ngram.py
@description N-gram Language Model with Laplace smoothing, perplexity calculation, and edit fluency delta scoring
@module orto/lm
"""

import json
import math
import os
import re
from collections import Counter, defaultdict
from typing import Any, Dict, Iterable, List, Optional, Tuple


class NGramLanguageModel:
    """
    N-gram language model (Unigram, Bigram, and Trigram) with Laplace (add-k) smoothing.
    Provides likelihood scoring, perplexity calculation, and edit fluency evaluation.
    """

    def __init__(
        self,
        order: int = 2,
        k: float = 1.0,
        min_freq: int = 1,
    ) -> None:
        """
        Initializes the N-gram language model.

        Args:
            order: Maximum N-gram order (1 for unigram, 2 for bigram, 3 for trigram).
            k: Laplace smoothing parameter (add-k). Defaults to 1.0.
            min_freq: Minimum frequency threshold for vocabulary inclusion.
        """
        self.order = order
        self.k = k
        self.min_freq = min_freq

        # Vocab and counts
        self.vocab: set = {"<s>", "</s>", "<unk>"}
        self.unigram_counts: Counter = Counter()
        self.bigram_counts: Counter = Counter()
        self.trigram_counts: Counter = Counter()
        self.context_counts: Counter = Counter()
        self.total_tokens: int = 0
        self.is_trained: bool = False

    @staticmethod
    def tokenize(text: str) -> List[str]:
        """
        Tokenizes raw text into normalized words and punctuation symbols.

        Args:
            text: Input string.

        Returns:
            List of normalized string tokens.
        """
        if not text:
            return []
        # Non-destructive word & punctuation tokenizer
        tokens = re.findall(r"\w+|[^\w\s]", text.lower(), re.UNICODE)
        return tokens

    def train(self, sentences: Iterable[str]) -> "NGramLanguageModel":
        """
        Trains the N-gram language model by estimating frequency counts across a corpus.

        Args:
            sentences: Iterable of raw sentence strings.

        Returns:
            Self (trained instance).
        """
        tokenized_corpus: List[List[str]] = []
        raw_vocab_counts: Counter = Counter()

        for s in sentences:
            toks = self.tokenize(s)
            if toks:
                tokenized_corpus.append(toks)
                raw_vocab_counts.update(toks)

        # Build vocabulary based on frequency threshold
        self.vocab = {"<s>", "</s>", "<unk>"}
        for word, count in raw_vocab_counts.items():
            if count >= self.min_freq:
                self.vocab.add(word)

        self.unigram_counts.clear()
        self.bigram_counts.clear()
        self.trigram_counts.clear()
        self.context_counts.clear()
        self.total_tokens = 0

        # Accumulate counts with padding
        for toks in tokenized_corpus:
            normalized = [t if t in self.vocab else "<unk>" for t in toks]
            padded = ["<s>"] + normalized + ["</s>"]
            self.total_tokens += len(normalized)

            for i, w in enumerate(padded):
                self.unigram_counts[w] += 1

                if self.order >= 2 and i >= 1:
                    prev_w = padded[i - 1]
                    self.bigram_counts[(prev_w, w)] += 1
                    self.context_counts[prev_w] += 1

                if self.order >= 3 and i >= 2:
                    p2, p1 = padded[i - 2], padded[i - 1]
                    self.trigram_counts[(p2, p1, w)] += 1
                    self.context_counts[(p2, p1)] += 1

        self.is_trained = True
        return self

    @property
    def vocab_size(self) -> int:
        """Returns the size of the vocabulary |V|."""
        return max(len(self.vocab), 1)

    def bigram_probability(self, word: str, prev_word: str) -> float:
        """
        Computes Laplace-smoothed bigram conditional probability P_Laplace(word | prev_word).

        Formula:
            P(w_i | w_{i-1}) = ( C(w_{i-1}, w_i) + k ) / ( C(w_{i-1}) + k * |V| )
        """
        w = word if word in self.vocab else "<unk>"
        pw = prev_word if prev_word in self.vocab else "<unk>"

        count_bigram = self.bigram_counts.get((pw, w), 0)
        count_prev = self.unigram_counts.get(pw, 0)

        prob = (count_bigram + self.k) / (count_prev + (self.k * self.vocab_size))
        return prob

    def log_likelihood(self, text: str) -> float:
        """
        Computes the total log2-likelihood of the sentence under the Laplace-smoothed model.

        Formula:
            LL(W) = sum_{i=1}^N log2 P(w_i | w_{i-1})
        """
        toks = self.tokenize(text)
        if not toks:
            return 0.0

        padded = ["<s>"] + [t if t in self.vocab else "<unk>" for t in toks] + ["</s>"]
        log_prob = 0.0

        for i in range(1, len(padded)):
            prev_w = padded[i - 1]
            curr_w = padded[i]
            p = self.bigram_probability(curr_w, prev_w)
            log_prob += math.log2(p)

        return log_prob

    def perplexity(self, text: str) -> float:
        """
        Computes the perplexity of a sentence.

        Formula:
            PPL(W) = 2^( - LL(W) / N )
        """
        toks = self.tokenize(text)
        if not toks:
            return float("inf")

        ll = self.log_likelihood(text)
        # N includes the end token </s>
        n = len(toks) + 1
        return math.pow(2.0, -ll / n)

    def score_edit_fluency_delta(
        self, original_text: str, patched_text: str
    ) -> float:
        """
        Scores the change in fluency produced by an edit.

        Formula:
            Delta LL = LL(patched_text) - LL(original_text)

        A positive delta indicates that the patched text is more fluent/probable
        under the language model than the original uncorrected text.

        Args:
            original_text: Unmodified source sentence.
            patched_text: Sentence with candidate edit applied.

        Returns:
            Delta log-likelihood score.
        """
        ll_orig = self.log_likelihood(original_text)
        ll_patch = self.log_likelihood(patched_text)
        return ll_patch - ll_orig

    def save(self, filepath: str) -> None:
        """Serializes model counts and vocabulary to a JSON file."""
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        data = {
            "order": self.order,
            "k": self.k,
            "min_freq": self.min_freq,
            "vocab": list(self.vocab),
            "unigram_counts": dict(self.unigram_counts),
            "bigram_counts": {f"{k[0]}|||{k[1]}": v for k, v in self.bigram_counts.items()},
            "total_tokens": self.total_tokens,
            "is_trained": self.is_trained,
        }
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(data, f)

    @classmethod
    def load(cls, filepath: str) -> "NGramLanguageModel":
        """Loads a serialized model from a JSON file."""
        with open(filepath, "r", encoding="utf-8") as f:
            data = json.load(f)

        model = cls(
            order=data.get("order", 2),
            k=data.get("k", 1.0),
            min_freq=data.get("min_freq", 1),
        )
        model.vocab = set(data.get("vocab", []))
        model.unigram_counts = Counter(data.get("unigram_counts", {}))
        bigram_raw = data.get("bigram_counts", {})
        model.bigram_counts = Counter(
            {tuple(k.split("|||")): v for k, v in bigram_raw.items()}
        )
        model.total_tokens = data.get("total_tokens", 0)
        model.is_trained = data.get("is_trained", True)
        return model
