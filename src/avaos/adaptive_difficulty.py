"""
Adaptive difficulty system for AVA OS.

Automatically adjusts question difficulty based on performance:
- Easy (< 60% accuracy) → Keep current level
- Medium (60-80% accuracy) → Maintain current level
- Hard (> 80% accuracy) → Increase difficulty
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from datetime import datetime


@dataclass
class DifficultyLevel:
    """Represents a difficulty level."""
    level: str  # 'easy', 'medium', 'hard'
    min_accuracy: float  # Minimum accuracy to achieve this level
    question_complexity: int  # 1-10 scale
    time_per_question: int  # Recommended seconds


class AdaptiveDifficulty:
    """Manage adaptive difficulty for each concept."""

    # Difficulty progression for different question types
    MATH_DIFFICULTY = {
        'easy': {
            'range': (1, 20),
            'operation': 'single_digit',
            'examples': ['2 + 3', '5 - 1', '2 x 3']
        },
        'medium': {
            'range': (20, 100),
            'operation': 'two_digit',
            'examples': ['23 + 45', '67 - 28', '7 x 8']
        },
        'hard': {
            'range': (100, 1000),
            'operation': 'multi_digit_with_carry',
            'examples': ['234 + 567', '891 - 345', '12 x 15']
        }
    }

    ENGLISH_DIFFICULTY = {
        'easy': {
            'sentence_length': 'short',
            'vocabulary': 'grade_3',
            'structure': 'simple_sentences'
        },
        'medium': {
            'sentence_length': 'medium',
            'vocabulary': 'grade_4_5',
            'structure': 'compound_sentences'
        },
        'hard': {
            'sentence_length': 'complex',
            'vocabulary': 'grade_6_7',
            'structure': 'complex_sentences'
        }
    }

    SCIENCE_DIFFICULTY = {
        'easy': {
            'concepts': 'basic_definitions',
            'depth': 'surface_level',
            'examples': 'relatable'
        },
        'medium': {
            'concepts': 'interconnected_topics',
            'depth': 'intermediate',
            'examples': 'detailed'
        },
        'hard': {
            'concepts': 'advanced_connections',
            'depth': 'deep_understanding',
            'examples': 'complex_scenarios'
        }
    }

    def __init__(self, memory_dir: Path):
        self.memory_dir = memory_dir
        self.difficulty_file = memory_dir / 'adaptive_difficulty.json'
        self.difficulty_data = self._load_or_create()

    def _load_or_create(self) -> dict:
        """Load or create difficulty tracking data."""
        if self.difficulty_file.exists():
            with open(self.difficulty_file) as f:
                return json.load(f)
        else:
            return {
                'concept_difficulty': {},
                'updated': datetime.now().isoformat()
            }

    def _save(self) -> None:
        """Save difficulty data to disk."""
        self.difficulty_data['updated'] = datetime.now().isoformat()
        self.difficulty_file.write_text(json.dumps(self.difficulty_data, indent=2))

    def initialize_concept(self, concept_id: str, subject: str) -> None:
        """Initialize difficulty tracking for a concept."""
        if concept_id not in self.difficulty_data['concept_difficulty']:
            self.difficulty_data['concept_difficulty'][concept_id] = {
                'subject': subject,
                'current_difficulty': 'easy',
                'accuracy_history': [],
                'attempts_at_level': 0,
                'last_updated': datetime.now().isoformat()
            }
            self._save()

    def record_performance(self, concept_id: str, accuracy: float) -> None:
        """Record performance and update difficulty if needed."""
        if concept_id not in self.difficulty_data['concept_difficulty']:
            return

        data = self.difficulty_data['concept_difficulty'][concept_id]
        data['accuracy_history'].append(accuracy)
        data['attempts_at_level'] += 1

        # Keep only last 10 attempts for trend analysis
        if len(data['accuracy_history']) > 10:
            data['accuracy_history'] = data['accuracy_history'][-10:]

        # Check if difficulty should change
        avg_accuracy = sum(data['accuracy_history']) / len(data['accuracy_history'])
        current_difficulty = data['current_difficulty']

        new_difficulty = self._calculate_new_difficulty(
            current_difficulty,
            avg_accuracy,
            data['attempts_at_level']
        )

        if new_difficulty != current_difficulty:
            data['current_difficulty'] = new_difficulty
            data['attempts_at_level'] = 0
            data['last_updated'] = datetime.now().isoformat()

        self._save()

    def _calculate_new_difficulty(self, current: str, avg_accuracy: float, attempts: int) -> str:
        """Calculate if difficulty should change."""
        # Need at least 3 attempts at current level before changing
        if attempts < 3:
            return current

        # Difficulty progression rules
        difficulty_progression = {
            'easy': {
                'stay': (0, 0.60),
                'advance': (0.80, 1.0),
                'next': 'medium'
            },
            'medium': {
                'regress': (0, 0.50),
                'stay': (0.50, 0.80),
                'advance': (0.85, 1.0),
                'next': 'hard',
                'prev': 'easy'
            },
            'hard': {
                'regress': (0, 0.70),
                'stay': (0.70, 1.0),
                'prev': 'medium'
            }
        }

        rules = difficulty_progression.get(current, {})

        # Check if should regress
        if 'regress' in rules:
            regress_range = rules['regress']
            if regress_range[0] <= avg_accuracy <= regress_range[1]:
                return rules.get('prev', current)

        # Check if should advance
        if 'advance' in rules:
            advance_range = rules['advance']
            if advance_range[0] <= avg_accuracy <= advance_range[1]:
                return rules.get('next', current)

        return current

    def get_current_difficulty(self, concept_id: str) -> str:
        """Get current difficulty level for a concept."""
        if concept_id in self.difficulty_data['concept_difficulty']:
            return self.difficulty_data['concept_difficulty'][concept_id]['current_difficulty']
        return 'easy'

    def get_difficulty_config(self, subject: str, difficulty: str) -> dict:
        """Get question configuration for subject and difficulty."""
        if subject == 'math':
            return self.MATH_DIFFICULTY.get(difficulty, self.MATH_DIFFICULTY['easy'])
        elif subject == 'english':
            return self.ENGLISH_DIFFICULTY.get(difficulty, self.ENGLISH_DIFFICULTY['easy'])
        elif subject == 'science':
            return self.SCIENCE_DIFFICULTY.get(difficulty, self.SCIENCE_DIFFICULTY['easy'])
        else:
            return {}

    def get_performance_summary(self, concept_id: str) -> dict:
        """Get performance summary for a concept."""
        if concept_id not in self.difficulty_data['concept_difficulty']:
            return {}

        data = self.difficulty_data['concept_difficulty'][concept_id]
        accuracy_history = data['accuracy_history']

        if not accuracy_history:
            return {
                'concept_id': concept_id,
                'current_difficulty': data['current_difficulty'],
                'avg_accuracy': 0,
                'trend': 'no_data'
            }

        avg_accuracy = sum(accuracy_history) / len(accuracy_history)

        # Determine trend
        if len(accuracy_history) >= 2:
            recent = sum(accuracy_history[-3:]) / min(3, len(accuracy_history))
            older = sum(accuracy_history[:-3]) / max(1, len(accuracy_history) - 3)
            if recent > older * 1.1:
                trend = 'improving'
            elif recent < older * 0.9:
                trend = 'declining'
            else:
                trend = 'stable'
        else:
            trend = 'insufficient_data'

        return {
            'concept_id': concept_id,
            'current_difficulty': data['current_difficulty'],
            'avg_accuracy': avg_accuracy,
            'recent_accuracy': accuracy_history[-1] if accuracy_history else 0,
            'trend': trend,
            'attempts_at_level': data['attempts_at_level']
        }

    def get_all_difficulty_levels(self) -> dict:
        """Get difficulty levels for all concepts."""
        result = {}
        for concept_id, data in self.difficulty_data['concept_difficulty'].items():
            result[concept_id] = self.get_performance_summary(concept_id)
        return result
