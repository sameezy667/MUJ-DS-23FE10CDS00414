"""
@file test_benchmark_eval.py
@description Unit and integration tests for ERRANT benchmark evaluation and ablation study runners
@module tests
"""

import tempfile
import pytest

from benchmarks.evaluate import compute_f_beta, evaluate_dataset, parse_jsonl_file, parse_m2_file
from benchmarks.run_ablations import run_ablations
from orto.pipeline import OrtoEngine


def test_compute_f_beta_standard_weights():
    """Verifies that F_0.5 weighs precision twice as heavily as recall."""
    p1, r1 = 0.8, 0.4
    f05_1 = compute_f_beta(p1, r1, beta=0.5)

    p2, r2 = 0.4, 0.8
    f05_2 = compute_f_beta(p2, r2, beta=0.5)

    assert f05_1 > f05_2
    assert 0.0 <= f05_1 <= 1.0
    assert compute_f_beta(0.0, 0.0) == 0.0


def test_parse_m2_file_structure():
    """Verifies that standard M2 files are parsed into structured sentence records."""
    sample_m2 = (
        "S The box of records were heavy .\n"
        "A 4 5|||R:VERB:SVA|||was|||REQUIRED|||-NONE-|||0\n"
        "\n"
        "S She has three book .\n"
        "A 3 4|||R:NOUN:NUM|||books|||REQUIRED|||-NONE-|||0\n"
    )
    with tempfile.NamedTemporaryFile(mode="w", suffix=".m2", delete=False) as f:
        f.write(sample_m2)
        f_path = f.name

    records = parse_m2_file(f_path)
    assert len(records) == 2
    assert records[0]["input"] == "The box of records were heavy ."
    assert len(records[0]["edits"]) == 1
    assert records[0]["edits"][0]["errant_type"] == "R:VERB:SVA"
    assert records[0]["edits"][0]["replacement"] == "was"


def test_evaluate_dataset_errant_m2():
    """Verifies that evaluate_dataset computes valid ERRANT TP, FP, FN, and F_0.5 scores."""
    sample_m2 = (
        "S The box of records were heavy .\n"
        "A 4 5|||R:VERB:SVA|||was|||REQUIRED|||-NONE-|||0\n"
        "\n"
        "S She will definately attend .\n"
        "A 2 3|||R:SPELL|||definitely|||REQUIRED|||-NONE-|||0\n"
    )
    with tempfile.NamedTemporaryFile(mode="w", suffix=".m2", delete=False) as f:
        f.write(sample_m2)
        f_path = f.name

    engine = OrtoEngine(enable_critic=True)
    results = evaluate_dataset(f_path, engine)

    assert results["samples_evaluated"] == 2
    assert results["tp"] >= 1
    assert 0.0 <= results["precision"] <= 1.0
    assert 0.0 <= results["recall"] <= 1.0
    assert 0.0 <= results["f_05"] <= 1.0
    assert "categories" in results


def test_run_ablations_offline():
    """Verifies that run_ablations executes all 3 tiers and returns delta precision."""
    sample_m2 = (
        "S The box of records were heavy .\n"
        "A 4 5|||R:VERB:SVA|||was|||REQUIRED|||-NONE-|||0\n"
        "\n"
        "S The team of researchers has completed the study .\n"
    )
    with tempfile.NamedTemporaryFile(mode="w", suffix=".m2", delete=False) as f:
        f.write(sample_m2)
        f_path = f.name

    ablation_out = run_ablations(f_path, mock_mode=True)
    assert "results" in ablation_out
    assert len(ablation_out["results"]) == 3
    assert "Baseline A: LLM-Only (No Critic)" in ablation_out["results"]
    assert "Baseline B: Symbolic-Only (Pure Rules)" in ablation_out["results"]
    assert "Proposed: Orto Full Pipeline" in ablation_out["results"]
    assert "delta_precision" in ablation_out
    assert "fp_reduction_percent" in ablation_out
