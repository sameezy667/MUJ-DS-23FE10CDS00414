"""
@file cli.py
@description Command-line interface for Orto Neurosymbolic GEC and Stylometry Engine
@module orto
"""

import argparse
import json
import sys
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from orto.pipeline import OrtoEngine
from orto.style.analyzer import StyleAnalyzer
from orto.style.naturalizer import StyleNaturalizer


def main() -> None:
    """CLI Entrypoint for Orto."""
    parser = argparse.ArgumentParser(
        description="Orto: Neurosymbolic GEC & Stylometry Engine"
    )
    parser.add_argument(
        "text",
        type=str,
        nargs="?",
        default=None,
        help="Input text to analyze (or pipe via stdin)",
    )
    parser.add_argument(
        "--style",
        action="store_true",
        help="Include research-grounded stylometric report and burstiness metrics",
    )
    parser.add_argument(
        "--naturalize",
        action="store_true",
        help="Apply cadence de-clichéing and re-rhythming",
    )
    parser.add_argument(
        "--no-critic",
        action="store_true",
        help="Disable Symbolic Critic verification",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Output raw JSON payload",
    )

    args = parser.parse_args()

    # Read from stdin if no text argument provided
    if args.text is None:
        if not sys.stdin.isatty():
            input_text = sys.stdin.read().strip()
        else:
            parser.print_help()
            sys.exit(1)
    else:
        input_text = args.text

    if not input_text:
        print("Error: Empty input text provided.")
        sys.exit(1)

    console = Console()

    # 1. Run GEC Pipeline
    engine = OrtoEngine(enable_critic=not args.no_critic)
    gec_response = engine.analyze(input_text)

    # 2. Run Optional Style Analysis
    style_result = None
    if args.style or args.naturalize:
        style_analyzer = StyleAnalyzer()
        style_result = style_analyzer.analyze(input_text)

    naturalized_text = None
    if args.naturalize:
        naturalizer = StyleNaturalizer()
        naturalized_text = naturalizer.naturalize(gec_response.corrected_text)

    # JSON output mode
    if args.json:
        payload = {
            "original_text": gec_response.original_text,
            "corrected_text": gec_response.corrected_text,
            "edits": [e.model_dump() for e in gec_response.edits],
            "telemetry": gec_response.telemetry.model_dump() if gec_response.telemetry else None,
        }
        if style_result:
            payload["stylometry"] = {
                "report": style_result.report.model_dump(),
                "suggestions": [s.model_dump() for s in style_result.suggestions],
            }
        if naturalized_text:
            payload["naturalized_text"] = naturalized_text

        print(json.dumps(payload, indent=2))
        return

    # Rich Terminal Output
    console.print("\n[bold magenta]══════════════════════════════════════════════════════[/bold magenta]")
    console.print("[bold cyan]✨ Orto Neurosymbolic GEC & Diagnostic Engine[/bold cyan]")
    console.print("[bold magenta]══════════════════════════════════════════════════════[/bold magenta]\n")

    console.print(Panel(f"[bold white]{gec_response.original_text}[/bold white]", title="Original Text", border_style="dim"))
    console.print(Panel(f"[bold green]{gec_response.corrected_text}[/bold green]", title="Corrected Text", border_style="green"))

    # Edits Table
    if gec_response.edits:
        edit_table = Table(title="Surgical Diagnostic Edits", header_style="bold blue")
        edit_table.add_column("Span", style="cyan")
        edit_table.add_column("Original", style="red strike")
        edit_table.add_column("Replacement", style="bold green")
        edit_table.add_column("Category", style="yellow")
        edit_table.add_column("Rule & Explanation", style="white")
        edit_table.add_column("Critic", justify="center")

        for e in gec_response.edits:
            critic_icon = "[green]✓ PASS[/green]" if e.critic_verified else "[yellow]UNVERIFIED[/yellow]"
            edit_table.add_row(
                f"[{e.span.start_char}:{e.span.end_char}]",
                e.span.original_text,
                e.replacement,
                e.errant_type,
                f"[bold]{e.linguistic_rule}:[/bold] {e.explanation}",
                critic_icon,
            )
        console.print(edit_table)
    else:
        console.print("[bold green]✓ No grammatical errors detected.[/bold green]\n")

    # Optional Stylometry Section
    if style_result:
        rep = style_result.report
        style_table = Table(title="📊 Stylometric Rhythm & Naturalness Report", header_style="bold magenta")
        style_table.add_column("Metric", style="bold")
        style_table.add_column("Score", justify="right", style="cyan")
        style_table.add_column("Interpretation", style="dim")

        grade_color = "green" if rep.naturalness_grade == "Natural" else "yellow" if rep.naturalness_grade == "Monotonous" else "red"

        style_table.add_row("Naturalness Grade", f"[{grade_color}]{rep.naturalness_grade}[/{grade_color}]", rep.summary)
        style_table.add_row("Burstiness Score (B)", f"{rep.burstiness_score:.2f}", "< 0.30: Monotonous | > 0.50: Natural human cadence")
        style_table.add_row("Mean Sentence Length", f"{rep.mean_sentence_length:.1f} words", f"Std Dev: {rep.std_sentence_length:.1f} words")
        style_table.add_row("AI Cliché Markers", f"{rep.cliche_count}", f"Detected: {', '.join(rep.detected_markers) if rep.detected_markers else 'None'}")
        style_table.add_row("Passive Verb Density", f"{rep.passive_ratio * 100:.1f}%", "< 25%: Standard | > 35%: Heavy passive voice")
        style_table.add_row("Nominalization Density", f"{rep.nominalization_ratio * 100:.1f}%", "Ratio of -tion/-ment/-ance nouns")
        style_table.add_row("Opening Variety Score", f"{rep.opening_variety_score:.2f}", "Syntactic POS variety of clause openings")

        console.print("\n", style_table, "\n")

        if naturalized_text and naturalized_text != gec_response.corrected_text:
            console.print(Panel(f"[bold cyan]{naturalized_text}[/bold cyan]", title="Re-Rhythmed Natural Output", border_style="cyan"))


if __name__ == "__main__":
    main()
