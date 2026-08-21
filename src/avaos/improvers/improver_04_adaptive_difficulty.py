"""Framework #4: Adaptive Difficulty Improver"""
from .framework_improver_template import BaseFrameworkImprover
from pathlib import Path

class AdaptiveDifficultyImprover(BaseFrameworkImprover):
    def __init__(self, memory_dir: Path):
        super().__init__(4, "adaptive_difficulty", memory_dir)

    def _default_config(self):
        config = super()._default_config()
        config.update({
            'accuracy_progression_speed': 0.75,
            'regression_threshold': 0.50,
            'optimal_difficulty_hit_rate': 0.80,
        })
        return config

    def analyze_performance(self):
        metrics = self.get_recent_metrics(100)
        if not metrics:
            return {'status': 'no_data'}

        correct_progression = sum(1 for m in metrics if m.get('progressed', False))
        regressions = sum(1 for m in metrics if m.get('regressed', False))
        total = len(metrics)

        return {
            'status': 'analyzed',
            'progression_rate': correct_progression / total if total > 0 else 0,
            'regression_rate': regressions / total if total > 0 else 0,
            'total_adjustments': total,
        }

    def suggest_improvements(self):
        perf = self.analyze_performance()
        suggestions = []

        if perf.get('progression_rate', 0) < 0.70:
            suggestions.append({
                'description': 'Difficulty progression too slow - adjust thresholds',
                'priority': 'medium',
                'type': 'parameter_tuning',
            })

        if perf.get('regression_rate', 0) > 0.15:
            suggestions.append({
                'description': 'Too many regressions - tighten progression criteria',
                'priority': 'high',
                'type': 'parameter_tuning',
            })

        return suggestions
