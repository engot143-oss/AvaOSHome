"""
Live fallback verification for AVA OS - docs/framework_design.md §9A steps 5-6.

For a high-stakes claim with no supporting source already available (see
pipeline.py's NEEDS_FALLBACK_CHECK status), this makes a real, live call to
the Claude API with the web search tool to attempt verification against the
actual internet before the claim ships in any response.

Requires:
- `pip install anthropic` (see requirements.txt)
- ANTHROPIC_API_KEY set in the environment. Set it once in your shell/OS
  environment - never hardcode a key in this file or any other source file.

This module makes real network calls and costs real money per claim checked
(model: claude-opus-5 + the web search server tool). It is deliberately NOT
exercised by the automated test suite for that reason - see
tests/test_fallback_check.py, which mocks the API client and never touches
the network. scripts/manual_fallback_check_demo.py is the one place that
makes a real call, and it's meant to be run by hand, not by CI.
"""

from __future__ import annotations

import os
import re
from dataclasses import dataclass
from enum import Enum, auto

import anthropic

MODEL = "claude-opus-5"

_VERDICT_RE = re.compile(r"VERDICT:\s*(CONFIRMED|CONTRADICTED|EMPTY)", re.IGNORECASE)

_TOOLS = [{"type": "web_search_20260209", "name": "web_search", "max_uses": 3}]

_SYSTEM_PROMPT = (
    "You are a fact-checking step inside a larger system (AVA OS) that refuses "
    "to ship unverified high-stakes claims. You will be given one factual claim. "
    "Use web search to check it against real, current sources, then respond in "
    "exactly this format:\n\n"
    "VERDICT: CONFIRMED | CONTRADICTED | EMPTY\n"
    "EXPLANATION: <one or two sentences>\n\n"
    "CONFIRMED = credible sources support the claim as stated.\n"
    "CONTRADICTED = credible sources say the claim is false or materially "
    "misleading - state what's actually true in the explanation.\n"
    "EMPTY = you could not find credible sources either way after searching - "
    "this is a valid, honest answer, not a failure to hide.\n"
    "Do not guess. If search results are thin or ambiguous, say EMPTY."
)


class FallbackOutcome(Enum):
    CONFIRMED = auto()
    CONTRADICTED = auto()
    EMPTY = auto()


@dataclass(frozen=True)
class FallbackResult:
    outcome: FallbackOutcome
    explanation: str
    citations: tuple[str, ...]


def _build_client() -> "anthropic.Anthropic":
    if not (os.environ.get("ANTHROPIC_API_KEY") or os.environ.get("ANTHROPIC_AUTH_TOKEN")):
        raise RuntimeError(
            "No Anthropic credentials found. Set ANTHROPIC_API_KEY in your "
            "environment before using fallback_check.py - never hardcode a key "
            "in source. See STATUS.md for setup notes."
        )
    return anthropic.Anthropic()


def _extract_citations(response) -> tuple[str, ...]:
    urls: list[str] = []
    for block in response.content:
        if getattr(block, "type", None) == "web_search_tool_result":
            content = block.content
            if isinstance(content, list):  # list = success; object = error (see skill notes)
                for result in content:
                    url = getattr(result, "url", None)
                    if url:
                        urls.append(url)
    return tuple(dict.fromkeys(urls))


def parse_verdict(text: str) -> tuple[FallbackOutcome, str]:
    """Split out for testability - parsing logic doesn't need a network call."""
    match = _VERDICT_RE.search(text)
    if not match:
        return FallbackOutcome.EMPTY, text.strip() or "Model did not return a parseable verdict."
    outcome = FallbackOutcome[match.group(1).upper()]
    remainder = text[match.end():].strip()
    remainder = re.sub(r"^EXPLANATION:\s*", "", remainder, flags=re.IGNORECASE).strip()
    return outcome, remainder or "(no explanation provided)"


def run_fallback_check(claim_text: str, client: "anthropic.Anthropic | None" = None) -> FallbackResult:
    """Make a real, live call to check `claim_text` against the internet.

    Raises RuntimeError if no API credentials are configured. Raises the
    underlying anthropic API exceptions (RateLimitError, APIConnectionError,
    etc.) unmodified - callers decide their own retry policy rather than have
    this function silently swallow a failed check and report false confidence.
    """
    client = client or _build_client()
    messages = [{"role": "user", "content": f"Claim to check: {claim_text}"}]

    response = client.messages.create(
        model=MODEL, max_tokens=1024, system=_SYSTEM_PROMPT, tools=_TOOLS, messages=messages,
    )

    # Server-side search loop hit its iteration cap - resume once per the
    # skill's documented pause_turn handling (resend history, no extra prompt).
    if response.stop_reason == "pause_turn":
        messages.append({"role": "assistant", "content": response.content})
        response = client.messages.create(
            model=MODEL, max_tokens=1024, system=_SYSTEM_PROMPT, tools=_TOOLS, messages=messages,
        )

    text = "\n".join(b.text for b in response.content if getattr(b, "type", None) == "text")
    outcome, explanation = parse_verdict(text)
    citations = _extract_citations(response)
    return FallbackResult(outcome=outcome, explanation=explanation, citations=citations)
