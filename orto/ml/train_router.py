"""
@file train_router.py
@description Training script for Edit Confidence Classifier & Invocation Router using scikit-learn
@module orto/ml
"""

import argparse
import os
import sys
import time
from pathlib import Path
from typing import Any, Dict, List, Tuple

# Ensure project root is in sys.path
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

import joblib
import numpy as np
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import GradientBoostingClassifier, RandomForestClassifier
from sklearn.metrics import accuracy_score, f1_score, precision_score, recall_score, roc_auc_score
from sklearn.model_selection import StratifiedKFold, cross_val_predict
from sklearn.preprocessing import StandardScaler

from benchmarks.evaluate import parse_m2_file
from orto.core.syntax_engine import SyntaxEngine
from orto.critic.verifier import SymbolicCritic
from orto.lm.ngram import NGramLanguageModel
from orto.llm.client import LLMClient, normalize_errant_type
from orto.llm.schemas import DiagnosticEdit, SpanCoordinate
from orto.ml.features import FEATURE_NAMES, FeatureExtractor


def generate_labeled_training_dataset(
    m2_path: str = "data/bea19_train_subset.m2",
    ngram_model_path: str = "data/models/ngram_bigram.json",
    cache_path: str = "data/cache/llm_cache.json",
    max_sentences: int = 500,
) -> Tuple[np.ndarray, np.ndarray]:
    """
    Constructs a realistic supervised tabular dataset from real LLM candidates generated on the training split.
    Labels are assigned based on whether each LLM candidate edit matches an annotated gold M2 edit:
    - True Positives (LLM edits that match gold corrections) labeled y = 1
    - False Positives (LLM false alarms, hallucinations, unaligned edits) labeled y = 0

    Args:
        m2_path: Path to M2 training corpus.
        ngram_model_path: Path to pre-trained N-gram model.
        cache_path: Path to persistent LLM disk cache.
        max_sentences: Maximum sentences to harvest.

    Returns:
        Tuple of feature matrix X (N x D) and label array y (N,).
    """
    records = parse_m2_file(m2_path) if os.path.exists(m2_path) else []
    if max_sentences and records:
        records = records[:max_sentences]

    ngram_model = (
        NGramLanguageModel.load(ngram_model_path)
        if os.path.exists(ngram_model_path)
        else None
    )

    feature_extractor = FeatureExtractor(ngram_model=ngram_model)
    syntax_engine = SyntaxEngine()
    critic = SymbolicCritic(syntax_engine)
    llm_client = LLMClient(cache_path=cache_path)

    X_list: List[List[float]] = []
    y_list: List[int] = []

    for rec in records:
        text = rec["input"]
        gold_edits = rec.get("edits", [])
        priors = syntax_engine.extract_priors(text)
        doc = priors.get("doc") or syntax_engine.parse(text)

        analysis = llm_client.analyze(text, priors)
        for edit in analysis.edits:
            critic_res = critic.verify_edit(text, edit)
            vec = feature_extractor.extract_vector(
                text, edit, priors, critic_result=critic_res
            )

            e_start = edit.span.start_char
            e_end = edit.span.end_char
            e_rep = edit.replacement.strip().lower()

            is_gold_match = False
            for g in gold_edits:
                g_rep = g.get("replacement", "").strip().lower()
                if g_rep == e_rep:
                    g_start_tok = g.get("start_tok", -1)
                    g_end_tok = g.get("end_tok", -1)
                    if 0 <= g_start_tok < len(doc):
                        g_char_start = doc[g_start_tok].idx
                        g_char_end = (
                            doc[min(g_end_tok - 1, len(doc) - 1)].idx
                            + len(doc[min(g_end_tok - 1, len(doc) - 1)].text)
                            if g_end_tok > g_start_tok
                            else g_char_start
                        )
                        if abs(e_start - g_char_start) <= 2 or (
                            e_start <= g_char_end and e_end >= g_char_start
                        ):
                            is_gold_match = True
                            break

            X_list.append(vec.to_list())
            y_list.append(1 if is_gold_match else 0)

    X = np.array(X_list, dtype=np.float32)
    y = np.array(y_list, dtype=np.int32)
    return X, y


def train_router_model(
    m2_path: str = "data/bea19_dev_sample.m2",
    ngram_model_path: str = "data/models/ngram_bigram.json",
    output_path: str = "data/models/edit_router.joblib",
    model_type: str = "logistic_regression",
) -> Dict[str, Any]:
    """
    Trains, validates, and serializes the Edit Confidence Classifier.

    Args:
        m2_path: Path to dataset for feature extraction.
        ngram_model_path: Path to trained N-gram model.
        output_path: Path to save serialized joblib model.
        model_type: 'logistic_regression' or 'gradient_boosting' or 'random_forest'.

    Returns:
        Dictionary of training metadata and validation scores.
    """
    console = Console()
    console.print("\n[bold cyan]=== Training Orto Edit Confidence Classifier & Router ===[/bold cyan]\n")

    t0 = time.perf_counter()
    X, y = generate_labeled_training_dataset(
        m2_path=m2_path,
        ngram_model_path=ngram_model_path,
    )
    console.print(f"[dim]Generated {len(X)} training feature vectors across {X.shape[1]} features.[/dim]")
    console.print(f"[dim]Class distribution: Positive={np.sum(y==1)} | Negative={np.sum(y==0)}[/dim]\n")

    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)

    # Select model architecture
    if model_type == "gradient_boosting":
        clf = GradientBoostingClassifier(
            n_estimators=100,
            learning_rate=0.1,
            max_depth=3,
            random_state=42,
        )
    elif model_type == "random_forest":
        clf = RandomForestClassifier(
            n_estimators=100,
            max_depth=4,
            random_state=42,
        )
    else:
        clf = LogisticRegression(
            C=1.0,
            max_iter=1000,
            class_weight="balanced",
            random_state=42,
        )

    # 5-fold cross validation
    cv = StratifiedKFold(n_splits=min(5, np.min(np.bincount(y))), shuffle=True, random_state=42)
    y_pred = cross_val_predict(clf, X_scaled, y, cv=cv)
    y_prob = cross_val_predict(clf, X_scaled, y, cv=cv, method="predict_proba")[:, 1]

    acc = accuracy_score(y, y_pred)
    prec = precision_score(y, y_pred, zero_division=0)
    rec = recall_score(y, y_pred, zero_division=0)
    f1 = f1_score(y, y_pred, zero_division=0)
    auc = roc_auc_score(y, y_prob)

    # Fit final model on full dataset
    clf.fit(X_scaled, y)
    elapsed = time.perf_counter() - t0

    # Save artifact bundle (classifier, scaler, feature names)
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    bundle = {
        "model_type": model_type,
        "classifier": clf,
        "scaler": scaler,
        "feature_names": FEATURE_NAMES,
        "training_samples": len(X),
        "validation_metrics": {
            "accuracy": float(acc),
            "precision": float(prec),
            "recall": float(rec),
            "f1": float(f1),
            "roc_auc": float(auc),
        },
    }
    joblib.dump(bundle, output_path)
    console.print(f"[green]✓ Serialized trained router model bundle to {output_path} in {elapsed:.2f}s[/green]\n")

    # Metrics Table
    metrics_table = Table(
        title="5-Fold Cross-Validation Performance Metrics",
        header_style="bold magenta",
    )
    metrics_table.add_column("Evaluation Metric", style="bold")
    metrics_table.add_column("Score (%)", justify="right", style="cyan")
    metrics_table.add_column("Assessment", style="green")

    metrics_table.add_row("Accuracy", f"{acc * 100:.2f}%", "General Classification Correctness")
    metrics_table.add_row("Precision", f"{prec * 100:.2f}%", "Rejection of False Alarms")
    metrics_table.add_row("Recall", f"{rec * 100:.2f}%", "True Positive Retention")
    metrics_table.add_row("F1 Score", f"{f1 * 100:.2f}%", "Harmonic Balance")
    metrics_table.add_row("ROC-AUC", f"{auc * 100:.2f}%", "Discriminative Separation")
    console.print(metrics_table)

    # Feature Importance / Coefficients Table
    feat_table = Table(
        title="Learned Feature Weights / Importances",
        header_style="bold blue",
    )
    feat_table.add_column("Feature Name", style="bold")
    feat_table.add_column("Learned Weight / Importance", justify="right", style="bold yellow")
    feat_table.add_column("Linguistic Role", style="dim")

    if hasattr(clf, "coef_"):
        coefs = clf.coef_[0]
        roles = {
            "critic_passed": "Strongest positive gatekeeper (+verdict)",
            "fluency_delta": "N-gram LM probability delta",
            "sva_error_flag": "Subject-Verb Agreement indicator",
            "initial_confidence": "LLM initial generation score",
            "errant_type_idx": "Error taxonomy categorical encoding",
            "has_intervening_prep": "Syntactic distractor presence",
            "sentence_len_tokens": "Sentence complexity normalizer",
            "span_start_ratio": "Positional token bias",
            "original_len": "Source span length",
            "replacement_len": "Target mutation length",
        }
        for name, weight in sorted(zip(FEATURE_NAMES, coefs), key=lambda x: abs(x[1]), reverse=True):
            feat_table.add_row(name, f"{weight:+.4f}", roles.get(name, "Structural feature"))
    elif hasattr(clf, "feature_importances_"):
        imps = clf.feature_importances_
        for name, imp in sorted(zip(FEATURE_NAMES, imps), key=lambda x: x[1], reverse=True):
            feat_table.add_row(name, f"{imp:.4f}", "Feature split importance")

    console.print("\n", feat_table, "\n")

    return bundle


def main() -> None:
    parser = argparse.ArgumentParser(description="Train Edit Confidence Classifier & Router for Orto")
    parser.add_argument(
        "--data",
        type=str,
        default="data/bea19_dev_sample.m2",
        help="Path to training M2 dataset",
    )
    parser.add_argument(
        "--ngram",
        type=str,
        default="data/models/ngram_bigram.json",
        help="Path to pre-trained N-gram model",
    )
    parser.add_argument(
        "--output",
        type=str,
        default="data/models/edit_router.joblib",
        help="Path to save serialized joblib model",
    )
    parser.add_argument(
        "--model",
        type=str,
        default="logistic_regression",
        choices=["logistic_regression", "gradient_boosting", "random_forest"],
        help="Classifier model architecture",
    )
    args = parser.parse_args()

    train_router_model(
        m2_path=args.data,
        ngram_model_path=args.ngram,
        output_path=args.output,
        model_type=args.model,
    )


if __name__ == "__main__":
    main()
