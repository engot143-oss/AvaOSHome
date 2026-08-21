"""
Tests for advanced insights (sentiment, emotions, velocity).
"""

import sys
import tempfile
import unittest
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from avaos.insights import SentimentAnalyzer, InsightEngine
from avaos.memory import Memory, ConversationTurn
from avaos.learning_analytics import LearningAnalytics
from avaos.knowledge import KnowledgeBase, INITIAL_FACTS


class TestSentimentAnalyzer(unittest.TestCase):
    def test_positive_sentiment(self):
        """Should detect positive sentiment."""
        result = SentimentAnalyzer.analyze("I love learning! This is amazing!")
        self.assertEqual(result["sentiment"], "positive")
        self.assertGreater(result["score"], 0)

    def test_negative_sentiment(self):
        """Should detect negative sentiment."""
        result = SentimentAnalyzer.analyze("I hate this. I'm so frustrated.")
        self.assertEqual(result["sentiment"], "negative")
        self.assertLess(result["score"], 0)

    def test_neutral_sentiment(self):
        """Should detect neutral sentiment."""
        result = SentimentAnalyzer.analyze("What is two plus two?")
        self.assertEqual(result["sentiment"], "neutral")

    def test_stress_detection(self):
        """Should detect stress indicators."""
        result = SentimentAnalyzer.analyze("I'm so stressed and anxious about the test.")
        self.assertGreater(result["stress_level"], 0)

    def test_score_range(self):
        """Score should be between -1 and 1."""
        texts = [
            "amazing wonderful fantastic",
            "terrible awful horrible",
            "normal regular text",
        ]
        for text in texts:
            result = SentimentAnalyzer.analyze(text)
            self.assertGreaterEqual(result["score"], -1.0)
            self.assertLessEqual(result["score"], 1.0)


class TestInsightEngine(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.memory_dir = Path(self.temp_dir.name)
        self.memory_dir.mkdir(exist_ok=True)

        # Create test data
        memory = Memory(self.memory_dir)
        memory.load_or_create_profile("Test", 10)

        # Add conversations with different sentiments
        for i, (role, text, topic) in enumerate([
            ("user", "I love learning!", "nursing"),
            ("assistant", "That's great!", "nursing"),
            ("user", "This is frustrating.", "finance"),
            ("assistant", "Let me help.", "finance"),
        ]):
            turn = ConversationTurn(
                timestamp=datetime.now().isoformat(),
                role=role,
                text=text,
                topic=topic,
            )
            memory.append_turn(turn)

        # Add learning data
        analytics = LearningAnalytics(self.memory_dir)
        analytics.record_discussion("nursing", 3)
        analytics.record_discussion("finance", 2)

        # Initialize KB
        kb = KnowledgeBase(self.memory_dir / "knowledge")
        for fact in INITIAL_FACTS:
            kb.add_fact(fact)

        self.engine = InsightEngine(self.memory_dir)

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_analyze_sentiment(self):
        """Should analyze sentiment correctly."""
        result = self.engine.analyze_sentiment("I'm so happy!")
        self.assertEqual(result["sentiment"], "positive")

    def test_record_emotional_checkpoint(self):
        """Should record emotional state."""
        self.engine.record_emotional_checkpoint("positive", 0.2, "nursing")
        trend = self.engine.get_emotional_trend(1)

        self.assertEqual(trend["checkpoints"], 1)

    def test_emotional_trend(self):
        """Should calculate emotional trend."""
        self.engine.record_emotional_checkpoint("positive", 0.1, "nursing")
        self.engine.record_emotional_checkpoint("positive", 0.2, "nursing")
        self.engine.record_emotional_checkpoint("negative", 0.7, "finance")

        trend = self.engine.get_emotional_trend(1)
        self.assertEqual(trend["checkpoints"], 3)
        self.assertLess(trend["avg_stress_level"], 1.0)

    def test_learning_velocity(self):
        """Should calculate learning velocity."""
        velocity = self.engine.calculate_learning_velocity()

        self.assertIn("velocity", velocity)
        self.assertIn("trend", velocity)
        self.assertIn("discussions_per_day", velocity)

    def test_engagement_patterns(self):
        """Should identify engagement patterns."""
        patterns = self.engine.get_engagement_patterns()

        self.assertIn("primary_interest", patterns)
        self.assertIn("focus_level", patterns)

    def test_stress_indicators(self):
        """Should identify stress indicators."""
        # Record high stress
        for _ in range(5):
            self.engine.record_emotional_checkpoint("negative", 0.9, "finance")

        indicators = self.engine.identify_stress_indicators()
        self.assertGreater(len(indicators), 0)

    def test_insights_summary(self):
        """Should generate comprehensive summary."""
        summary = self.engine.get_insights_summary()

        self.assertIn("emotional_trend", summary)
        self.assertIn("learning_velocity", summary)
        self.assertIn("engagement_patterns", summary)
        self.assertIn("stress_indicators", summary)
        self.assertIn("generated_at", summary)


if __name__ == "__main__":
    unittest.main()
