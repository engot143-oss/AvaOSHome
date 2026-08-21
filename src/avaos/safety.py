"""
Safety and security guardrails for AVA OS.

Implements:
- Rate limiting (prevent abuse)
- Input validation (sanitize user input)
- Prompt injection detection (prevent jailbreaks)
- Content filtering (block harmful content)
- Conversation length limits
- API key protection
"""

from __future__ import annotations

from datetime import datetime, timedelta
from dataclasses import dataclass
from pathlib import Path
import json
import re


class RateLimiter:
    """Rate limiting to prevent abuse."""

    def __init__(self, max_requests: int = 100, window_minutes: int = 60):
        self.max_requests = max_requests
        self.window_seconds = window_minutes * 60
        self.request_times: list[datetime] = []

    def is_allowed(self) -> bool:
        """Check if request is within rate limit."""
        now = datetime.now()
        cutoff = now - timedelta(seconds=self.window_seconds)

        # Remove old requests outside window
        self.request_times = [t for t in self.request_times if t > cutoff]

        if len(self.request_times) >= self.max_requests:
            return False

        self.request_times.append(now)
        return True

    def get_remaining(self) -> int:
        """Get remaining requests in current window."""
        now = datetime.now()
        cutoff = now - timedelta(seconds=self.window_seconds)
        self.request_times = [t for t in self.request_times if t > cutoff]
        return max(0, self.max_requests - len(self.request_times))


class InputValidator:
    """Validates and sanitizes user input."""

    # Patterns to detect potentially harmful input
    SQL_INJECTION = re.compile(
        r"(\bUNION\b|\bSELECT\b|\bDROP\b|\bINSERT\b|\bDELETE\b|\bUPDATE\b)",
        re.IGNORECASE,
    )

    COMMAND_INJECTION = re.compile(
        r"[;&|`$(){}[\]<>]",
        re.IGNORECASE,
    )

    PROMPT_INJECTION = re.compile(
        r"(ignore|forget|disregard|override|bypass|jailbreak|system prompt|admin|root)",
        re.IGNORECASE,
    )

    @staticmethod
    def validate_length(text: str, max_length: int = 2000) -> tuple[bool, str]:
        """Check message length."""
        if len(text) > max_length:
            return False, f"Message too long ({len(text)} > {max_length} chars)"
        if len(text) < 1:
            return False, "Message is empty"
        return True, ""

    @staticmethod
    def validate_characters(text: str) -> tuple[bool, str]:
        """Check for suspicious character sequences."""
        # Allow normal text, numbers, punctuation, newlines
        if not re.match(r"^[\w\s\-.,!?'\"\(\)\n:;]*$", text):
            return False, "Contains suspicious characters"
        return True, ""

    @staticmethod
    def detect_prompt_injection(text: str) -> tuple[bool, str]:
        """Detect potential prompt injection attempts."""
        if InputValidator.PROMPT_INJECTION.search(text):
            return True, "Potential prompt injection detected"
        return False, ""

    @staticmethod
    def detect_sql_injection(text: str) -> tuple[bool, str]:
        """Detect SQL injection patterns."""
        if InputValidator.SQL_INJECTION.search(text):
            return True, "Potential SQL injection detected"
        return False, ""

    @staticmethod
    def detect_command_injection(text: str) -> tuple[bool, str]:
        """Detect command injection patterns."""
        dangerous_chars = InputValidator.COMMAND_INJECTION.findall(text)
        if dangerous_chars:
            return True, "Contains potentially dangerous shell characters"
        return False, ""

    @staticmethod
    def validate(text: str) -> tuple[bool, str]:
        """Run all validations."""
        # Check length
        valid, msg = InputValidator.validate_length(text)
        if not valid:
            return False, msg

        # Check characters
        valid, msg = InputValidator.validate_characters(text)
        if not valid:
            return False, msg

        # Check prompt injection
        is_injected, msg = InputValidator.detect_prompt_injection(text)
        if is_injected:
            return False, msg

        # Check SQL injection
        is_injected, msg = InputValidator.detect_sql_injection(text)
        if is_injected:
            return False, msg

        return True, ""


class ContentFilter:
    """Filters harmful or inappropriate content."""

    # Topics that trigger high scrutiny
    SENSITIVE_TOPICS = {
        "self-harm", "suicide", "suicidal", "drugs", "alcohol abuse",
        "abuse", "exploitation", "illegal", "violence", "death",
    }

    # Words that might indicate harmful intent
    HARMFUL_KEYWORDS = re.compile(
        r"\b(hurt|kill|die|dead|destroy|harm|abuse|exploit|suicide|suicidal)\b",
        re.IGNORECASE,
    )

    @staticmethod
    def is_high_risk(text: str) -> tuple[bool, str]:
        """Check if text contains high-risk content."""
        for topic in ContentFilter.SENSITIVE_TOPICS:
            if topic.lower() in text.lower():
                return True, f"High-risk topic detected: {topic}"

        if ContentFilter.HARMFUL_KEYWORDS.search(text):
            return True, "Potentially harmful language detected"

        return False, ""

    @staticmethod
    def should_escalate(text: str) -> bool:
        """Determine if message should be escalated to parent."""
        is_risky, _ = ContentFilter.is_high_risk(text)
        return is_risky


class ConversationGuard:
    """Guards conversation safety and limits."""

    def __init__(self, max_turns_per_session: int = 100):
        self.max_turns = max_turns_per_session
        self.turn_count = 0

    def increment_turn(self) -> bool:
        """Increment turn count, return if within limit."""
        self.turn_count += 1
        return self.turn_count <= self.max_turns

    def get_remaining_turns(self) -> int:
        """Get remaining turns in session."""
        return max(0, self.max_turns - self.turn_count)

    def reset(self):
        """Reset turn count."""
        self.turn_count = 0


@dataclass(frozen=True)
class SecurityViolation:
    """Record of a security violation."""
    timestamp: str
    violation_type: str  # "rate_limit", "injection", "harmful_content", "length"
    message: str
    details: str


class SecurityLogger:
    """Logs security violations for audit."""

    def __init__(self, log_file: Path):
        self.log_file = Path(log_file)
        self.log_file.parent.mkdir(parents=True, exist_ok=True)

    def log_violation(self, violation: SecurityViolation):
        """Log a security violation."""
        with open(self.log_file, "a") as f:
            f.write(
                json.dumps(
                    {
                        "timestamp": violation.timestamp,
                        "type": violation.violation_type,
                        "message": violation.message,
                        "details": violation.details,
                    }
                )
                + "\n"
            )

    def get_violations(self, violation_type: str | None = None) -> list[SecurityViolation]:
        """Get logged violations."""
        if not self.log_file.exists():
            return []

        violations = []
        for line in self.log_file.read_text().strip().split("\n"):
            if not line.strip():
                continue
            data = json.loads(line)
            if violation_type and data["type"] != violation_type:
                continue
            violations.append(
                SecurityViolation(
                    timestamp=data["timestamp"],
                    violation_type=data["type"],
                    message=data["message"],
                    details=data["details"],
                )
            )
        return violations


class SafetyManager:
    """Centralized safety management."""

    def __init__(self, memory_dir: Path):
        self.rate_limiter = RateLimiter(max_requests=100, window_minutes=60)
        self.conversation_guard = ConversationGuard(max_turns_per_session=100)
        self.security_logger = SecurityLogger(memory_dir / "security_log.jsonl")

    def validate_message(self, text: str) -> tuple[bool, str]:
        """Validate incoming message."""
        # Check rate limit
        if not self.rate_limiter.is_allowed():
            remaining = self.rate_limiter.get_remaining()
            return False, f"Rate limit exceeded. Try again in a minute. ({remaining} remaining)"

        # Check conversation length
        if not self.conversation_guard.increment_turn():
            remaining = self.conversation_guard.get_remaining_turns()
            return False, f"Session limit reached ({remaining} turns remaining)"

        # Validate input
        valid, msg = InputValidator.validate(text)
        if not valid:
            violation = SecurityViolation(
                timestamp=datetime.now().isoformat(),
                violation_type="input_validation",
                message=msg,
                details=text[:100],
            )
            self.security_logger.log_violation(violation)
            return False, msg

        # Check for harmful content
        is_harmful, msg = ContentFilter.is_high_risk(text)
        if is_harmful:
            violation = SecurityViolation(
                timestamp=datetime.now().isoformat(),
                violation_type="harmful_content",
                message=msg,
                details=text[:100],
            )
            self.security_logger.log_violation(violation)
            return False, "That topic is sensitive. Please rephrase or ask an adult for help."

        return True, ""

    def should_escalate_to_parent(self, text: str) -> bool:
        """Check if message needs parent notification."""
        return ContentFilter.should_escalate(text)

    def get_safety_stats(self) -> dict:
        """Get safety statistics."""
        violations = self.security_logger.get_violations()
        by_type = {}
        for v in violations:
            by_type[v.violation_type] = by_type.get(v.violation_type, 0) + 1

        return {
            "total_violations": len(violations),
            "by_type": by_type,
            "rate_limit_remaining": self.rate_limiter.get_remaining(),
            "conversation_turns_remaining": self.conversation_guard.get_remaining_turns(),
        }
