"""
Smart learning recommendations for AVA OS.

Recommends what to study next based on:
- Mastery level (prioritize low performers)
- Spaced repetition schedule (due reviews)
- Subject balance (prevent over-focus)
- Learning velocity (pace of progress)
- Prerequisite chains (logical progression)
"""

from __future__ import annotations

import json
from pathlib import Path
from datetime import datetime
from enum import Enum


class RecommendationType(Enum):
    """Types of learning recommendations."""
    CONCEPT_DUE = 'spaced_repetition_due'
    PREREQUISITE = 'prerequisite_not_mastered'
    LOW_MASTERY = 'improve_weak_area'
    SUBJECT_BALANCE = 'balance_subjects'
    OPTIMAL_NEXT = 'optimal_progression'
    MAINTENANCE = 'maintenance_review'


class LearningRecommendations:
    """Generate personalized learning recommendations."""

    def __init__(self, memory_dir: Path, curriculum_path: Path):
        self.memory_dir = memory_dir
        self.curriculum_path = curriculum_path
        self.recommendation_file = memory_dir / 'learning_recommendations.json'
        self.curriculum = self._load_curriculum()
        self.recommendations = self._load_or_create()

    def _load_curriculum(self) -> dict:
        """Load curriculum."""
        with open(self.curriculum_path) as f:
            return json.load(f)

    def _load_or_create(self) -> dict:
        """Load or create recommendations file."""
        if self.recommendation_file.exists():
            with open(self.recommendation_file) as f:
                return json.load(f)
        else:
            return {
                'generated_at': datetime.now().isoformat(),
                'recommendations': []
            }

    def _save(self) -> None:
        """Save recommendations to disk."""
        self.recommendations['generated_at'] = datetime.now().isoformat()
        self.recommendation_file.write_text(json.dumps(self.recommendations, indent=2))

    def generate_recommendations(
        self,
        kumon_tracker: any,
        spaced_repetition: any,
        adaptive_difficulty: any
    ) -> list[dict]:
        """Generate list of recommended concepts to study next."""
        recommendations = []

        # 1. Recommend spaced repetition reviews (highest priority)
        due_reviews = spaced_repetition.get_all_reviews_due()
        for review in due_reviews:
            recommendations.append({
                'type': RecommendationType.CONCEPT_DUE.value,
                'priority': 'critical',
                'concept_id': review['concept_id'],
                'reason': f"Review due (stage: {review['stage_name']})",
                'urgency': 'overdue' if review['next_review_date'] else 'due_today',
                'score': 10
            })

        # 2. Recommend prerequisite fixes
        all_progress = kumon_tracker.get_all_progress()
        for subject, subject_info in self.curriculum['subjects'].items():
            for concept in subject_info['concepts']:
                concept_id = concept['id']
                progress = kumon_tracker.progress.get(concept_id, {})

                if not progress.get('mastered'):
                    # Check if prerequisites met
                    for prereq in concept.get('prerequisites', []):
                        prereq_progress = kumon_tracker.progress.get(prereq, {})
                        if not prereq_progress.get('mastered'):
                            recommendations.append({
                                'type': RecommendationType.PREREQUISITE.value,
                                'priority': 'high',
                                'concept_id': prereq,
                                'reason': f"Required for {concept['name']}",
                                'locked_concept': concept['name'],
                                'score': 9
                            })
                            break

        # 3. Recommend improving weak areas (< 70% mastery)
        mastery_report = kumon_tracker.get_mastery_report()
        weak_concepts = [c for c in mastery_report if 0 < c['mastery_percent'] < 70 and not c['mastered']]

        for concept in sorted(weak_concepts, key=lambda x: x['mastery_percent'])[:3]:
            recommendations.append({
                'type': RecommendationType.LOW_MASTERY.value,
                'priority': 'high',
                'concept_id': concept['concept_id'],
                'reason': f"Improve mastery: currently {concept['mastery_percent']:.0f}%",
                'current_mastery': concept['mastery_percent'],
                'score': 8
            })

        # 4. Recommend next unlocked concept if no urgent reviews
        if not due_reviews:
            next_concept = kumon_tracker.get_next_unlocked_concept()
            if next_concept and not kumon_tracker.progress[next_concept['id']].get('mastered'):
                recommendations.append({
                    'type': RecommendationType.OPTIMAL_NEXT.value,
                    'priority': 'medium',
                    'concept_id': next_concept['id'],
                    'reason': f"Ready to learn: {next_concept['name']}",
                    'score': 7
                })

        # 5. Recommend subject balance
        subject_engagement = self._get_subject_engagement(kumon_tracker)
        least_engaged = min(subject_engagement, key=subject_engagement.get)

        if subject_engagement[least_engaged] < 0.3:  # < 30% engaged
            concepts = self.curriculum['subjects'][least_engaged]['concepts']
            for concept in concepts:
                if not kumon_tracker.progress[concept['id']].get('mastered'):
                    recommendations.append({
                        'type': RecommendationType.SUBJECT_BALANCE.value,
                        'priority': 'low',
                        'concept_id': concept['id'],
                        'reason': f"Balance {least_engaged} practice",
                        'subject': least_engaged,
                        'score': 5
                    })
                    break

        # 6. Recommend faith/character topics (important for holistic development)
        if 'faith' in self.curriculum.get('subjects', {}):
            faith_concepts = self.curriculum['subjects']['faith']['concepts']
            # Recommend faith topics at medium priority for character development
            for concept in faith_concepts[:2]:  # Top 2 faith concepts
                if not kumon_tracker.progress.get(concept['id'], {}).get('mastered'):
                    recommendations.append({
                        'type': 'faith_development',
                        'priority': 'medium',
                        'concept_id': concept['id'],
                        'reason': f"Character development: {concept['name']}",
                        'subject': 'faith',
                        'score': 6,
                        'importance': 'Research shows faith and values support resilience and decision-making'
                    })

        # Sort by priority and score
        priority_order = {'critical': 0, 'high': 1, 'medium': 2, 'low': 3}
        recommendations.sort(
            key=lambda x: (priority_order.get(x['priority'], 999), -x['score'])
        )

        self.recommendations['recommendations'] = recommendations[:5]  # Top 5
        self._save()

        return recommendations[:5]

    def _get_subject_engagement(self, kumon_tracker: any) -> dict:
        """Get engagement level (0-1) for each subject."""
        engagement = {}
        total_concepts = sum(
            len(info['concepts'])
            for info in self.curriculum['subjects'].values()
        )

        for subject, info in self.curriculum['subjects'].items():
            subject_concepts = len(info['concepts'])
            mastered = sum(
                1 for concept in info['concepts']
                if kumon_tracker.progress.get(concept['id'], {}).get('mastered')
            )
            engagement[subject] = mastered / subject_concepts if subject_concepts > 0 else 0

        return engagement

    def get_top_recommendation(self) -> dict | None:
        """Get the single top recommendation."""
        if self.recommendations['recommendations']:
            return self.recommendations['recommendations'][0]
        return None

    def get_all_recommendations(self) -> list[dict]:
        """Get all current recommendations."""
        return self.recommendations.get('recommendations', [])

    def explain_recommendation(self, recommendation: dict) -> str:
        """Get human-readable explanation of a recommendation."""
        rec_type = recommendation['type']
        concept_name = recommendation.get('concept_id', 'Unknown')
        reason = recommendation.get('reason', 'General recommendation')

        explanations = {
            RecommendationType.CONCEPT_DUE.value: f"Time to review {concept_name}! ({reason})",
            RecommendationType.PREREQUISITE.value: f"Master {concept_name} first - it unlocks {recommendation.get('locked_concept', 'other concepts')}",
            RecommendationType.LOW_MASTERY.value: f"Let's strengthen {concept_name} ({reason})",
            RecommendationType.SUBJECT_BALANCE.value: f"Diversify learning with {concept_name} ({reason})",
            RecommendationType.OPTIMAL_NEXT.value: f"Ready for the next challenge: {concept_name}",
            RecommendationType.MAINTENANCE.value: f"Keep sharp with {concept_name}"
        }

        return explanations.get(rec_type, reason)

    def get_weekly_learning_plan(self, kumon_tracker: any, spaced_repetition: any) -> dict:
        """Generate a weekly learning plan."""
        due_reviews = spaced_repetition.get_all_reviews_due()
        recommendations = self.get_all_recommendations()

        plan = {
            'week_start': datetime.now().date().isoformat(),
            'reviews_due': len(due_reviews),
            'new_concepts_available': 0,
            'focus_area': None,
            'estimated_time_min': 0,
            'daily_breakdown': []
        }

        # Count new unlocked concepts
        for concept_id, progress in kumon_tracker.progress.items():
            if progress['unlocked'] and not progress['mastered'] and concept_id not in [r['concept_id'] for r in due_reviews]:
                plan['new_concepts_available'] += 1

        # Focus area from recommendations
        if recommendations:
            plan['focus_area'] = recommendations[0]['reason']

        # Estimate time (20 min per day default, more if reviews due)
        plan['estimated_time_min'] = (len(due_reviews) * 15) + (7 * 20)

        # Daily breakdown
        for day in range(7):
            day_plan = {
                'day': day,
                'recommended_reviews': 1 if due_reviews else 0,
                'recommended_concept': recommendations[day % len(recommendations)]['concept_id'] if recommendations else None,
                'time_estimate_min': 25
            }
            plan['daily_breakdown'].append(day_plan)

        return plan
