"""
Enhanced safety filtering for AVA OS - child-safe content protection.

Blocks:
- Self-harm, suicide, abuse content
- Drug/alcohol references
- Inappropriate sexual content
- Violence and gore
- Illegal activities
- Phishing/scam URLs
- External URLs (unless whitelisted)
"""

from __future__ import annotations

import re
from pathlib import Path
from datetime import datetime


class EnhancedSafetyFilter:
    """Advanced content filtering for child safety."""

    # Blocked keywords by category
    SELF_HARM_KEYWORDS = {
        'suicide', 'kill myself', 'self harm', 'hurt myself', 'end my life',
        'die', 'death', 'overdose', 'poison', 'hang', 'cutting', 'bleed'
    }

    ABUSE_KEYWORDS = {
        'abuse', 'assault', 'rape', 'molest', 'hit', 'hurt', 'violence',
        'attack', 'punch', 'kick', 'beat', 'torture', 'violent', 'physical abuse'
    }

    DRUG_KEYWORDS = {
        'drugs', 'cocaine', 'heroin', 'meth', 'marijuana', 'weed', 'pot',
        'acid', 'ecstasy', 'crack', 'opioid', 'addiction', 'high', 'trip'
    }

    ALCOHOL_KEYWORDS = {
        'alcohol', 'beer', 'wine', 'vodka', 'whiskey', 'drunk', 'intoxicated',
        'drinking', 'hangover', 'binge', 'alcoholic'
    }

    SEXUAL_KEYWORDS = {
        'sex', 'porn', 'nude', 'naked', 'sexual', 'intercourse', 'masturbat',
        'orgasm', 'xxx', 'adult', 'inappropriate', 'grooming'
    }

    VIOLENCE_KEYWORDS = {
        'kill', 'murder', 'stab', 'shoot', 'gun', 'weapon', 'bomb', 'explosive',
        'gore', 'blood', 'death', 'massacre', 'terrorist', 'attack'
    }

    ILLEGAL_KEYWORDS = {
        'steal', 'robbery', 'hack', 'cheat', 'fraud', 'scam', 'illegal',
        'crime', 'criminal', 'jail', 'prison', 'illegal drug', 'counterfeit'
    }

    CURSE_WORDS = {
        'damn', 'hell', 'crap', 'piss', 'bastard', 'bitch', 'ass', 'asshole',
        'dick', 'cock', 'pussy', 'shit', 'fuck', 'motherfucker'
    }

    # Whitelisted domains (safe external links)
    WHITELISTED_DOMAINS = {
        'github.com',
        'wikipedia.org',
        'khan academy.org',
        'code.org',
        'scratch.mit.edu',
        'youtube.com',
        'youtube-nocookie.com',
        'google.com',
        'duckduckgo.com',
        'python.org',
        'docs.python.org',
        'w3schools.com',
    }

    def __init__(self, memory_dir: Path):
        self.memory_dir = memory_dir
        self.blocked_log = memory_dir / 'content_blocks.jsonl'

    def is_safe(self, text: str) -> tuple[bool, str]:
        """Check if text is safe. Returns (is_safe, reason)."""
        text_lower = text.lower()

        # Check for self-harm content
        if self._has_keywords(text_lower, self.SELF_HARM_KEYWORDS):
            return False, 'Self-harm content detected'

        # Check for abuse content
        if self._has_keywords(text_lower, self.ABUSE_KEYWORDS):
            return False, 'Abuse or violence content detected'

        # Check for drug references
        if self._has_keywords(text_lower, self.DRUG_KEYWORDS):
            return False, 'Drug-related content detected'

        # Check for alcohol references
        if self._has_keywords(text_lower, self.ALCOHOL_KEYWORDS):
            return False, 'Alcohol-related content detected'

        # Check for sexual content
        if self._has_keywords(text_lower, self.SEXUAL_KEYWORDS):
            return False, 'Inappropriate sexual content detected'

        # Check for violence
        if self._has_keywords(text_lower, self.VIOLENCE_KEYWORDS):
            return False, 'Violence or gore content detected'

        # Check for illegal activities
        if self._has_keywords(text_lower, self.ILLEGAL_KEYWORDS):
            return False, 'Illegal activity content detected'

        # Check for external URLs (except whitelisted)
        if self._has_unsafe_urls(text):
            return False, 'External link not allowed'

        # Check for phishing patterns
        if self._has_phishing_indicators(text):
            return False, 'Potential phishing or scam detected'

        # All checks passed
        return True, 'Safe'

    def _has_keywords(self, text: str, keywords: set) -> bool:
        """Check if text contains any blocked keywords."""
        for keyword in keywords:
            # Use word boundaries to avoid false positives
            pattern = r'\b' + re.escape(keyword) + r'\b'
            if re.search(pattern, text):
                return True
        return False

    def _has_unsafe_urls(self, text: str) -> bool:
        """Check for external URLs not in whitelist."""
        # Find all URLs
        url_pattern = r'https?://[^\s]+'
        urls = re.findall(url_pattern, text, re.IGNORECASE)

        for url in urls:
            # Check if domain is whitelisted
            domain_match = re.search(r'://([^/]+)', url)
            if domain_match:
                domain = domain_match.group(1).lower()
                # Remove www. prefix for comparison
                domain = domain.replace('www.', '')

                is_whitelisted = any(domain.endswith(safe) for safe in self.WHITELISTED_DOMAINS)
                if not is_whitelisted:
                    return True

        return False

    def _has_phishing_indicators(self, text: str) -> bool:
        """Check for common phishing/scam patterns."""
        phishing_patterns = [
            r'click here.*urgent',
            r'verify.*account',
            r'confirm.*password',
            r'update.*payment',
            r'act now.*limited time',
            r'claim.*prize',
            r'congratulations.*won',
            r'update.*information',
            r'suspicious activity',
        ]

        text_lower = text.lower()
        for pattern in phishing_patterns:
            if re.search(pattern, text_lower):
                return True

        return False

    def sanitize_response(self, text: str) -> str:
        """Remove or redact blocked content from response."""
        text_lower = text.lower()
        all_keywords = (
            self.SELF_HARM_KEYWORDS | self.ABUSE_KEYWORDS |
            self.DRUG_KEYWORDS | self.ALCOHOL_KEYWORDS |
            self.SEXUAL_KEYWORDS | self.VIOLENCE_KEYWORDS |
            self.ILLEGAL_KEYWORDS
        )

        for keyword in all_keywords:
            pattern = r'\b' + re.escape(keyword) + r'\b'
            text = re.sub(pattern, '[REDACTED]', text, flags=re.IGNORECASE)

        return text

    def log_blocked_content(self, text: str, reason: str, source: str = 'user') -> None:
        """Log blocked content for parent review."""
        import json
        entry = {
            'timestamp': datetime.now().isoformat(),
            'source': source,
            'reason': reason,
            'text_preview': text[:100],  # Only log preview for privacy
            'blocked': True
        }
        self.blocked_log.parent.mkdir(parents=True, exist_ok=True)
        with open(self.blocked_log, 'a') as f:
            f.write(json.dumps(entry) + '\n')

    def get_safety_report(self) -> dict:
        """Generate safety report for parent review."""
        if not self.blocked_log.exists():
            return {
                'total_blocked': 0,
                'by_reason': {},
                'recent_blocks': []
            }

        import json
        blocked_entries = []
        reason_counts = {}

        try:
            with open(self.blocked_log) as f:
                for line in f:
                    if line.strip():
                        entry = json.loads(line)
                        blocked_entries.append(entry)
                        reason = entry.get('reason', 'unknown')
                        reason_counts[reason] = reason_counts.get(reason, 0) + 1
        except (json.JSONDecodeError, FileNotFoundError):
            pass

        return {
            'total_blocked': len(blocked_entries),
            'by_reason': reason_counts,
            'recent_blocks': blocked_entries[-10:] if blocked_entries else []
        }
