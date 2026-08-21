"""
Hallucination-mitigation pipeline for AVA OS - docs/framework_design.md §9A,
steps 1-4 and 7. Wires together claims.py, evidence.py, and stakes.py.

Stops short of steps 5-6 (the "batched fallback check" for high-stakes
ungrounded claims) on purpose: that step needs a real verification capability
(a live search tool, an external API, or a populated knowledge store) that
doesn't exist in this codebase yet. Rather than silently guess at one, claims
that would need it are marked NEEDS_FALLBACK_CHECK and left unrendered as fact -
see STATUS.md for the open question this raises.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum, auto
from typing import Any, Callable

from .claims import Claim, checkable_claims
from .evidence import GroundingResult, Outcome, Source, check_grounding
from .stakes import Stakes, classify_stakes


class RenderedStatus(Enum):
    GROUNDED = auto()              # confirmed against an already-available source - cite it
    HEDGED_LOW_STAKES = auto()      # ungrounded, low stakes - render with uncertainty
    NEEDS_FALLBACK_CHECK = auto()    # ungrounded, high stakes - awaiting live verification
    VERIFIED_LIVE = auto()           # fallback check confirmed it against a live search
    CONTRADICTED_LIVE = auto()       # fallback check found it false - corrected, not shipped as-is
    UNVERIFIED_AFTER_LIVE_CHECK = auto()  # fallback check ran but found nothing either way


@dataclass(frozen=True)
class ClaimAssessment:
    claim: Claim
    status: RenderedStatus
    grounding: GroundingResult
    rendered_text: str


def _hedge(claim_text: str) -> str:
    """Step 4/7: render with visible, calibrated uncertainty rather than a
    flat assertion."""
    stripped = claim_text.rstrip(".")
    return f"{stripped} (my best understanding, not independently verified)."


def assess_response(draft_text: str, sources: list[Source]) -> list[ClaimAssessment]:
    """Run every checkable claim in `draft_text` through grounding + stakes
    classification. Returns one ClaimAssessment per checkable claim, in order.
    """
    assessments: list[ClaimAssessment] = []
    for claim in checkable_claims(draft_text):
        grounding = check_grounding(claim.text, sources)

        if grounding.outcome == Outcome.CONFIRMED:
            assessments.append(
                ClaimAssessment(
                    claim=claim,
                    status=RenderedStatus.GROUNDED,
                    grounding=grounding,
                    rendered_text=claim.text,
                )
            )
            continue

        stake = classify_stakes(claim.text)
        if stake == Stakes.LOW:
            assessments.append(
                ClaimAssessment(
                    claim=claim,
                    status=RenderedStatus.HEDGED_LOW_STAKES,
                    grounding=grounding,
                    rendered_text=_hedge(claim.text),
                )
            )
        else:
            assessments.append(
                ClaimAssessment(
                    claim=claim,
                    status=RenderedStatus.NEEDS_FALLBACK_CHECK,
                    grounding=grounding,
                    rendered_text=claim.text,
                )
            )

    return assessments


def resolve_fallback_checks(
    assessments: list[ClaimAssessment],
    fallback_fn: Callable[[str], Any],
) -> list[ClaimAssessment]:
    """Resolve every NEEDS_FALLBACK_CHECK assessment by calling `fallback_fn`
    once per claim - normally fallback_check.run_fallback_check (a real, live,
    costed API call), or a test double in tests.

    Duck-typed on the result (`.outcome.name`, `.explanation`) instead of
    importing fallback_check.FallbackOutcome directly, so this module has no
    hard dependency on the `anthropic` package or network access - only code
    that actually wants live verification needs to import fallback_check.
    """
    resolved: list[ClaimAssessment] = []
    for assessment in assessments:
        if assessment.status != RenderedStatus.NEEDS_FALLBACK_CHECK:
            resolved.append(assessment)
            continue

        result = fallback_fn(assessment.claim.text)
        outcome_name = result.outcome.name
        claim_text = assessment.claim.text.rstrip(".")

        if outcome_name == "CONFIRMED":
            status = RenderedStatus.VERIFIED_LIVE
            rendered = assessment.claim.text
        elif outcome_name == "CONTRADICTED":
            status = RenderedStatus.CONTRADICTED_LIVE
            rendered = f"{claim_text} — correction: {result.explanation}"
        else:  # EMPTY
            status = RenderedStatus.UNVERIFIED_AFTER_LIVE_CHECK
            rendered = f"{claim_text} (I couldn't verify this with a live search - best to check with a trusted adult)."

        resolved.append(
            ClaimAssessment(
                claim=assessment.claim,
                status=status,
                grounding=assessment.grounding,
                rendered_text=rendered,
            )
        )

    return resolved
