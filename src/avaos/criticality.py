"""
Criticality classification for AVA OS.

Implements:
- Risk-tier concept from docs/framework_design.md §6 (low/medium/high confirmation gating)
- Consequence Triage (Fix 1) and the Criticality Lock (Invariant 4)
  from docs/pbvl_remediation_plan.md

Given a piece of text (a user request, or a claim in a draft response), classify
which real-world domain(s) it touches and how severe the consequence of acting on
it wrong would be. This is a pure keyword-based first pass: cheap, explainable, and
deliberately conservative (MAX aggregation - the highest-risk signal wins).

Not a hallucination detector by itself. It answers one narrower question:
"if this were acted on and it were wrong, how much would that cost?" Everything
downstream (confirmation policy, grounding checks) reads this tier to decide how
much friction to apply.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import IntEnum


class ConsequenceTier(IntEnum):
    """Ordered so max(tiers) picks the most severe. Higher = more caution required."""

    LOW = 1
    MEDIUM = 2
    HIGH = 3
    CRITICAL = 4


class Domain(IntEnum):
    GENERAL = 0
    LEGAL = 1
    SECURITY = 2
    FINANCIAL = 3
    MEDICAL = 4
    IDENTITY = 5
    IRREVERSIBLE = 6


# Base tier for a domain match on its own, before any escalation.
_DOMAIN_BASE_TIER: dict[Domain, ConsequenceTier] = {
    Domain.GENERAL: ConsequenceTier.LOW,
    Domain.LEGAL: ConsequenceTier.MEDIUM,
    Domain.SECURITY: ConsequenceTier.MEDIUM,
    Domain.FINANCIAL: ConsequenceTier.HIGH,
    Domain.MEDICAL: ConsequenceTier.HIGH,
    Domain.IDENTITY: ConsequenceTier.CRITICAL,
    Domain.IRREVERSIBLE: ConsequenceTier.CRITICAL,
}

# Keyword -> domain. Deliberately small and readable rather than exhaustive;
# meant to be extended as real usage surfaces gaps (see docs/framework_design.md
# gap-tracker concept in §3/§8 - the same "log what we missed" idea applies here).
_DOMAIN_KEYWORDS: dict[Domain, tuple[str, ...]] = {
    Domain.MEDICAL: (
        "medication", "dose", "dosage", "prescription", "diagnosis", "symptom",
        "side effect", "drug interaction", "stop taking", "surgery", "treatment",
        "pregnant", "pregnancy", "allergic reaction", "overdose",
    ),
    Domain.FINANCIAL: (
        "wire transfer", "invest", "investment", "stock", "savings", "loan",
        "mortgage", "withdraw", "deposit", "bank account", "credit card",
        "retirement", "401k", "crypto", "cryptocurrency",
    ),
    Domain.LEGAL: (
        "contract", "lawsuit", "liability", "sue", "patent", "copyright",
        "compliance", "regulation", "legal advice",
    ),
    Domain.SECURITY: (
        "password", "encryption", "vulnerability", "breach", "hack",
        "authentication", "2fa", "private key",
    ),
    Domain.IDENTITY: (
        "social security number", "ssn", "passport number", "driver's license number",
        "government id", "date of birth and address",
    ),
}

# Explicit action verbs that turn "discussing X" into "about to do X" -
# this is what the remediation plan's Fix 1 calls the difference between a
# casual mention and a decision about to be acted on.
_ACTION_MARKERS: tuple[str, ...] = (
    "i'm going to", "i am going to", "should i", "i will", "let's",
    "i want to", "please send", "go ahead and", "do it", "confirm",
)

# Words that make an action functionally irreversible once taken.
_IRREVERSIBLE_MARKERS: tuple[str, ...] = (
    "permanently delete", "wire the money", "sign the contract",
    "stop my medication", "quit my job", "empty the trash",
    "send the payment", "close the account",
)


@dataclass(frozen=True)
class ClassificationResult:
    tier: ConsequenceTier
    domains: tuple[Domain, ...]
    matched_keywords: tuple[str, ...]
    escalated: bool = field(default=False)

    def __repr__(self) -> str:  # pragma: no cover - convenience only
        domain_names = ", ".join(d.name for d in self.domains) or "GENERAL"
        return f"ClassificationResult(tier={self.tier.name}, domains=[{domain_names}])"


def classify(text: str) -> ClassificationResult:
    """Classify a piece of text into a ConsequenceTier.

    MAX aggregation: if multiple domains match, the highest tier wins - a message
    that's both financial and medical is judged by its riskier half, not averaged.
    """
    lowered = text.lower()

    matched_domains: list[Domain] = []
    matched_keywords: list[str] = []

    for domain, keywords in _DOMAIN_KEYWORDS.items():
        for kw in keywords:
            if kw in lowered:
                matched_domains.append(domain)
                matched_keywords.append(kw)
                break  # one hit is enough to flag this domain

    irreversible_hit = next((m for m in _IRREVERSIBLE_MARKERS if m in lowered), None)
    if irreversible_hit:
        matched_domains.append(Domain.IRREVERSIBLE)
        matched_keywords.append(irreversible_hit)

    if not matched_domains:
        return ClassificationResult(
            tier=ConsequenceTier.LOW,
            domains=(Domain.GENERAL,),
            matched_keywords=(),
        )

    base_tier = max(_DOMAIN_BASE_TIER[d] for d in matched_domains)

    # Criticality Lock (Invariant 4, pbvl_remediation_plan.md): a domain-risk
    # match paired with an explicit action marker escalates by one tier, since
    # the user isn't just discussing the topic - they're about to act on it.
    has_action_marker = any(m in lowered for m in _ACTION_MARKERS)
    escalated = has_action_marker and base_tier < ConsequenceTier.CRITICAL
    final_tier = ConsequenceTier(base_tier + 1) if escalated else base_tier

    return ClassificationResult(
        tier=final_tier,
        domains=tuple(dict.fromkeys(matched_domains)),  # de-dupe, keep order
        matched_keywords=tuple(matched_keywords),
        escalated=escalated,
    )
