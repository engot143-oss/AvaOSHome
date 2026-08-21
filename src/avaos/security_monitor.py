"""
Security monitoring for AVA OS - log and alert on security events.

Monitors:
- Rate limit violations
- Failed authentication attempts
- Content filtering blocks
- Unusual patterns
- Security alerts
"""

from __future__ import annotations

import json
from pathlib import Path
from datetime import datetime, timedelta
from collections import defaultdict


class SecurityMonitor:
    """Monitor and log security events."""

    def __init__(self, memory_dir: Path):
        self.memory_dir = memory_dir
        self.security_log = memory_dir / 'security_monitor.jsonl'
        self.memory_dir.mkdir(parents=True, exist_ok=True)

    def log_event(
        self,
        event_type: str,
        severity: str,  # 'info', 'warning', 'critical'
        description: str,
        details: dict | None = None,
        source_ip: str | None = None
    ) -> None:
        """Log a security event."""
        entry = {
            'timestamp': datetime.now().isoformat(),
            'event_type': event_type,
            'severity': severity,
            'description': description,
            'details': details or {},
            'source_ip': source_ip,
        }

        with open(self.security_log, 'a') as f:
            f.write(json.dumps(entry) + '\n')

        # Alert on critical events
        if severity == 'critical':
            self._alert_critical(entry)

    def log_rate_limit_violation(
        self,
        client_ip: str,
        endpoint: str,
        limit: int
    ) -> None:
        """Log rate limit violation."""
        self.log_event(
            event_type='rate_limit_violation',
            severity='warning',
            description=f'Rate limit exceeded on {endpoint}',
            details={
                'endpoint': endpoint,
                'limit': limit,
            },
            source_ip=client_ip
        )

    def log_content_block(
        self,
        reason: str,
        content_preview: str,
        concept_id: str | None = None
    ) -> None:
        """Log content filtering block."""
        self.log_event(
            event_type='content_blocked',
            severity='warning',
            description=f'Content blocked: {reason}',
            details={
                'reason': reason,
                'content_preview': content_preview[:100],
                'concept_id': concept_id,
            }
        )

    def log_injection_attempt(
        self,
        client_ip: str,
        message: str,
        injection_type: str
    ) -> None:
        """Log suspected injection attack."""
        self.log_event(
            event_type='injection_attempt',
            severity='critical',
            description=f'Suspected {injection_type} injection attempt',
            details={
                'injection_type': injection_type,
                'message_preview': message[:100],
            },
            source_ip=client_ip
        )

    def log_failed_auth(
        self,
        client_ip: str,
        reason: str
    ) -> None:
        """Log failed authentication attempt."""
        self.log_event(
            event_type='failed_authentication',
            severity='warning',
            description=f'Failed authentication: {reason}',
            details={
                'reason': reason,
            },
            source_ip=client_ip
        )

    def log_error(
        self,
        error_type: str,
        message: str,
        stack_trace: str | None = None
    ) -> None:
        """Log application error."""
        self.log_event(
            event_type='error',
            severity='warning',
            description=f'{error_type}: {message}',
            details={
                'error_type': error_type,
                'stack_trace': stack_trace[:500] if stack_trace else None,
            }
        )

    def get_security_report(self, days: int = 7) -> dict:
        """Generate security report for parent."""
        if not self.security_log.exists():
            return {
                'period_days': days,
                'total_events': 0,
                'by_severity': {},
                'by_type': {},
                'critical_events': [],
                'recent_events': []
            }

        cutoff = datetime.now() - timedelta(days=days)
        events = []
        severity_counts = defaultdict(int)
        type_counts = defaultdict(int)
        critical_events = []

        try:
            with open(self.security_log) as f:
                for line in f:
                    if line.strip():
                        entry = json.loads(line)
                        event_time = datetime.fromisoformat(entry['timestamp'])

                        if event_time > cutoff:
                            events.append(entry)
                            severity_counts[entry['severity']] += 1
                            type_counts[entry['event_type']] += 1

                            if entry['severity'] == 'critical':
                                critical_events.append(entry)
        except (json.JSONDecodeError, FileNotFoundError):
            pass

        return {
            'period_days': days,
            'total_events': len(events),
            'by_severity': dict(severity_counts),
            'by_type': dict(type_counts),
            'critical_events': critical_events[-10:],  # Last 10 critical
            'recent_events': events[-20:],  # Last 20 events
        }

    def _alert_critical(self, event: dict) -> None:
        """Alert on critical security event."""
        alert_file = self.memory_dir / 'security_alerts.txt'

        with open(alert_file, 'a') as f:
            f.write(f"\n{'='*60}\n")
            f.write(f"CRITICAL SECURITY ALERT\n")
            f.write(f"{'='*60}\n")
            f.write(f"Time: {event['timestamp']}\n")
            f.write(f"Type: {event['event_type']}\n")
            f.write(f"Description: {event['description']}\n")
            f.write(f"Details: {json.dumps(event['details'], indent=2)}\n")
            if event.get('source_ip'):
                f.write(f"Source IP: {event['source_ip']}\n")
            f.write(f"{'='*60}\n")

    def get_top_threats(self) -> list[dict]:
        """Get top security threats by frequency."""
        if not self.security_log.exists():
            return []

        threat_counts = defaultdict(int)
        threat_details = defaultdict(list)

        try:
            with open(self.security_log) as f:
                for line in f:
                    if line.strip():
                        entry = json.loads(line)
                        if entry['severity'] in ['warning', 'critical']:
                            event_type = entry['event_type']
                            threat_counts[event_type] += 1
                            threat_details[event_type].append(entry)
        except (json.JSONDecodeError, FileNotFoundError):
            pass

        # Sort by frequency
        sorted_threats = sorted(
            threat_counts.items(),
            key=lambda x: x[1],
            reverse=True
        )

        return [
            {
                'threat_type': threat_type,
                'count': count,
                'recent': threat_details[threat_type][-3:]  # Last 3 instances
            }
            for threat_type, count in sorted_threats[:10]
        ]
