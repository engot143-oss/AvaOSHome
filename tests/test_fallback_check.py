"""
Tests for fallback_check.py. None of these make a real network call or need
an API key - run_fallback_check() is exercised with a fake client object that
mimics the shape of an anthropic.Anthropic response, and parse_verdict() is
tested directly. See scripts/manual_fallback_check_demo.py for a real,
costed, human-run call against the live API.
"""

import os
import sys
import types
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from avaos.fallback_check import FallbackOutcome, parse_verdict, run_fallback_check


def _text_block(text):
    return types.SimpleNamespace(type="text", text=text)


def _search_result_block(urls):
    results = [types.SimpleNamespace(url=u) for u in urls]
    return types.SimpleNamespace(type="web_search_tool_result", content=results)


def _fake_response(text, urls=(), stop_reason="end_turn"):
    content = [_search_result_block(urls)] if urls else []
    content.append(_text_block(text))
    return types.SimpleNamespace(content=content, stop_reason=stop_reason)


class FakeMessages:
    def __init__(self, responses):
        self._responses = list(responses)

    def create(self, **kwargs):
        return self._responses.pop(0)


class FakeClient:
    def __init__(self, responses):
        self.messages = FakeMessages(responses)


class TestParseVerdict(unittest.TestCase):
    def test_confirmed(self):
        outcome, explanation = parse_verdict(
            "VERDICT: CONFIRMED\nEXPLANATION: NASA confirms this launch date."
        )
        self.assertEqual(outcome, FallbackOutcome.CONFIRMED)
        self.assertIn("NASA", explanation)

    def test_contradicted(self):
        outcome, explanation = parse_verdict(
            "VERDICT: CONTRADICTED\nEXPLANATION: Actually the bridge is 900 feet, not 1200."
        )
        self.assertEqual(outcome, FallbackOutcome.CONTRADICTED)

    def test_empty_when_no_sources_found(self):
        outcome, _ = parse_verdict("VERDICT: EMPTY\nEXPLANATION: No credible sources found.")
        self.assertEqual(outcome, FallbackOutcome.EMPTY)

    def test_unparseable_text_defaults_to_empty_not_confirmed(self):
        # If the model doesn't follow the format, fail closed (EMPTY), never
        # silently treat it as CONFIRMED.
        outcome, _ = parse_verdict("Sure, that sounds about right!")
        self.assertEqual(outcome, FallbackOutcome.EMPTY)


class TestRunFallbackCheck(unittest.TestCase):
    def test_no_credentials_raises_clear_error(self):
        env_backup = {
            k: os.environ.pop(k) for k in ("ANTHROPIC_API_KEY", "ANTHROPIC_AUTH_TOKEN") if k in os.environ
        }
        try:
            with self.assertRaises(RuntimeError) as ctx:
                run_fallback_check("The sky is green.")
            self.assertIn("credentials", str(ctx.exception).lower())
        finally:
            os.environ.update(env_backup)

    def test_confirmed_result_with_citations(self):
        response = _fake_response(
            "VERDICT: CONFIRMED\nEXPLANATION: Multiple sources agree.",
            urls=["https://example.com/a", "https://example.com/b"],
        )
        client = FakeClient([response])
        result = run_fallback_check("Water boils at 100C at sea level.", client=client)
        self.assertEqual(result.outcome, FallbackOutcome.CONFIRMED)
        self.assertEqual(result.citations, ("https://example.com/a", "https://example.com/b"))

    def test_pause_turn_resumes_once(self):
        paused = _fake_response("", stop_reason="pause_turn")
        final = _fake_response("VERDICT: EMPTY\nEXPLANATION: Nothing found.")
        client = FakeClient([paused, final])
        result = run_fallback_check("Some obscure claim.", client=client)
        self.assertEqual(result.outcome, FallbackOutcome.EMPTY)


if __name__ == "__main__":
    unittest.main()
