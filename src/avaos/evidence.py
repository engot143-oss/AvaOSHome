"""
Evidence/source data model and grounding check for AVA OS.

Implements the `sources` entry from docs/framework_design.md §5's response
schema, and the grounding check from §9A step 2: does a claim trace back to
something already retrieved (memory or tool output), or not?

Grounding here is checked against a `sources` list that's passed in - this
module does NOT fetch sources itself. There's no memory store or tool layer
built yet (see STATUS.md), so for now the caller is responsible for gathering
whatever's actually been retrieved and handing it to check_grounding().
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from enum import Enum, auto


class SourceType(Enum):
    MEMORY = "memory"
    TOOL = "tool"
    DIRECT = "direct"


class ConfidenceLevel(Enum):
    GROUNDED = "grounded"
    VERIFIED = "verified"
    HEDGED_LOW_STAKES = "hedged_low_stakes"
    UNVERIFIED = "unverified"


class Outcome(Enum):
    ORIGINAL = "original"
    CONFIRMED = "confirmed"
    CONTRADICTED = "contradicted"
    EMPTY = "empty"


@dataclass(frozen=True)
class Source:
    type: SourceType
    content: str
    ref: str | None = None


@dataclass(frozen=True)
class GroundingResult:
    outcome: Outcome
    confidence: ConfidenceLevel
    matched_source: Source | None = None
    gap_logged: bool = False


_STOPWORDS = {
    "a", "an", "the", "is", "are", "was", "were", "in", "on", "at", "of", "to",
    "for", "and", "or", "with", "this", "that", "it", "its", "as", "by", "be",
}


def _keywords(text: str) -> set[str]:
    words = re.findall(r"[a-z0-9]+", text.lower())
    return {w for w in words if w not in _STOPWORDS and len(w) > 1}


def check_grounding(claim_text: str, sources: list[Source]) -> GroundingResult:
    """Heuristic overlap check: does any source share enough vocabulary with
    the claim to plausibly support or contradict it?

    This is NOT semantic understanding - it's keyword overlap, same honesty
    caveat as claims.py's pattern matching. It will call a source "supporting"
    when it merely shares topic words but doesn't actually confirm the claim,
    and it can't detect contradiction at all beyond a crude negation check.
    A real implementation needs either a real memory store with embeddings or
    an LLM-based entailment check - neither exists yet (see STATUS.md).
    """
    claim_kw = _keywords(claim_text)
    if not claim_kw:
        return GroundingResult(outcome=Outcome.EMPTY, confidence=ConfidenceLevel.UNVERIFIED, gap_logged=True)

    best_source: Source | None = None
    best_overlap = 0.0
    for source in sources:
        source_kw = _keywords(source.content)
        if not source_kw:
            continue
        overlap = len(claim_kw & source_kw) / len(claim_kw)
        if overlap > best_overlap:
            best_overlap = overlap
            best_source = source

    NEGATIONS = (" not ", " no ", " never ", "n't ")

    if best_source is None or best_overlap < 0.5:
        return GroundingResult(outcome=Outcome.EMPTY, confidence=ConfidenceLevel.UNVERIFIED, gap_logged=True)

    claim_negated = any(n in f" {claim_text.lower()} " for n in NEGATIONS)
    source_negated = any(n in f" {best_source.content.lower()} " for n in NEGATIONS)
    if claim_negated != source_negated:
        return GroundingResult(
            outcome=Outcome.CONTRADICTED,
            confidence=ConfidenceLevel.UNVERIFIED,
            matched_source=best_source,
        )

    return GroundingResult(
        outcome=Outcome.CONFIRMED,
        confidence=ConfidenceLevel.GROUNDED,
        matched_source=best_source,
    )
