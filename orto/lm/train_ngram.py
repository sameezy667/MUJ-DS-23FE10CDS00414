"""
@file train_ngram.py
@description Corpus training script for N-gram Language Model with Laplace smoothing
@module orto/lm
"""

import argparse
import os
import sys
import time
from pathlib import Path
from typing import List

# Ensure project root in sys.path
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from rich.console import Console
from rich.table import Table

from orto.lm.ngram import NGramLanguageModel


def extract_sentences_from_m2(m2_path: str, max_sentences: int = 50000) -> List[str]:
    """Extracts raw sentence strings from an M2 benchmark corpus."""
    sentences: List[str] = []
    if not os.path.exists(m2_path):
        return sentences

    with open(m2_path, "r", encoding="utf-8") as f:
        for line in f:
            if line.startswith("S "):
                s = line[2:].strip()
                if s:
                    sentences.append(s)
                    if len(sentences) >= max_sentences:
                        break
    return sentences


def get_default_training_sentences() -> List[str]:
    """Returns a curated set of clean English reference sentences if no M2 file is provided."""
    return [
        "The box of old vintage vinyl records was dropped by the movers.",
        "The list of registered participants is available online.",
        "The results of the preliminary investigation were inconclusive.",
        "The team of experienced research scientists has published their findings.",
        "She will definitely receive the package until Friday.",
        "The government provides much information to the public.",
        "We are very interested in participating in this research project.",
        "There is no doubt that the committee will approve the budget.",
        "An unexpected error occurred during the file upload process.",
        "Many students were present at the annual linguistics conference.",
        "Regular exercise and proper nutrition are essential for good health.",
        "The development of new artificial intelligence systems requires rigorous safety testing.",
        "Technological advancements have significantly transformed the global communication landscape.",
        "The university offers a diverse range of undergraduate and postgraduate academic degrees.",
        "Environmental scientists emphasize the urgent necessity of reducing carbon emissions.",
    ]


def train_and_save_ngram(
    corpus_path: str = "data/downloads/wi+locness/m2/ABC.train.gold.bea19.m2",
    output_path: str = "data/models/ngram_bigram.json",
    order: int = 2,
    k: float = 1.0,
    min_freq: int = 2,
    max_sentences: int = 30000,
) -> NGramLanguageModel:
    """
    Trains an N-gram language model on the specified corpus and saves to disk.

    Args:
        corpus_path: Path to training corpus (.m2 or text file).
        output_path: Path to save the serialized JSON model.
        order: N-gram order (default 2 for bigram).
        k: Laplace smoothing constant.
        min_freq: Minimum token frequency for vocabulary.
        max_sentences: Maximum sentences to train on.

    Returns:
        Trained NGramLanguageModel instance.
    """
    console = Console()
    console.print("\n[bold cyan]=== Training N-gram Language Model with Laplace Smoothing ===[/bold cyan]\n")

    sentences = extract_sentences_from_m2(corpus_path, max_sentences=max_sentences)
    if not sentences:
        console.print("[yellow]! Training corpus not found or empty, using curated reference sentences.[/yellow]")
        sentences = get_default_training_sentences() * 50

    console.print(f"[dim]Loaded {len(sentences)} training sentences from {corpus_path}[/dim]")

    t0 = time.perf_counter()
    lm = NGramLanguageModel(order=order, k=k, min_freq=min_freq)
    lm.train(sentences)
    elapsed = time.perf_counter() - t0

    # Save to disk
    lm.save(output_path)
    console.print(f"[green]✓ Trained N-gram model saved to {output_path} in {elapsed:.2f}s[/green]\n")

    # Evaluation on probe sentences
    probe_pairs = [
        (
            "The box of records was dropped .",
            "The box of records were dropped .",
            "SVA singular head vs plural distractor",
        ),
        (
            "She will definitely receive the package .",
            "She will definately recieve the package .",
            "Orthographic spelling check",
        ),
        (
            "There is no doubt about it .",
            "Their is no doubt about it .",
            "Homophone existential 'there'",
        ),
    ]

    table = Table(
        title="N-Gram Fluency Probe Evaluations",
        header_style="bold magenta",
    )
    table.add_column("Linguistic Probe", style="bold")
    table.add_column("Correct (PPL)", justify="right", style="green")
    table.add_column("Erroneous (PPL)", justify="right", style="red")
    table.add_column("Δ Log-Likelihood", justify="right", style="cyan")
    table.add_column("Fluency Verdict", justify="center", style="bold")

    for cor, err, desc in probe_pairs:
        ppl_cor = lm.perplexity(cor)
        ppl_err = lm.perplexity(err)
        delta_ll = lm.score_edit_fluency_delta(err, cor)
        verdict = "✓ Fluency Improved" if delta_ll > 0 else "✗ Unfavorable"

        table.add_row(
            desc,
            f"{ppl_cor:.1f}",
            f"{ppl_err:.1f}",
            f"{delta_ll:+.2f} bits",
            verdict,
        )

    console.print(table)
    console.print(f"\n[bold green]✓ Vocabulary Size:[/bold green] |V| = {lm.vocab_size}")
    console.print(f"[bold green]✓ Total Tokens Processed:[/bold green] N = {lm.total_tokens}")
    console.print(f"[bold green]✓ Unique Bigrams Counted:[/bold green] B = {len(lm.bigram_counts)}\n")

    return lm


def main() -> None:
    parser = argparse.ArgumentParser(description="Train Laplace-Smoothed N-gram LM on GEC corpus")
    parser.add_argument(
        "--corpus",
        type=str,
        default="data/downloads/wi+locness/m2/ABC.train.gold.bea19.m2",
        help="Path to training M2 or text corpus",
    )
    parser.add_argument(
        "--output",
        type=str,
        default="data/models/ngram_bigram.json",
        help="Path to save serialized JSON model",
    )
    parser.add_argument(
        "--order",
        type=int,
        default=2,
        help="N-gram order (default 2 for bigram)",
    )
    parser.add_argument(
        "--k",
        type=float,
        default=1.0,
        help="Laplace add-k smoothing parameter (default 1.0)",
    )
    parser.add_argument(
        "--min-freq",
        type=int,
        default=2,
        help="Minimum word frequency threshold",
    )
    parser.add_argument(
        "--max-sentences",
        type=int,
        default=30000,
        help="Maximum training sentences",
    )
    args = parser.parse_args()

    train_and_save_ngram(
        corpus_path=args.corpus,
        output_path=args.output,
        order=args.order,
        k=args.k,
        min_freq=args.min_freq,
        max_sentences=args.max_sentences,
    )


if __name__ == "__main__":
    main()
