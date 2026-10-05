"""
@file run_pipeline.py
@description Quick CLI entry point for running the Orto GEC Engine
@module code
"""

import sys
from orto.pipeline import OrtoEngine


def main():
    if len(sys.argv) < 2:
        print("Usage: python code/run_pipeline.py \"<Sentence to correct>\"")
        sys.exit(1)

    text = sys.argv[1]
    engine = OrtoEngine()
    response = engine.analyze(text)

    print("\n" + "=" * 60)
    print(f"ORIGINAL  : {response.original_text}")
    print(f"CORRECTED : {response.corrected_text}")
    print(f"TIER      : {response.telemetry.engine_tier if response.telemetry else ''}")
    print(f"LATENCY   : {response.telemetry.latency_ms:.1f} ms" if response.telemetry else "")
    print("EDITS DETECTED:")
    if not response.edits:
        print("  ✅ Clean text — No grammatical errors detected.")
    else:
        for idx, edit in enumerate(response.edits, 1):
            print(f"  {idx}. [{edit.span.original_text} -> {edit.replacement}] ({edit.errant_type})")
            print(f"     Rule    : {edit.linguistic_rule}")
            print(f"     Expl    : {edit.explanation}")
            print(f"     Example : {edit.counterfactual_example}")
            print(f"     Verified: {edit.critic_verified}")
    print("=" * 60 + "\n")


if __name__ == "__main__":
    main()
