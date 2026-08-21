"""
Spaced repetition system for AVA OS.

Uses scientifically-proven spacing intervals to maximize memory retention:
- Day 1: First exposure
- Day 3: Review (3 days later)
- Day 7: Review (7 days later)
- Day 14: Review (14 days later)
- Day 30: Final review

Adapts intervals based on performance.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from datetime import datetime, timedelta
from enum import Enum


class ReviewStage(Enum):
    """Stages of spaced repetition."""
    NEW = 0
    REVIEW_3 = 3
    REVIEW_7 = 7
    REVIEW_14 = 14
    REVIEW_30 = 30
    MASTERED = 999


@dataclass
class ReviewSchedule:
    """Track when a concept should be reviewed."""
    concept_id: str
    first_learned_date: str
    current_stage: ReviewStage
    next_review_date: str
    review_count: int
    performance_score: float  # 0.0 to 1.0


class SpacedRepetition:
    """Manage spaced repetition scheduling."""

    # Standard intervals (in days)
    INTERVALS = [1, 3, 7, 14, 30]

    # Adjust intervals based on performance
    PERFORMANCE_MULTIPLIERS = {
        'poor': 0.5,      # < 60% accuracy: reduce interval
        'fair': 0.8,      # 60-75% accuracy: slightly reduce interval
        'good': 1.0,      # 75-85% accuracy: standard interval
        'excellent': 1.5  # > 85% accuracy: increase interval
    }

    def __init__(self, memory_dir: Path):
        self.memory_dir = memory_dir
        self.schedule_file = memory_dir / 'spaced_repetition.json'
        self.schedule_data = self._load_or_create()

    def _load_or_create(self) -> dict:
        """Load or create spaced repetition schedule."""
        if self.schedule_file.exists():
            with open(self.schedule_file) as f:
                return json.load(f)
        else:
            return {
                'schedules': {},
                'updated': datetime.now().isoformat()
            }

    def _save(self) -> None:
        """Save schedule to disk."""
        self.schedule_data['updated'] = datetime.now().isoformat()
        self.schedule_file.write_text(json.dumps(self.schedule_data, indent=2))

    def mark_concept_learned(self, concept_id: str) -> None:
        """Mark a concept as newly learned and start spaced repetition."""
        today = datetime.now().date().isoformat()
        next_review = (datetime.now() + timedelta(days=self.INTERVALS[0])).date().isoformat()

        self.schedule_data['schedules'][concept_id] = {
            'first_learned_date': today,
            'current_stage': 0,  # NEW stage
            'next_review_date': next_review,
            'review_count': 0,
            'performance_score': 0.0,
            'last_review_date': today,
            'all_reviews': [
                {
                    'date': today,
                    'stage': 0,
                    'accuracy': 0.0
                }
            ]
        }
        self._save()

    def record_review(self, concept_id: str, accuracy: float) -> bool:
        """Record a review attempt. Returns True if moved to next stage."""
        if concept_id not in self.schedule_data['schedules']:
            return False

        schedule = self.schedule_data['schedules'][concept_id]
        today = datetime.now().date().isoformat()

        # Only advance if review date has passed
        if today < schedule['next_review_date']:
            return False

        performance = self._get_performance_level(accuracy)
        current_stage = schedule['current_stage']

        # Record this review
        schedule['all_reviews'].append({
            'date': today,
            'stage': current_stage,
            'accuracy': accuracy
        })
        schedule['last_review_date'] = today
        schedule['performance_score'] = (schedule['performance_score'] + accuracy) / 2

        # Determine next stage
        if current_stage < len(self.INTERVALS) - 1:
            # Move to next interval
            next_stage = current_stage + 1
            interval_days = self.INTERVALS[next_stage]

            # Adjust interval based on performance
            multiplier = self.PERFORMANCE_MULTIPLIERS.get(performance, 1.0)
            adjusted_interval = int(interval_days * multiplier)

            next_review = (datetime.now() + timedelta(days=adjusted_interval)).date().isoformat()

            schedule['current_stage'] = next_stage
            schedule['next_review_date'] = next_review
            schedule['review_count'] += 1

            self._save()
            return True
        else:
            # Concept is mastered, no more reviews needed
            schedule['current_stage'] = 999  # MASTERED
            schedule['next_review_date'] = None
            schedule['review_count'] += 1
            self._save()
            return True

    def _get_performance_level(self, accuracy: float) -> str:
        """Categorize accuracy into performance level."""
        if accuracy < 0.60:
            return 'poor'
        elif accuracy < 0.75:
            return 'fair'
        elif accuracy < 0.85:
            return 'good'
        else:
            return 'excellent'

    def get_concepts_due_for_review(self) -> list[str]:
        """Get list of concepts that need review today."""
        today = datetime.now().date().isoformat()
        due = []

        for concept_id, schedule in self.schedule_data['schedules'].items():
            next_review = schedule.get('next_review_date')

            # Skip if mastered or no review scheduled
            if next_review is None or schedule['current_stage'] == 999:
                continue

            # Check if due today or overdue
            if next_review <= today:
                due.append(concept_id)

        return due

    def get_review_schedule(self, concept_id: str) -> dict:
        """Get full review schedule for a concept."""
        if concept_id not in self.schedule_data['schedules']:
            return {}

        schedule = self.schedule_data['schedules'][concept_id]

        return {
            'concept_id': concept_id,
            'first_learned': schedule['first_learned_date'],
            'current_stage': schedule['current_stage'],
            'stage_name': self._stage_name(schedule['current_stage']),
            'next_review_date': schedule['next_review_date'],
            'review_count': schedule['review_count'],
            'performance_score': schedule['performance_score'],
            'is_due': schedule['next_review_date'] and schedule['next_review_date'] <= datetime.now().date().isoformat() and schedule['current_stage'] != 999,
            'is_mastered': schedule['current_stage'] == 999
        }

    def _stage_name(self, stage: int) -> str:
        """Get human-readable stage name."""
        stage_names = {
            0: 'Newly Learned',
            3: 'First Review',
            7: 'Second Review',
            14: 'Third Review',
            30: 'Final Review',
            999: 'Mastered'
        }
        return stage_names.get(stage, 'Unknown')

    def get_all_reviews_due(self) -> list[dict]:
        """Get all reviews due today with details."""
        due = self.get_concepts_due_for_review()
        return [self.get_review_schedule(concept_id) for concept_id in due]

    def get_spaced_repetition_summary(self) -> dict:
        """Get summary of spaced repetition progress."""
        total = len(self.schedule_data['schedules'])
        mastered = sum(
            1 for s in self.schedule_data['schedules'].values()
            if s['current_stage'] == 999
        )
        due_today = len(self.get_concepts_due_for_review())

        stages = {
            0: 0,
            3: 0,
            7: 0,
            14: 0,
            30: 0,
            999: 0
        }

        for schedule in self.schedule_data['schedules'].values():
            stage = schedule['current_stage']
            if stage in stages:
                stages[stage] += 1

        return {
            'total_concepts': total,
            'mastered': mastered,
            'due_today': due_today,
            'by_stage': {
                'newly_learned': stages[0],
                'review_3_days': stages[3],
                'review_7_days': stages[7],
                'review_14_days': stages[14],
                'review_30_days': stages[30],
                'mastered': stages[999]
            }
        }
