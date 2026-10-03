"""
@file run_ablations.py
@description Comparative ablation runner evaluating LLM-only, symbolic-only, and full neurosymbolic pipeline with official ERRANT metrics
@module benchmarks
"""

import argparse
import sys
import time
from pathlib import Path
from typing import Any, Dict, List, Tuple

# Ensure project root is in sys.path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

import errant
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from benchmarks.evaluate import evaluate_dataset
from orto.core.syntax_engine import SyntaxEngine
from orto.critic.verifier import SymbolicCritic
from orto.llm.client import LLMClient
from orto.pipeline import OrtoEngine


def run_ablations(
    dataset_path: str,
    max_samples: int = None,
    mock_mode: bool = False,
) -> Dict[str, Any]:
    """
    Executes benchmark evaluation across three primary ablation configurations:
    1. Baseline A (LLM-Only): Unconstrained / Pure LLM generation without Symbolic Critic.
    2. Baseline B (Symbolic-Only): Classical dependency & morphological heuristics without generative LLM.
    3. Proposed (Full Neurosymbolic Pipeline): Syntax Priors + Constrained LLM + Symbolic Critic + Refinement.

    Args:
        dataset_path: Path to .m2 or .jsonl benchmark file.
        max_samples: Optional maximum number of sentences to evaluate.
        mock_mode: If True, uses deterministic offline linguistic engine for fast reproducible runs.

    Returns:
        Dict mapping configuration names to their evaluation metrics and ablation impact stats.
    """
    console = Console()
    console.print("\n[bold cyan]================================================================[/bold cyan]")
    console.print("[bold cyan]       Orto Neurosymbolic GEC — Architectural Ablation Study     [/bold cyan]")
    console.print("[bold cyan]================================================================[/bold cyan]\n")
    console.print(f"[dim]Dataset: {dataset_path} | Max samples: {max_samples or 'All'} | Offline Mock: {mock_mode}[/dim]\n")

    annotator = errant.load("en")
    syntax_engine = SyntaxEngine()
    critic = SymbolicCritic(syntax_engine)

    # 1. Configuration definitions
    configs = [
        (
            "Baseline A: LLM-Only (No Critic)",
            OrtoEngine(
                syntax_engine=syntax_engine,
                llm_client=LLMClient(mock_mode=mock_mode),
                critic=critic,
                enable_critic=False,
                max_refinements=0,
            ),
            "Generates edits without symbolic invariant checks; prone to false alarms on distractor nouns.",
        ),
        (
            "Baseline B: Symbolic-Only (Pure Rules)",
            OrtoEngine(
                syntax_engine=syntax_engine,
                llm_client=LLMClient(mock_mode=True),
                critic=critic,
                enable_critic=True,
                max_refinements=0,
            ),
            "Classical Universal Dependency & SVA heuristics only; high precision but low recall on open grammar.",
        ),
        (
            "Proposed: Orto Full Pipeline",
            OrtoEngine(
                syntax_engine=syntax_engine,
                llm_client=LLMClient(mock_mode=mock_mode),
                critic=critic,
                enable_critic=True,
                enable_ml_filter=True,
                max_refinements=1,
            ),
            "Syntax Priors + Constrained Few-Shot LLM + Symbolic Critic + ML Router Confidence Filter + Refinement.",
        ),
    ]

    ablation_table = Table(
        title="Comparative Ablation Matrix (ERRANT F_0.5 Evaluation)",
        header_style="bold magenta",
    )
    ablation_table.add_column("Pipeline Configuration", style="bold", min_width=32)
    ablation_table.add_column("TP", justify="center", style="green")
    ablation_table.add_column("FP", justify="center", style="red")
    ablation_table.add_column("FN", justify="center", style="yellow")
    ablation_table.add_column("Precision (%)", justify="right", style="cyan")
    ablation_table.add_column("Recall (%)", justify="right", style="cyan")
    ablation_table.add_column("F_0.5 (%)", justify="right", style="bold green")
    ablation_table.add_column("Latency (s)", justify="right", style="dim")

    results_by_config: Dict[str, Dict[str, Any]] = {}

    for name, engine, desc in configs:
        console.print(f"[bold yellow]→ Evaluating {name}...[/bold yellow]")
        t0 = time.perf_counter()
        res = evaluate_dataset(dataset_path, engine, annotator=annotator, max_samples=max_samples)
        elapsed = time.perf_counter() - t0
        res["latency_sec"] = elapsed
        res["description"] = desc
        results_by_config[name] = res

        ablation_table.add_row(
            name,
            str(res["tp"]),
            str(res["fp"]),
            str(res["fn"]),
            f"{res['precision'] * 100:.2f}%",
            f"{res['recall'] * 100:.2f}%",
            f"{res['f_05'] * 100:.2f}%",
            f"{elapsed:.2f}s",
        )

    console.print("\n", ablation_table, "\n")

    # 2. Symbolic Critic Impact Analysis
    llm_res = results_by_config["Baseline A: LLM-Only (No Critic)"]
    full_res = results_by_config["Proposed: Orto Full Pipeline"]

    delta_p = (full_res["precision"] - llm_res["precision"]) * 100
    delta_f05 = (full_res["f_05"] - llm_res["f_05"]) * 100
    fp_reduction = (
        ((llm_res["fp"] - full_res["fp"]) / llm_res["fp"] * 100)
        if llm_res["fp"] > 0
        else 0.0
    )

    critic_panel_text = (
        f"[bold green]✓ Precision Gain:[/bold green] [bold cyan]{delta_p:+.2f}%[/bold cyan] "
        f"({llm_res['precision']*100:.2f}% → {full_res['precision']*100:.2f}%)\n"
        f"[bold green]✓ F_0.5 Quality Gain:[/bold green] [bold yellow]{delta_f05:+.2f}%[/bold yellow] "
        f"({llm_res['f_05']*100:.2f}% → {full_res['f_05']*100:.2f}%)\n"
        f"[bold green]✓ False Positive Reduction:[/bold green] [bold red]{llm_res['fp']} FP → {full_res['fp']} FP[/bold red] "
        f"([bold green]{fp_reduction:.1f}% reduction in false alarms[/bold green])\n"
        f"[bold green]✓ Clean Sentence Preservation:[/bold green] {full_res['clean_sentences_preserved']}/{full_res['clean_sentences_tested']} clean sentences untouched "
        f"(vs {llm_res['clean_sentences_preserved']}/{llm_res['clean_sentences_tested']} in LLM-only)"
    )

    console.print(
        Panel(
            critic_panel_text,
            title="[bold green]Symbolic Critic Ablation Impact (Proof of Anti-Hallucination)[/bold green]",
            border_style="green",
            expand=False,
        )
    )

    # 3. Category Breakdown Comparison Table
    cat_comp_table = Table(
        title="Category-Level Precision Breakdown: LLM-Only vs Full Pipeline",
        header_style="bold blue",
    )
    cat_comp_table.add_column("ERRANT Category", style="bold")
    cat_comp_table.add_column("LLM-Only FP", justify="center", style="red")
    cat_comp_table.add_column("Full Pipeline FP", justify="center", style="green")
    cat_comp_table.add_column("LLM-Only Prec (%)", justify="right")
    cat_comp_table.add_column("Full Prec (%)", justify="right", style="cyan")
    cat_comp_table.add_column("Δ Precision", justify="right", style="bold green")

    all_cats = sorted(
        set(llm_res["categories"].keys()) | set(full_res["categories"].keys())
    )
    for cat in all_cats:
        llm_stat = llm_res["categories"].get(cat, {"tp": 0, "fp": 0, "fn": 0})
        full_stat = full_res["categories"].get(cat, {"tp": 0, "fp": 0, "fn": 0})

        llm_tp, llm_fp = llm_stat["tp"], llm_stat["fp"]
        full_tp, full_fp = full_stat["tp"], full_stat["fp"]

        p_llm = llm_tp / (llm_tp + llm_fp) if (llm_tp + llm_fp) > 0 else 0.0
        p_full = full_tp / (full_tp + full_fp) if (full_tp + full_fp) > 0 else 0.0
        d_p = (p_full - p_llm) * 100

        if llm_tp + llm_fp > 0 or full_tp + full_fp > 0:
            cat_comp_table.add_row(
                cat,
                str(llm_fp),
                str(full_fp),
                f"{p_llm * 100:.1f}%",
                f"{p_full * 100:.1f}%",
                f"{d_p:+.1f}%" if d_p != 0 else "0.0%",
            )

    console.print("\n", cat_comp_table, "\n")

    return {
        "results": results_by_config,
        "delta_precision": delta_p,
        "delta_f05": delta_f05,
        "fp_reduction_percent": fp_reduction,
    }


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Run comparative ablation study across LLM-only, symbolic-only, and Orto full pipeline"
    )
    parser.add_argument(
        "--data",
        type=str,
        default="data/bea19_dev_sample.m2",
        help="Path to .m2 or .jsonl benchmark dataset",
    )
    parser.add_argument(
        "--max-samples",
        type=int,
        default=None,
        help="Limit number of benchmark samples for faster ablation runs",
    )
    parser.add_argument(
        "--mock",
        action="store_true",
        help="Use deterministic offline linguistic engine for instant reproducible runs",
    )
    args = parser.parse_args()
    run_ablations(args.data, max_samples=args.max_samples, mock_mode=args.mock)


if __name__ == "__main__":
    main()
