"""
AVA OS Automation Framework - Master System Controller

The core orchestrator that:
1. Monitors all 20 frameworks
2. Collects performance metrics
3. Analyzes system health
4. Triggers improvements
5. Logs all changes
6. Ensures quality assurance

This is the "brain" that makes AVA OS continuously improve itself.
"""

from __future__ import annotations

import json
from pathlib import Path
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
from typing import List, Dict, Any


@dataclass
class FrameworkMetric:
    """Track a single framework's performance."""
    framework_id: str
    framework_name: str
    metric_name: str
    value: float
    timestamp: str
    status: str  # healthy, warning, critical
    notes: str = ""


@dataclass
class FrameworkImprovement:
    """Track an improvement made to a framework."""
    framework_id: str
    improvement_id: str
    description: str
    change_type: str  # parameter_tuning, algorithm_change, new_feature, bug_fix
    old_value: Any
    new_value: Any
    impact: str  # high, medium, low
    success: bool
    timestamp: str
    metrics_before: Dict[str, float] = None
    metrics_after: Dict[str, float] = None


class AutomationFramework:
    """Master system that orchestrates all framework improvements."""

    def __init__(self, memory_dir: Path):
        self.memory_dir = memory_dir
        self.metrics_file = memory_dir / "framework_metrics.jsonl"
        self.improvements_file = memory_dir / "framework_improvements.jsonl"
        self.analysis_file = memory_dir / "system_analysis.json"
        self.config_file = memory_dir / "automation_config.json"

        self.memory_dir.mkdir(parents=True, exist_ok=True)
        self._load_or_create_config()

    def _load_or_create_config(self) -> None:
        """Load or create automation configuration."""
        if self.config_file.exists():
            with open(self.config_file) as f:
                self.config = json.load(f)
        else:
            self.config = {
                'automation_enabled': True,
                'analysis_frequency': 'daily',  # daily, weekly, monthly
                'auto_update_enabled': True,
                'require_parent_approval': False,
                'min_confidence_for_update': 0.85,
                'max_concurrent_improvements': 3,
                'rollback_on_failure': True,
                'framework_priorities': {
                    'hallucination_prevention': 1,  # Highest priority
                    'safety_system': 2,
                    'learning_recommendations': 3,
                    'adaptive_difficulty': 4,
                    'kumon_curriculum': 5,
                    'spaced_repetition': 6,
                    'faith_curriculum': 7,
                    'financial_literacy': 8,
                    'budget_tracker': 9,
                    'memory_system': 10,
                    'security_monitoring': 11,
                    'uncertainty_communication': 12,
                    'claim_extractor': 13,
                    'fact_verification': 14,
                    'encryption': 15,
                    'pwa': 16,
                    'parent_dashboard': 17,
                    'diary_system': 18,
                    'curriculum_generator': 19,
                    'api_server': 20,
                },
                'last_analysis': None,
                'total_improvements': 0,
            }
            self._save_config()

    def _save_config(self) -> None:
        """Save configuration to disk."""
        self.config['last_updated'] = datetime.now().isoformat()
        with open(self.config_file, 'w') as f:
            json.dump(self.config, f, indent=2)

    def record_metric(
        self,
        framework_id: str,
        framework_name: str,
        metric_name: str,
        value: float,
        status: str = "healthy",
        notes: str = ""
    ) -> None:
        """Record a performance metric for a framework."""
        metric = FrameworkMetric(
            framework_id=framework_id,
            framework_name=framework_name,
            metric_name=metric_name,
            value=value,
            timestamp=datetime.now().isoformat(),
            status=status,
            notes=notes
        )

        with open(self.metrics_file, 'a') as f:
            f.write(json.dumps(asdict(metric)) + '\n')

    def record_improvement(
        self,
        framework_id: str,
        description: str,
        change_type: str,
        old_value: Any,
        new_value: Any,
        impact: str,
        success: bool,
        metrics_before: Dict[str, float] = None,
        metrics_after: Dict[str, float] = None
    ) -> None:
        """Record an improvement made to a framework."""
        improvement = FrameworkImprovement(
            framework_id=framework_id,
            improvement_id=f"{framework_id}_{int(datetime.now().timestamp())}",
            description=description,
            change_type=change_type,
            old_value=old_value,
            new_value=new_value,
            impact=impact,
            success=success,
            timestamp=datetime.now().isoformat(),
            metrics_before=metrics_before,
            metrics_after=metrics_after
        )

        with open(self.improvements_file, 'a') as f:
            f.write(json.dumps(asdict(improvement, dict_factory=lambda x: {
                k: v for k, v in x if v is not None
            })) + '\n')

        self.config['total_improvements'] += 1
        self._save_config()

    def analyze_system_health(self) -> Dict[str, Any]:
        """Analyze health of all frameworks."""
        if not self.metrics_file.exists():
            return {'status': 'no_data', 'frameworks': {}}

        metrics_by_framework = {}
        with open(self.metrics_file) as f:
            for line in f:
                metric = json.loads(line)
                fw_id = metric['framework_id']
                if fw_id not in metrics_by_framework:
                    metrics_by_framework[fw_id] = []
                metrics_by_framework[fw_id].append(metric)

        analysis = {
            'timestamp': datetime.now().isoformat(),
            'total_frameworks': len(metrics_by_framework),
            'healthy_count': 0,
            'warning_count': 0,
            'critical_count': 0,
            'frameworks': {},
            'top_priorities': [],
            'recommendations': []
        }

        # Analyze each framework's latest metrics
        for fw_id, metrics in metrics_by_framework.items():
            latest_metrics = metrics[-10:]  # Last 10 entries
            statuses = [m['status'] for m in latest_metrics]

            framework_analysis = {
                'framework_id': fw_id,
                'latest_status': statuses[-1] if statuses else 'unknown',
                'status_history': statuses,
                'health_score': self._calculate_health_score(statuses),
                'latest_metrics': latest_metrics[-1] if latest_metrics else {},
                'trend': self._analyze_trend(latest_metrics)
            }

            analysis['frameworks'][fw_id] = framework_analysis

            if framework_analysis['latest_status'] == 'healthy':
                analysis['healthy_count'] += 1
            elif framework_analysis['latest_status'] == 'warning':
                analysis['warning_count'] += 1
            elif framework_analysis['latest_status'] == 'critical':
                analysis['critical_count'] += 1

        # Identify top priorities for improvement
        priorities = sorted(
            analysis['frameworks'].items(),
            key=lambda x: (x[1]['latest_status'] == 'critical', x[1]['health_score'])
        )

        analysis['top_priorities'] = [
            p[0] for p in priorities[:5]
        ]

        # Generate recommendations
        analysis['recommendations'] = self._generate_recommendations(analysis)

        self.config['last_analysis'] = datetime.now().isoformat()
        self._save_config()

        # Save analysis report
        with open(self.analysis_file, 'w') as f:
            json.dump(analysis, f, indent=2)

        return analysis

    def _calculate_health_score(self, statuses: List[str]) -> float:
        """Calculate health score (0-1) from status history."""
        if not statuses:
            return 0.5

        score_map = {'healthy': 1.0, 'warning': 0.5, 'critical': 0.0}
        scores = [score_map.get(s, 0.5) for s in statuses]
        return sum(scores) / len(scores)

    def _analyze_trend(self, metrics: List[Dict]) -> str:
        """Analyze if framework is improving or degrading."""
        if len(metrics) < 2:
            return 'insufficient_data'

        recent = metrics[-5:] if len(metrics) >= 5 else metrics
        status_sequence = [m['status'] for m in recent]

        critical_count = status_sequence.count('critical')
        warning_count = status_sequence.count('warning')

        if critical_count > len(recent) / 2:
            return 'degrading'
        elif warning_count > len(recent) / 2:
            return 'unstable'
        else:
            return 'improving'

    def _generate_recommendations(self, analysis: Dict[str, Any]) -> List[str]:
        """Generate improvement recommendations."""
        recommendations = []

        if analysis['critical_count'] > 0:
            recommendations.append(
                f"URGENT: {analysis['critical_count']} framework(s) in critical state require immediate attention"
            )

        if analysis['warning_count'] > 2:
            recommendations.append(
                f"WARNING: {analysis['warning_count']} framework(s) showing warning status - monitor closely"
            )

        for fw_id in analysis['top_priorities'][:3]:
            trend = analysis['frameworks'][fw_id]['trend']
            if trend == 'degrading':
                recommendations.append(
                    f"DEGRADING: {fw_id} showing degrading trend - investigate root cause"
                )

        if analysis['healthy_count'] == analysis['total_frameworks']:
            recommendations.append(
                "EXCELLENT: All frameworks operating at healthy status"
            )

        return recommendations

    def should_run_analysis(self) -> bool:
        """Check if analysis should run based on frequency."""
        if not self.config['last_analysis']:
            return True

        last_analysis = datetime.fromisoformat(self.config['last_analysis'])
        frequency = self.config['analysis_frequency']

        if frequency == 'daily':
            return datetime.now() - last_analysis > timedelta(days=1)
        elif frequency == 'weekly':
            return datetime.now() - last_analysis > timedelta(days=7)
        elif frequency == 'monthly':
            return datetime.now() - last_analysis > timedelta(days=30)

        return False

    def get_framework_status_report(self) -> str:
        """Generate human-readable status report."""
        analysis = json.load(open(self.analysis_file)) if self.analysis_file.exists() else {}

        if not analysis:
            return "No analysis data available yet"

        report = f"""
AUTOMATION FRAMEWORK STATUS REPORT
==================================
Generated: {analysis.get('timestamp', 'Unknown')}

SYSTEM HEALTH:
- Total Frameworks: {analysis.get('total_frameworks', 0)}
- Healthy: {analysis.get('healthy_count', 0)}
- Warning: {analysis.get('warning_count', 0)}
- Critical: {analysis.get('critical_count', 0)}

TOP PRIORITIES FOR IMPROVEMENT:
{chr(10).join(f"  {i+1}. {fw}" for i, fw in enumerate(analysis.get('top_priorities', [])[:5]))}

RECOMMENDATIONS:
{chr(10).join(f"  • {rec}" for rec in analysis.get('recommendations', []))}

TOTAL IMPROVEMENTS MADE: {self.config.get('total_improvements', 0)}

Automation Status: {'ENABLED' if self.config.get('automation_enabled') else 'DISABLED'}
Auto-Update: {'ON' if self.config.get('auto_update_enabled') else 'OFF'}
Parent Approval Required: {'YES' if self.config.get('require_parent_approval') else 'NO'}
"""
        return report

    def get_improvement_history(self, framework_id: str = None, limit: int = 10) -> List[Dict]:
        """Get improvement history for a framework."""
        if not self.improvements_file.exists():
            return []

        improvements = []
        with open(self.improvements_file) as f:
            for line in f:
                imp = json.loads(line)
                if framework_id is None or imp['framework_id'] == framework_id:
                    improvements.append(imp)

        return sorted(
            improvements,
            key=lambda x: x['timestamp'],
            reverse=True
        )[:limit]


# Example usage for testing
if __name__ == '__main__':
    import tempfile
    with tempfile.TemporaryDirectory() as tmpdir:
        memory_dir = Path(tmpdir)
        automation = AutomationFramework(memory_dir)

        # Record some test metrics
        automation.record_metric(
            'hallucination_prevention',
            'Hallucination Prevention',
            'false_positive_rate',
            0.05,
            'healthy',
            'Excellent performance'
        )

        automation.record_metric(
            'safety_system',
            'Enhanced Safety',
            'blocked_content_rate',
            0.02,
            'healthy',
            'Normal operation'
        )

        # Analyze system
        analysis = automation.analyze_system_health()
        print(automation.get_framework_status_report())
