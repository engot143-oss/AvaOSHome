"""
Manual, human-run demo of a real live fallback check against the Claude API.

This is NOT part of the automated test suite on purpose - it costs real
money (one claude-opus-5 call with web search) and needs a real API key.
Run it yourself, by hand, when you want to see the whole pipeline work
end to end against the live internet:

    set ANTHROPIC_API_KEY=sk-ant-...          (PowerShell: $env:ANTHROPIC_API_KEY="sk-ant-...")
    python scripts/manual_fallback_check_demo.py
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from avaos.fallback_check import run_fallback_check
from avaos.pipeline import assess_response, resolve_fallback_checks

DEMO_TEXT = (
    "The Eiffel Tower is in Paris. "
    "Aspirin was first synthesized by Bayer in 1897. "
    "This new supplement cures anxiety completely with no side effects."
)

if __name__ == "__main__":
    print("Running claims through the pipeline (no network calls yet)...\n")
    assessments = assess_response(DEMO_TEXT, sources=[])
    for a in assessments:
        print(f"[{a.status.name}] {a.claim.text}")

    needs_check = [a for a in assessments if a.status.name == "NEEDS_FALLBACK_CHECK"]
    if not needs_check:
        print("\nNothing needed a live check.")
        sys.exit(0)

    print(f"\n{len(needs_check)} claim(s) need a live check - calling the real API now...\n")
    resolved = resolve_fallback_checks(assessments, fallback_fn=run_fallback_check)
    for a in resolved:
        print(f"[{a.status.name}] {a.rendered_text}")
