"""
Tests for learning analytics and tracking.
"""

import sys
import tempfile
import unittest
from datetime import datetime, timedelta
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from avaos.learning_analytics import (
    LearningAnalytics,
    format_learning_report,
)
from avaos.memory import Memory, ConversationTurn


class TestLearningAnalytics(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.memory_dir = Path(self.temp_dir.name) / "memory"
        self.memory_dir.mkdir(parents=True, exist_ok=True)

        self.memory = Memory(self.memory_dir)
        self.memory.load_or_create_profile("Test", 10)

        self.analytics = LearningAnalytics(self.memory_dir)

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_record_discussion(self):
        """Should record topic discussions."""
        self.analytics.record_discussion("nursing", 3)
        self.analytics.record_discussion("nursing", 2)
        self.analytics.record_discussion("finance", 4)

        engagements = self.analytics.get_topic_engagement()
        self.assertEqual(len(engagements), 2)

        nursing = next((e for e in engagements if e.topic == "nursing"), None)
        self.assertIsNotNone(nursing)
        self.assertEqual(nursing.times_discussed, 2)
        self.assertEqual(nursing.total_messages, 5)

    def test_engagement_sorting(self):
        """Topics should be sorted by engagement."""
        self.analytics.record_discussion("nursing", 5)
        self.analytics.record_discussion("finance", 2)
        self.analytics.record_discussion("nursing", 3)

        engagements = self.analytics.get_topic_engagement()
        # First should be nursing (8 messages total)
        self.assertEqual(engagements[0].topic, "nursing")
        self.assertEqual(engagements[1].topic, "finance")

    def test_mastery_levels(self):
        """Should track and retrieve mastery levels."""
        self.analytics.set_mastery("nursing", 2)
        self.analytics.set_mastery("finance", 4)

        mastery = self.analytics.get_mastery_levels()
        self.assertEqual(mastery["nursing"], 2)
        self.assertEqual(mastery["finance"], 4)

    def test_mastery_clamping(self):
        """Mastery should be clamped to 1-5."""
        self.analytics.set_mastery("nursing", 10)
        self.analytics.set_mastery("finance", 0)

        mastery = self.analytics.get_mastery_levels()
        self.assertEqual(mastery["nursing"], 5)
        self.assertEqual(mastery["finance"], 1)

    def test_knowledge_gaps(self):
        """Should identify topics not yet discussed."""
        self.analytics.record_discussion("nursing", 1)

        all_topics = ["nursing", "finance", "life_skills", "school"]
        gaps = self.analytics.get_knowledge_gaps(all_topics)

        self.assertEqual(len(gaps), 3)
        self.assertIn("finance", gaps)
        self.assertIn("life_skills", gaps)

    def test_learning_streaks(self):
        """Should track learning streaks."""
        self.analytics.record_discussion("nursing", 1)
        streaks = self.analytics.get_learning_streaks()

        self.assertEqual(streaks["nursing"], 1)

    def test_generate_report(self):
        """Should generate comprehensive learning report."""
        self.analytics.record_discussion("nursing", 5)
        self.analytics.record_discussion("finance", 2)
        self.analytics.set_mastery("nursing", 3)

        all_topics = ["nursing", "finance", "life_skills"]
        report = self.analytics.generate_report(all_topics)

        self.assertEqual(report.unique_topics, 2)
        self.assertEqual(report.most_discussed_topic, "nursing")
        self.assertIn("life_skills", report.knowledge_gaps)
        self.assertGreater(report.learning_efficiency, 0)

    def test_learning_efficiency(self):
        """Should calculate learning efficiency."""
        self.analytics.record_discussion("nursing", 1)
        self.analytics.record_discussion("finance", 1)

        all_topics = ["nursing", "finance", "life_skills", "school"]
        report = self.analytics.generate_report(all_topics)

        # 2 topics discussed out of 4
        self.assertEqual(report.learning_efficiency, 0.5)

    def test_topic_engagement_metrics(self):
        """Should calculate messages per discussion."""
        self.analytics.record_discussion("nursing", 5)
        self.analytics.record_discussion("nursing", 10)

        engagements = self.analytics.get_topic_engagement()
        nursing = engagements[0]

        self.assertEqual(nursing.times_discussed, 2)
        self.assertEqual(nursing.total_messages, 15)
        self.assertEqual(nursing.messages_per_discussion, 7.5)

    def test_recommendations(self):
        """Should provide learning recommendations."""
        self.analytics.record_discussion("nursing", 1)

        recommendations = self.analytics.get_recommendations()
        self.assertGreater(len(recommendations), 0)

    def test_analytics_persistence(self):
        """Analytics should persist to disk."""
        self.analytics.record_discussion("nursing", 3)
        self.analytics.set_mastery("nursing", 2)

        # Create new analytics instance
        analytics2 = LearningAnalytics(self.memory_dir)
        engagements = analytics2.get_topic_engagement()

        self.assertEqual(len(engagements), 1)
        self.assertEqual(engagements[0].topic, "nursing")
        self.assertEqual(engagements[0].times_discussed, 1)

    def test_export_analytics(self):
        """Should export analytics in JSON format."""
        self.analytics.record_discussion("nursing", 5)
        self.analytics.set_mastery("nursing", 3)

        export = self.analytics.export_analytics()

        self.assertIn("report", export)
        self.assertIn("topics", export)
        self.assertIn("recommendations", export)
        self.assertEqual(export["report"]["unique_topics"], 1)

    def test_format_report(self):
        """Should format report as readable text."""
        self.analytics.record_discussion("nursing", 1)

        all_topics = ["nursing", "finance", "life_skills"]
        report = self.analytics.generate_report(all_topics)
        formatted = format_learning_report(report)

        self.assertIn("Conversations", formatted)
        self.assertIn("Topics Engaged", formatted)
        self.assertIn("nursing", formatted)


if __name__ == "__main__":
    unittest.main()
