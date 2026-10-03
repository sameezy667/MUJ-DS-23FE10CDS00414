"""
@file evaluate.py
@description Precision, Recall, and F_0.5 evaluation harness for Orto GEC benchmarks using official ERRANT scoring
@module benchmarks
"""

import argparse
import json
import os
import sys
import tempfile
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

# Ensure project root is in sys.path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

import errant
from rich.console import Console
from rich.table import Table

from orto.pipeline import OrtoEngine


def compute_f_beta(precision: float, recall: float, beta: float = 0.5) -> float:
    """
    Computes F_beta score (defaults to F_0.5 for GEC, weighting precision 2x over recall).

    Args:
        precision: Precision score [0.0, 1.0].
        recall: Recall score [0.0, 1.0].
        beta: Weighting parameter (0.5 for standard GEC).

    Returns:
        F_beta metric [0.0, 1.0].
    """
    if precision + recall == 0.0:
        return 0.0
    beta_sq = beta**2
    return ((1 + beta_sq) * precision * recall) / ((beta_sq * precision) + recall)


def parse_m2_file(m2_path: str) -> List[Dict[str, Any]]:
    """
    Parses a standard M2 file (BEA-2019 / CoNLL-2014) into structured sentence records.

    Args:
        m2_path: Path to .m2 file.

    Returns:
        List of dicts containing source text tokens, raw sentence, and gold edits.
    """
    records: List[Dict[str, Any]] = []
    with open(m2_path, "r", encoding="utf-8") as f:
        current_sentence = None
        current_edits = []
        for line in f:
            line = line.rstrip("\r\n")
            if not line:
                if current_sentence is not None:
                    records.append(
                        {
                            "input": current_sentence,
                            "edits": current_edits,
                        }
                    )
                    current_sentence = None
                    current_edits = []
            elif line.startswith("S "):
                current_sentence = line[2:].strip()
                current_edits = []
            elif line.startswith("A "):
                parts = line[2:].split("|||")
                if len(parts) >= 6:
                    span_tokens = parts[0].split()
                    start_tok = int(span_tokens[0])
                    end_tok = int(span_tokens[1])
                    err_type = parts[1]
                    correction = parts[2]
                    annotator_id = int(parts[5]) if parts[5].isdigit() else 0
                    if err_type != "noop":
                        current_edits.append(
                            {
                                "start_tok": start_tok,
                                "end_tok": end_tok,
                                "errant_type": err_type,
                                "replacement": correction,
                                "annotator_id": annotator_id,
                            }
                        )

        if current_sentence is not None:
            records.append(
                {
                    "input": current_sentence,
                    "edits": current_edits,
                }
            )

    return records


def parse_jsonl_file(jsonl_path: str) -> List[Dict[str, Any]]:
    """
    Parses a JSONL benchmark dataset into structured records.

    Args:
        jsonl_path: Path to .jsonl file.

    Returns:
        List of benchmark records.
    """
    records: List[Dict[str, Any]] = []
    with open(jsonl_path, "r", encoding="utf-8") as f:
        for line in f:
            if line.strip():
                records.append(json.loads(line))
    return records


def evaluate_dataset(
    dataset_path: str,
    engine: OrtoEngine,
    annotator: Optional[Any] = None,
    max_samples: Optional[int] = None,
) -> Dict[str, Any]:
    """
    Evaluates Orto on a benchmark dataset (M2 or JSONL) using official ERRANT scoring.

    Args:
        dataset_path: Path to .m2 or .jsonl benchmark file.
        engine: OrtoEngine instance to evaluate.
        annotator: Optional pre-loaded errant Annotator instance.
        max_samples: Optional limit on the number of samples to evaluate.

    Returns:
        Dictionary containing global metrics (P, R, F0.5), category breakdown, and false alarm stats.
    """
    if annotator is None:
        annotator = errant.load("en")

    if dataset_path.endswith(".m2"):
        records = parse_m2_file(dataset_path)
    else:
        records = parse_jsonl_file(dataset_path)

    if max_samples is not None and max_samples > 0:
        records = records[:max_samples]

    global_tp = 0
    global_fp = 0
    global_fn = 0

    category_stats: Dict[str, Dict[str, int]] = defaultdict(
        lambda: {"tp": 0, "fp": 0, "fn": 0}
    )

    clean_sentences_tested = 0
    clean_sentences_preserved = 0
    false_alarms_on_clean = 0

    for item in records:
        source_text = item["input"]
        gold_edits = item.get("edits", [])
        is_clean_gold = len(gold_edits) == 0

        if is_clean_gold:
            clean_sentences_tested += 1

        # Run Orto pipeline
        response = engine.analyze(source_text)
        corrected_text = response.corrected_text

        # Parse source and hypothesis with ERRANT
        orig_doc = annotator.parse(source_text)
        hyp_doc = annotator.parse(corrected_text)
        hyp_edits = annotator.annotate(orig_doc, hyp_doc)

        if is_clean_gold:
            if len(hyp_edits) == 0:
                clean_sentences_preserved += 1
            else:
                false_alarms_on_clean += len(hyp_edits)

        matched_hyp_indices = set()
        matched_gold_indices = set()

        # Match hypothesis edits against gold edits
        for h_idx, h_edit in enumerate(hyp_edits):
            h_start = h_edit.o_start
            h_end = h_edit.o_end
            h_rep = h_edit.c_str.strip().lower()
            h_type = h_edit.type

            found_match = False
            for g_idx, g_edit in enumerate(gold_edits):
                if g_idx in matched_gold_indices:
                    continue

                g_start = g_edit.get("start_tok")
                g_end = g_edit.get("end_tok")
                g_rep = g_edit.get("replacement", "").strip().lower()
                g_type = g_edit.get("errant_type", "R:OTHER")

                # If token offsets are not present (e.g. char-offset jsonl), use text match
                if g_start is None:
                    # Fallback character level span match
                    g_char_start = g_edit.get("start_char", -1)
                    if g_char_start >= 0 and g_rep == h_rep:
                        found_match = True
                        matched_hyp_indices.add(h_idx)
                        matched_gold_indices.add(g_idx)
                        global_tp += 1
                        category_stats[g_type]["tp"] += 1
                        break
                else:
                    # Standard ERRANT span + replacement matching
                    if h_start == g_start and h_end == g_end and h_rep == g_rep:
                        found_match = True
                        matched_hyp_indices.add(h_idx)
                        matched_gold_indices.add(g_idx)
                        global_tp += 1
                        category_stats[g_type]["tp"] += 1
                        break

            if not found_match:
                global_fp += 1
                category_stats[h_type]["fp"] += 1

        for g_idx, g_edit in enumerate(gold_edits):
            if g_idx not in matched_gold_indices:
                global_fn += 1
                g_type = g_edit.get("errant_type", "R:OTHER")
                category_stats[g_type]["fn"] += 1

    precision = global_tp / (global_tp + global_fp) if (global_tp + global_fp) > 0 else 0.0
    recall = global_tp / (global_tp + global_fn) if (global_tp + global_fn) > 0 else 0.0
    f_05 = compute_f_beta(precision, recall, beta=0.5)

    return {
        "samples_evaluated": len(records),
        "tp": global_tp,
        "fp": global_fp,
        "fn": global_fn,
        "precision": precision,
        "recall": recall,
        "f_05": f_05,
        "clean_sentences_tested": clean_sentences_tested,
        "clean_sentences_preserved": clean_sentences_preserved,
        "false_alarms_on_clean": false_alarms_on_clean,
        "categories": category_stats,
    }


def main() -> None:
    """CLI entry point for running GEC evaluation."""
    parser = argparse.ArgumentParser(description="Evaluate Orto GEC performance with ERRANT")
    parser.add_argument(
        "--data",
        type=str,
        default="data/bea19_dev_sample.m2",
        help="Path to .m2 or .jsonl benchmark dataset",
    )
    parser.add_argument(
        "--no-critic",
        action="store_true",
        help="Disable Symbolic Critic verification for ablation testing",
    )
    parser.add_argument(
        "--max-samples",
        type=int,
        default=None,
        help="Limit number of evaluation samples",
    )
    parser.add_argument(
        "--mock",
        action="store_true",
        help="Use deterministic offline linguistic engine for instant reproducible runs",
    )
    args = parser.parse_args()

    console = Console()
    console.print("\n[bold cyan]=== Orto Neurosymbolic GEC Benchmark Runner (ERRANT M2) ===[/bold cyan]\n")
    console.print(f"[dim]Dataset: {args.data} | Critic Enabled: {not args.no_critic} | Offline Mock: {args.mock}[/dim]\n")

    engine = OrtoEngine(
        enable_critic=not args.no_critic,
        llm_client=None if not args.mock else __import__("orto.llm.client", fromlist=["LLMClient"]).LLMClient(mock_mode=True),
    )
    results = evaluate_dataset(args.data, engine, max_samples=args.max_samples)

    # Summary Table
    summary_table = Table(
        title="Global GEC Metrics (Official ERRANT F_0.5 Evaluation)",
        header_style="bold magenta",
    )
    summary_table.add_column("Samples", justify="center")
    summary_table.add_column("TP", justify="center", style="green")
    summary_table.add_column("FP", justify="center", style="red")
    summary_table.add_column("FN", justify="center", style="yellow")
    summary_table.add_column("Precision (%)", justify="right", style="cyan")
    summary_table.add_column("Recall (%)", justify="right", style="cyan")
    summary_table.add_column("F_0.5 Score (%)", justify="right", style="bold green")

    summary_table.add_row(
        str(results["samples_evaluated"]),
        str(results["tp"]),
        str(results["fp"]),
        str(results["fn"]),
        f"{results['precision'] * 100:.2f}%",
        f"{results['recall'] * 100:.2f}%",
        f"{results['f_05'] * 100:.2f}%",
    )
    console.print(summary_table)

    # ERRANT Breakdown Table
    cat_table = Table(title="ERRANT Taxonomy Category Breakdown", header_style="bold blue")
    cat_table.add_column("ERRANT Category", style="bold")
    cat_table.add_column("TP", justify="center", style="green")
    cat_table.add_column("FP", justify="center", style="red")
    cat_table.add_column("FN", justify="center", style="yellow")
    cat_table.add_column("Precision (%)", justify="right")
    cat_table.add_column("Recall (%)", justify="right")
    cat_table.add_column("F_0.5 (%)", justify="right", style="bold")

    for cat, stats in sorted(results["categories"].items()):
        tp = stats["tp"]
        fp = stats["fp"]
        fn = stats["fn"]
        p = tp / (tp + fp) if (tp + fp) > 0 else 0.0
        r = tp / (tp + fn) if (tp + fn) > 0 else 0.0
        f05 = compute_f_beta(p, r, beta=0.5)

        cat_table.add_row(
            cat,
            str(tp),
            str(fp),
            str(fn),
            f"{p * 100:.1f}%",
            f"{r * 100:.1f}%",
            f"{f05 * 100:.1f}%",
        )
    console.print("\n", cat_table, "\n")


if __name__ == "__main__":
    main()
