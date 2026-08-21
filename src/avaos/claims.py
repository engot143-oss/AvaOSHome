"""
Claim extraction for AVA OS.

Implements docs/framework_design.md §9A step 1: decompose a draft response into
discrete, checkable factual assertions. Opinions, conversational filler, questions,
instructions, and already-hedged statements are skipped - only assertions presented
as flat fact go on to grounding/stakes checks (later pipeline stages, not this file).

This is a heuristic, keyword/pattern-based first pass, not real NLP. It will
misclassify sentences a proper parser wouldn't (see KNOWN LIMITATIONS at the
bottom). That's an accepted tradeoff for a fast, dependency-free, explainable
first stage - not a claim that this is production-grade language understanding.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from enum import Enum, auto


class ClaimKind(Enum):
    FACTUAL = auto()      # presented as flat fact - goes on to grounding checks
    HEDGED = auto()        # already carries its own uncertainty language
    OPINION = auto()        # subjective preference/feeling, not a checkable fact
    QUESTION = auto()       # asks something, doesn't assert anything
    INSTRUCTION = auto()    # imperative / tells the reader to do something


_HEDGE_MARKERS: tuple[str, ...] = (
    "might", "may be", "may not", "possibly", "perhaps", "likely", "unlikely",
    "i think", "i believe", "it's possible", "it is possible", "could be",
    "not sure", "i'm not certain", "i am not certain", "probably", "seems like",
    "appears to", "as far as i know",
)

_OPINION_MARKERS: tuple[str, ...] = (
    "i like", "i love", "i hate", "i prefer", "in my opinion", "i feel",
    "i enjoy", "my favorite", "i think it's best", "i'd say",
)

_INSTRUCTION_LEAD_VERBS: tuple[str, ...] = (
    "please", "try", "consider", "make sure", "remember to", "don't forget",
    "go", "click", "open", "run", "check", "add", "remove", "use",
)

# Sentence splitter: break on ., !, ? followed by whitespace/end, but don't split
# on common abbreviations (Dr., Mr., e.g., i.e., etc.) - a short deny-list, not a
# real tokenizer. Known to still mis-split on things like decimal numbers ("3.14").
_ABBREVIATIONS = {"dr", "mr", "mrs", "ms", "prof", "sr", "jr", "e.g", "i.e", "etc", "vs"}

_SENTENCE_SPLIT_RE = re.compile(r"(?<=[.!?])\s+(?=[A-Z\"'(]|$)")


@dataclass(frozen=True)
class Claim:
    text: str
    kind: ClaimKind

    @property
    def is_checkable(self) -> bool:
        return self.kind == ClaimKind.FACTUAL


def _split_sentences(text: str) -> list[str]:
    raw_parts = _SENTENCE_SPLIT_RE.split(text.strip())
    sentences: list[str] = []
    for part in raw_parts:
        part = part.strip()
        if not part:
            continue
        # Guard against splitting on "Dr. Smith said..." -> merge if the
        # previous sentence ended in a known abbreviation.
        if sentences:
            last_word = sentences[-1].rstrip(".").split()[-1].lower() if sentences[-1] else ""
            if last_word in _ABBREVIATIONS:
                sentences[-1] = sentences[-1] + " " + part
                continue
        sentences.append(part)
    return sentences


def _split_compound(sentence: str) -> list[str]:
    """Split a sentence joined by ' and ' into separate assertions, but only
    when both halves look like independent clauses (each has its own verb-ish
    shape - approximated here as "contains a space", to avoid splitting noun
    phrases like 'bread and butter')."""
    if " and " not in sentence:
        return [sentence]
    left, _, right = sentence.partition(" and ")
    left, right = left.strip(), right.strip()
    if len(left.split()) >= 3 and len(right.split()) >= 3:
        # crude independent-clause heuristic: both sides are long enough to
        # plausibly be their own sentence
        if not right.endswith((".", "!", "?")):
            right = right.rstrip(".") + "."
        if not left.endswith((".", "!", "?")):
            left = left.rstrip(".") + "."
        return [left, right]
    return [sentence]


def _classify_sentence(sentence: str) -> ClaimKind:
    lowered = sentence.lower().strip()

    if lowered.endswith("?"):
        return ClaimKind.QUESTION

    if any(marker in lowered for marker in _HEDGE_MARKERS):
        return ClaimKind.HEDGED

    if any(marker in lowered for marker in _OPINION_MARKERS):
        return ClaimKind.OPINION

    first_word = lowered.split()[0] if lowered.split() else ""
    if first_word in _INSTRUCTION_LEAD_VERBS:
        return ClaimKind.INSTRUCTION

    return ClaimKind.FACTUAL


def extract_claims(text: str) -> list[Claim]:
    """Decompose `text` into Claim objects. Order is preserved."""
    claims: list[Claim] = []
    for sentence in _split_sentences(text):
        for piece in _split_compound(sentence):
            piece = piece.strip()
            if not piece:
                continue
            claims.append(Claim(text=piece, kind=_classify_sentence(piece)))
    return claims


def checkable_claims(text: str) -> list[Claim]:
    """Convenience: only the FACTUAL claims, i.e. what §9A step 2 (grounding
    check) should actually run against."""
    return [c for c in extract_claims(text) if c.is_checkable]


# KNOWN LIMITATIONS (honest, not aspirational - see STATUS.md):
# - Sentence splitting breaks on numbered lists, decimals, and unusual
#   punctuation; it's a regex, not a parser.
# - Compound splitting only handles " and " and only at the top level - it
#   won't decompose "X, Y, and Z" into three claims.
# - Hedge/opinion/instruction detection is a fixed keyword list. A claim like
#   "This drug is probably safe for children" is correctly caught by "probably",
#   but "This drug carries no meaningful risk for children" is NOT hedged
#   language and would be classified FACTUAL even though it's a strong claim
#   that deserves scrutiny - that's the point: strength is not the same axis as
#   groundedness, and stakes classification (a later stage) is what's supposed
#   to catch that, not this file.
