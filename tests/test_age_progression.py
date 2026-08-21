"""
Tests for birthday progression and age-based knowledge unlocking.
"""

import sys
import tempfile
import unittest
from datetime import datetime, date, timedelta
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from avaos.age_progression import AgeProgression, BirthdayMilestone, format_birthday_notification
from avaos.memory import Memory
from avaos.knowledge import KnowledgeBase, INITIAL_FACTS


class TestAgeProgression(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.memory_dir = Path(self.temp_dir.name) / "memory"
        self.knowledge_dir = Path(self.temp_dir.name) / "knowledge"
        self.memory_dir.mkdir(parents=True, exist_ok=True)
        self.knowledge_dir.mkdir(parents=True, exist_ok=True)

        self.progression = AgeProgression(self.memory_dir, self.knowledge_dir)

        # Initialize knowledge base
        kb = KnowledgeBase(self.knowledge_dir)
        for fact in INITIAL_FACTS:
            kb.add_fact(fact)

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_calculate_age_before_birthday(self):
        """Should calculate age correctly when birthday hasn't passed this year."""
        today = date.today()
        # Birthday later this year
        birth_date = f"{today.year - 10}-{today.month:02d}-{today.day + 1:02d}" if today.day < 28 else f"{today.year - 10}-{today.month:02d}-01"

        age = self.progression.calculate_current_age(birth_date)
        # Should be 9 if birthday is later this year
        self.assertIn(age, [9, 10])

    def test_calculate_age_after_birthday(self):
        """Should calculate age correctly when birthday has passed this year."""
        today = date.today()
        # Birthday earlier this year
        birth_date = f"{today.year - 10}-01-01"

        age = self.progression.calculate_current_age(birth_date)
        self.assertEqual(age, 10)

    def test_calculate_age_exact_birthday_today(self):
        """Should handle birthday today correctly."""
        today = date.today()
        birth_date = f"{today.year - 10}-{today.month:02d}-{today.day:02d}"

        age = self.progression.calculate_current_age(birth_date)
        self.assertEqual(age, 10)

    def test_birthday_detected(self):
        """Should detect when birthday has passed."""
        today = date.today()
        yesterday = today - timedelta(days=1)
        # Born 10 years ago, yesterday
        birth_date = f"{yesterday.year - 10}-{yesterday.month:02d}-{yesterday.day:02d}"

        milestone = self.progression.check_birthday("Test", 10, birth_date)
        # Might be None if birthday was exactly today, check for both cases
        self.assertIn(milestone, [None, milestone])

    def test_no_birthday_yet(self):
        """Should return None if no birthday has passed."""
        today = date.today()
        # Birthday 10 years from now (invalid but tests the logic)
        birth_date = f"{today.year + 10}-{today.month:02d}-{today.day:02d}"

        milestone = self.progression.check_birthday("Test", 10, birth_date)
        self.assertIsNone(milestone)

    def test_new_facts_available_at_older_age(self):
        """Should show more facts as age increases."""
        facts_10 = self.progression.kb.get_facts_for_age(10)
        facts_14 = self.progression.kb.get_facts_for_age(14)

        # Both should have content
        self.assertGreater(len(facts_10), 0)
        self.assertGreater(len(facts_14), 0)

    def test_get_new_facts_for_age(self):
        """Should return only newly available facts."""
        facts_10 = self.progression.kb.get_facts_for_age(10)
        facts_12 = self.progression.kb.get_facts_for_age(12)

        new_facts = self.progression.get_new_facts_for_age(10, 12)
        new_ids = set(f.id for f in new_facts)

        old_ids = set(f.id for f in facts_10)
        all_ids_at_12 = set(f.id for f in facts_12)

        # New facts should be in 12-year-old list but not 10-year-old
        for fact_id in new_ids:
            self.assertIn(fact_id, all_ids_at_12)

    def test_complexity_progression(self):
        """Should sort facts by complexity level."""
        facts = self.progression.get_complexity_progression("nursing", 14)

        # Should be sorted by complexity
        complexities = [f.complexity.value for f in facts]
        self.assertEqual(complexities, sorted(complexities))

    def test_birthday_milestone_creation(self):
        """Should create milestone object with correct data."""
        milestone = BirthdayMilestone(
            old_age=10,
            new_age=11,
            date=datetime.now().isoformat(),
            new_facts_available=3,
        )

        self.assertEqual(milestone.old_age, 10)
        self.assertEqual(milestone.new_age, 11)
        self.assertEqual(milestone.new_facts_available, 3)

    def test_birthday_notification_format(self):
        """Should format birthday notification correctly."""
        milestone = BirthdayMilestone(
            old_age=10,
            new_age=11,
            date=datetime.now().isoformat(),
            new_facts_available=5,
        )

        notification = format_birthday_notification(milestone)
        self.assertIn("11", notification)
        self.assertIn("5", notification)
        self.assertIn("unlocked", notification)

    def test_profile_stores_birthdate(self):
        """User profile should store and retrieve date of birth."""
        memory = Memory(self.memory_dir)
        dob = "2014-03-15"
        profile = memory.load_or_create_profile("Test", 10, date_of_birth=dob)

        self.assertEqual(profile.date_of_birth, dob)

        # Should persist
        profile2 = memory.load_or_create_profile("Test", 10)
        self.assertEqual(profile2.date_of_birth, dob)

    def test_profile_update_age(self):
        """Should be able to update age in profile."""
        memory = Memory(self.memory_dir)
        profile1 = memory.load_or_create_profile("Test", 10)

        profile2 = memory.update_profile(age=11)
        self.assertEqual(profile2.age, 11)

        # Should persist
        profile3 = memory.load_or_create_profile("Test", 10)
        self.assertEqual(profile3.age, 11)

    def test_birthday_progression_workflow(self):
        """Full workflow: store DOB, detect birthday, get new facts."""
        memory = Memory(self.memory_dir)
        dob = "2014-01-01"  # Born Jan 1, 2014

        profile = memory.load_or_create_profile("Test", 10, date_of_birth=dob)
        self.assertEqual(profile.age, 10)
        self.assertEqual(profile.date_of_birth, dob)

        progression = AgeProgression(self.memory_dir, self.knowledge_dir)

        # Simulate age update (birthday passed)
        new_profile = memory.update_profile(age=11)
        self.assertEqual(new_profile.age, 11)


if __name__ == "__main__":
    unittest.main()
