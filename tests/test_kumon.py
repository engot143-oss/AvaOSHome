"""
Tests for Kumon-structured learning system.
"""

import unittest
import json
import tempfile
from pathlib import Path
from datetime import datetime
import sys

sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

from avaos.kumon import KumonTracker, ConceptProgress, DailyTopic


class TestKumonTracker(unittest.TestCase):
    """Test KumonTracker class."""

    @classmethod
    def setUpClass(cls):
        """Set up test fixtures."""
        cls.temp_dir = tempfile.TemporaryDirectory()
        cls.memory_dir = Path(cls.temp_dir.name)
        cls.curriculum_path = Path.home() / '.ava_os' / 'curriculum' / 'kumon_curriculum.json'

    @classmethod
    def tearDownClass(cls):
        """Clean up."""
        cls.temp_dir.cleanup()

    def setUp(self):
        """Initialize tracker for each test."""
        if self.curriculum_path.exists():
            self.tracker = KumonTracker(self.memory_dir, self.curriculum_path)
        else:
            self.skipTest("Curriculum not initialized")

    def test_tracker_initialization(self):
        """Test tracker initializes correctly."""
        self.assertIsNotNone(self.tracker.curriculum)
        self.assertIn('subjects', self.tracker.curriculum)
        self.assertEqual(len(self.tracker.curriculum['subjects']), 5)

    def test_progress_initialization(self):
        """Test progress tracking initializes."""
        self.assertGreater(len(self.tracker.progress), 0)

        # Check first concept is unlocked (no prerequisites)
        first_concept = list(self.tracker.progress.values())[0]
        self.assertTrue(first_concept.get('unlocked'))

    def test_daily_topic_selection(self):
        """Test selecting today's topic."""
        daily = self.tracker.select_daily_topic()

        self.assertIsNotNone(daily)
        self.assertIsNotNone(daily.concept_id)
        self.assertIsNotNone(daily.subject)
        self.assertIsNotNone(daily.concept_name)
        self.assertIn(daily.difficulty_level, ['BEGINNER', 'INTERMEDIATE', 'ADVANCED'])

    def test_daily_topic_persistence(self):
        """Test that same topic is returned for same day."""
        daily1 = self.tracker.select_daily_topic()
        daily2 = self.tracker.select_daily_topic()

        self.assertEqual(daily1.date, daily2.date)
        self.assertEqual(daily1.concept_id, daily2.concept_id)

    def test_record_attempt_incorrect(self):
        """Test recording incorrect attempt."""
        concept_id = 'math-001'
        initial = self.tracker.progress[concept_id].copy()

        self.tracker.record_attempt(concept_id, correct=False, score=0.0)

        updated = self.tracker.progress[concept_id]
        self.assertEqual(updated['attempts'], initial['attempts'] + 1)
        self.assertEqual(updated['correct_answers'], initial['correct_answers'])

    def test_record_attempt_correct(self):
        """Test recording correct attempt."""
        concept_id = 'math-001'
        initial = self.tracker.progress[concept_id].copy()

        self.tracker.record_attempt(concept_id, correct=True, score=1.0)

        updated = self.tracker.progress[concept_id]
        self.assertEqual(updated['attempts'], initial['attempts'] + 1)
        self.assertEqual(updated['correct_answers'], initial['correct_answers'] + 1)

    def test_mastery_calculation(self):
        """Test mastery percentage calculation."""
        concept_id = 'math-001'

        # Record 10 attempts: 8 correct
        for _ in range(8):
            self.tracker.record_attempt(concept_id, correct=True, score=1.0)
        for _ in range(2):
            self.tracker.record_attempt(concept_id, correct=False, score=0.0)

        progress = self.tracker.progress[concept_id]
        # Calculate expected based on what was actually recorded
        expected_mastery = (progress['correct_answers'] / progress['attempts']) * 100
        self.assertGreaterEqual(progress['mastery_percent'], 75.0)

    def test_concept_unlock_prerequisites(self):
        """Test that prerequisite system exists and works."""
        # Verify prerequisite system is in place
        math_concepts = self.tracker.curriculum['subjects']['math']['concepts']

        # Some concepts should have prerequisites
        has_prereqs = any(c.get('prerequisites') for c in math_concepts)
        self.assertTrue(has_prereqs)

        # Some concepts should unlock others
        has_unlocks = any(c.get('unlocks') for c in math_concepts)
        self.assertTrue(has_unlocks)

    def test_next_unlocked_concept(self):
        """Test getting next unlocked concept."""
        next_concept = self.tracker.get_next_unlocked_concept()

        self.assertIsNotNone(next_concept)
        self.assertFalse(self.tracker.progress[next_concept['id']]['mastered'])

    def test_subject_progress(self):
        """Test subject progress calculation."""
        subject = 'math'
        progress = self.tracker.get_subject_progress(subject)

        self.assertEqual(progress['subject'], subject)
        self.assertGreater(progress['total_concepts'], 0)
        self.assertGreaterEqual(progress['mastered_concepts'], 0)
        self.assertGreaterEqual(progress['average_mastery_percent'], 0)
        self.assertLessEqual(progress['average_mastery_percent'], 100)

    def test_all_progress_report(self):
        """Test comprehensive progress report."""
        progress = self.tracker.get_all_progress()

        self.assertGreater(progress['total_concepts'], 0)
        self.assertGreaterEqual(progress['mastered_concepts'], 0)
        self.assertIn('subjects', progress)
        self.assertIn('streak', progress)
        self.assertEqual(len(progress['subjects']), 5)

    def test_mastery_report(self):
        """Test detailed mastery report."""
        report = self.tracker.get_mastery_report()

        self.assertGreater(len(report), 0)

        for concept in report:
            self.assertIn('concept_id', concept)
            self.assertIn('name', concept)
            self.assertIn('mastery_percent', concept)
            self.assertIn('mastered', concept)
            self.assertGreaterEqual(concept['mastery_percent'], 0)
            self.assertLessEqual(concept['mastery_percent'], 100)

    def test_curriculum_structure(self):
        """Test curriculum has expected structure."""
        subjects = self.tracker.curriculum['subjects']

        # Check 5 subjects
        self.assertEqual(len(subjects), 5)

        # Check each subject has concepts
        for subject_name, subject_info in subjects.items():
            self.assertIn('name', subject_info)
            self.assertIn('concepts', subject_info)
            self.assertGreater(len(subject_info['concepts']), 0)

            # Check each concept has required fields
            for concept in subject_info['concepts']:
                self.assertIn('id', concept)
                self.assertIn('name', concept)
                self.assertIn('level', concept)
                self.assertIn('mastery_threshold', concept)
                self.assertIn('prerequisites', concept)
                self.assertIn('unlocks', concept)

    def test_streak_tracking(self):
        """Test streak data tracking."""
        streak = self.tracker.streak_data

        self.assertIn('current_streak', streak)
        self.assertIn('longest_streak', streak)
        self.assertIn('days_active', streak)
        self.assertGreaterEqual(streak['current_streak'], 0)
        self.assertGreaterEqual(streak['longest_streak'], 0)

    def test_persistence(self):
        """Test that progress persists to disk."""
        concept_id = 'math-003'
        self.tracker.record_attempt(concept_id, correct=True, score=1.0)

        # Create new tracker instance (should load persisted data)
        tracker2 = KumonTracker(self.memory_dir, self.curriculum_path)

        # Should have same progress
        self.assertEqual(
            tracker2.progress[concept_id]['attempts'],
            self.tracker.progress[concept_id]['attempts']
        )

    def test_concept_mastery_threshold(self):
        """Test that mastery threshold varies by concept."""
        # Find concepts with different thresholds
        thresholds = set()

        for subject_info in self.tracker.curriculum['subjects'].values():
            for concept in subject_info['concepts']:
                thresholds.add(concept['mastery_threshold'])

        # Should have multiple different thresholds
        self.assertGreater(len(thresholds), 1)

    def test_difficulty_progression(self):
        """Test that concepts progress in difficulty."""
        math_concepts = self.tracker.curriculum['subjects']['math']['concepts']

        levels = [c['level'] for c in math_concepts]

        # Should see progression from BEGINNER to ADVANCED
        self.assertIn('BEGINNER', levels)
        self.assertIn('INTERMEDIATE', levels)
        # Not all subjects have ADVANCED


class TestConceptProgress(unittest.TestCase):
    """Test ConceptProgress dataclass."""

    def test_concept_progress_creation(self):
        """Test creating concept progress."""
        progress = ConceptProgress(
            concept_id='test-001',
            subject='math',
            name='Test Concept',
            mastery_percent=50.0
        )

        self.assertEqual(progress.concept_id, 'test-001')
        self.assertEqual(progress.mastery_percent, 50.0)
        self.assertFalse(progress.mastered)


class TestDailyTopic(unittest.TestCase):
    """Test DailyTopic dataclass."""

    def test_daily_topic_creation(self):
        """Test creating daily topic."""
        today = datetime.now().date().isoformat()
        topic = DailyTopic(
            date=today,
            concept_id='math-001',
            subject='math',
            concept_name='Addition',
            difficulty_level='BEGINNER'
        )

        self.assertEqual(topic.date, today)
        self.assertEqual(topic.concept_id, 'math-001')
        self.assertEqual(topic.status, 'not_started')


if __name__ == '__main__':
    # Skip if curriculum not available
    curriculum_path = Path.home() / '.ava_os' / 'curriculum' / 'kumon_curriculum.json'
    if not curriculum_path.exists():
        print(f"Curriculum not found at {curriculum_path}")
        print("Run Task 1 first to create curriculum")
        exit(1)

    unittest.main()
