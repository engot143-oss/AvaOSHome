import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from avaos.knowledge import (
    KnowledgeBase,
    KnowledgeFact,
    Complexity,
    LearnedTopic,
    INITIAL_FACTS,
)


class TestKnowledgeBase(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.kb = KnowledgeBase(Path(self.temp_dir.name))

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_initial_facts_load(self):
        """Verify initial facts can be added."""
        for fact in INITIAL_FACTS:
            self.kb.add_fact(fact)

        facts = self.kb.get_facts_for_age(10)
        self.assertGreater(len(facts), 0)

    def test_age_filtering(self):
        """Only facts in the age range should be returned."""
        young_fact = KnowledgeFact(
            id="test-1",
            topic="test",
            title="For young kids",
            explanation="Simple",
            min_age=5,
            max_age=8,
        )
        old_fact = KnowledgeFact(
            id="test-2",
            topic="test",
            title="For teens",
            explanation="Complex",
            min_age=14,
            max_age=18,
        )
        self.kb.add_fact(young_fact)
        self.kb.add_fact(old_fact)

        age_10 = self.kb.get_facts_for_age(10)
        self.assertEqual(len(age_10), 0)  # neither fact applies

    def test_topic_filtering(self):
        """Only facts in the requested topic should be returned."""
        for fact in INITIAL_FACTS:
            self.kb.add_fact(fact)

        nursing = self.kb.get_facts_for_age(10, topic="nursing")
        finance = self.kb.get_facts_for_age(10, topic="finance")

        self.assertGreater(len(nursing), 0)
        self.assertGreater(len(finance), 0)
        self.assertTrue(all(f.topic == "nursing" for f in nursing))

    def test_complexity_sorting(self):
        """Facts should be sorted by complexity level."""
        for fact in INITIAL_FACTS:
            self.kb.add_fact(fact)

        facts = self.kb.get_facts_for_age(14)
        complexities = [f.complexity.value for f in facts]
        self.assertEqual(complexities, sorted(complexities))

    def test_track_learned_topics(self):
        """Record and retrieve what has been learned."""
        self.kb.mark_learned("nursing", "nursing-01", 10)
        self.kb.mark_learned("finance", "finance-02", 10)

        learned = self.kb.get_learned_topics()
        self.assertEqual(len(learned), 2)
        self.assertEqual(learned[0].topic, "nursing")
        self.assertEqual(learned[1].fact_id, "finance-02")

    def test_context_building(self):
        """Knowledge base context should include age-appropriate facts."""
        for fact in INITIAL_FACTS:
            self.kb.add_fact(fact)

        context = self.kb.build_context_for_age(10, topics=["nursing", "finance"])
        self.assertIn("nursing", context.lower())
        self.assertIn("finance", context.lower())


if __name__ == "__main__":
    unittest.main()
