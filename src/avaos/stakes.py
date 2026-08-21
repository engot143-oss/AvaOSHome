"""
Stakes classification for AVA OS.

Implements docs/framework_design.md §9A step 3: for an *ungrounded* claim
(one that didn't trace back to any already-available source - see evidence.py),
decide whether it's low stakes (safe to hedge and move on) or high stakes
(needs a real verification attempt before it ships).

Calibration note: the design doc's own worked example is "Paris is the capital
of France" = low stakes, even though it contains proper names. So "contains a
name" can't be the trigger on its own, or that example would misclassify as
high stakes. The interpretation used here: specificity that matters is numbers,
dates, and causal claims (the kind of detail someone could act on and be wrong
about) - not the mere presence of a proper noun. This is a judgment call, not
something derivable purely from the doc text; documented here so it's visible
and revisable rather than silently baked in.
"""

from __future__ import annotations

import re
from enum import Enum, auto

from .criticality import ConsequenceTier, classify as classify_criticality

_NUMBER_RE = re.compile(r"\b\d[\d,.]*\b")
_CAUSAL_MARKERS: tuple[str, ...] = (
    "causes", "caused by", "leads to", "results in", "because", "due to",
    "therefore", "as a result",
)


class Stakes(Enum):
    LOW = auto()
    HIGH = auto()


def _has_specific_markers(text: str) -> bool:
    lowered = text.lower()
    if _NUMBER_RE.search(text):
        return True
    return any(marker in lowered for marker in _CAUSAL_MARKERS)


def classify_stakes(claim_text: str) -> Stakes:
    """A claim is HIGH stakes if it touches a risk-relevant domain (reuses
    criticality.py's tiering) or contains specific, actionable detail
    (numbers, dates, causal claims). Otherwise LOW."""
    criticality = classify_criticality(claim_text)
    if criticality.tier >= ConsequenceTier.MEDIUM:
        return Stakes.HIGH
    if _has_specific_markers(claim_text):
        return Stakes.HIGH
    return Stakes.LOW
