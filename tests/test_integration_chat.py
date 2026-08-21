"""
End-to-end integration test for the chat system.

Tests the full flow:
1. Load knowledge base
2. Initialize memory
3. Run message through pipeline
4. Verify hallucination checking
5. Verify notifications are logged
"""

import sys
import tempfile
import unittest
from datetime import datetime
from pathlib import Path
from unittest.mock import patch, MagicMock

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from avaos.chat import run_chat, NotificationHandler
from avaos.knowledge import KnowledgeBase, INITIAL_FACTS
from avaos.memory import Memory, ConversationTurn
from avaos.pipeline import assess_response
from avaos.criticality import classify as classify_criticality


class TestIntegrationChat(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.memory_dir = Path(self.temp_dir.name) / "memory"
        self.knowledge_dir = Path(self.temp_dir.name) / "knowledge"
        self.memory_dir.mkdir(parents=True, exist_ok=True)
        self.knowledge_dir.mkdir(parents=True, exist_ok=True)

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_knowledge_base_loads_on_startup(self):
        """Knowledge base initializes with core facts."""
        kb = KnowledgeBase(self.knowledge_dir)
        for fact in INITIAL_FACTS:
            kb.add_fact(fact)

        facts_10 = kb.get_facts_for_age(10)
        self.assertGreater(len(facts_10), 0)

        # Should include nursing, finance, and life skills
        topics = {f.topic for f in facts_10}
        self.assertIn("nursing", topics)
        self.assertIn("finance", topics)
        self.assertIn("life_skills", topics)

    def test_memory_saves_conversation_turns(self):
        """Conversation history is properly saved and loaded."""
        memory = Memory(self.memory_dir)
        memory.load_or_create_profile("TestDaughter", 10)

        # Add a turn
        turn = ConversationTurn(
            timestamp=datetime.now().isoformat(),
            role="user",
            text="How do nurses help people?",
            topic="nursing",
        )
        memory.append_turn(turn)

        # Verify it was saved
        history_file = self.memory_dir / "conversation_history.jsonl"
        self.assertTrue(history_file.exists())
        lines = history_file.read_text().strip().split("\n")
        self.assertEqual(len(lines), 1)

    def test_notification_handler_logs_high_stakes(self):
        """High-stakes advice triggers notifications."""
        notifications = NotificationHandler(self.memory_dir / "notifications.log")

        # Log a medical notification
        notifications.notify("MEDICAL", "Advised on symptoms")
        notifications.notify("FINANCIAL", "Discussed investment strategy")

        # Verify notifications were logged
        log_file = self.memory_dir / "notifications.log"
        self.assertTrue(log_file.exists())
        lines = log_file.read_text().strip().split("\n")
        self.assertEqual(len(lines), 2)
        self.assertIn("MEDICAL", lines[0])
        self.assertIn("FINANCIAL", lines[1])

    def test_hallucination_pipeline_on_response(self):
        """Response goes through hallucination pipeline."""
        ava_response = (
            "Nurses help people who are sick or hurt. "
            "There are many types of nurses: emergency room nurses, "
            "pediatric nurses, and surgical nurses."
        )

        assessments = assess_response(ava_response, sources=[])

        # Should extract multiple claims
        self.assertGreater(len(assessments), 0)

        # Each assessment should have rendered text
        for assessment in assessments:
            self.assertIsNotNone(assessment.rendered_text)

    def test_criticality_classification(self):
        """Queries are classified by consequence tier."""
        # Medical query with action marker
        medical_query = "I think I have a medication side effect"
        tier = classify_criticality(medical_query)
        self.assertGreaterEqual(tier.tier.value, 3)  # HIGH or higher (action marker escalates)

        # Finance query with action marker
        finance_query = "How should I invest $1000?"
        tier = classify_criticality(finance_query)
        self.assertGreaterEqual(tier.tier.value, 3)  # CRITICAL (financial + action marker)

        # Casual query without risk domains
        casual_query = "What's your favorite color?"
        tier = classify_criticality(casual_query)
        self.assertEqual(tier.tier.value, 1)  # LOW tier

    def test_knowledge_context_for_age(self):
        """Knowledge base builds context appropriate for age."""
        kb = KnowledgeBase(self.knowledge_dir)
        for fact in INITIAL_FACTS:
            kb.add_fact(fact)

        context_10 = kb.build_context_for_age(10)
        context_14 = kb.build_context_for_age(14)

        # Both should have knowledge base content
        self.assertIn("nursing", context_10.lower())
        self.assertIn("nursing", context_14.lower())
        self.assertIn("finance", context_10.lower())

        # Contexts may differ based on complexity levels available
        self.assertGreater(len(context_10), 0)
        self.assertGreater(len(context_14), 0)

    def test_conversation_flow_with_memory(self):
        """Full conversation flow: input → pipeline → memory → notification."""
        memory = Memory(self.memory_dir)
        notifications = NotificationHandler(self.memory_dir / "notifications.log")
        kb = KnowledgeBase(self.knowledge_dir)

        for fact in INITIAL_FACTS:
            kb.add_fact(fact)

        profile = memory.load_or_create_profile("TestDaughter", 10)
        self.assertEqual(profile.name, "TestDaughter")
        self.assertEqual(profile.age, 10)

        # Simulate conversation
        user_turn = ConversationTurn(
            timestamp=datetime.now().isoformat(),
            role="user",
            text="What do nurses do?",
            topic="nursing",
        )
        memory.append_turn(user_turn)

        # Simulate response with knowledge context
        kb_context = kb.build_context_for_age(10, topics=["nursing"])
        self.assertIn("nursing", kb_context.lower())

        ava_response = "Nurses help patients who are sick or hurt."
        assessments = assess_response(ava_response, sources=[])

        # Save response
        assistant_turn = ConversationTurn(
            timestamp=datetime.now().isoformat(),
            role="assistant",
            text=ava_response,
            topic="nursing",
            flagged_for_notification=False,
        )
        memory.append_turn(assistant_turn)

        # Notify on nursing topic (parent info)
        notifications.notify("NURSING", "Discussed nursing career path")

        # Verify everything was saved
        history_file = self.memory_dir / "conversation_history.jsonl"
        self.assertTrue(history_file.exists())
        lines = history_file.read_text().strip().split("\n")
        self.assertEqual(len(lines), 2)  # user + assistant

        log_file = self.memory_dir / "notifications.log"
        self.assertTrue(log_file.exists())
        self.assertIn("NURSING", log_file.read_text())

    def test_age_progression_affects_knowledge(self):
        """As daughter ages, different facts become available."""
        kb = KnowledgeBase(self.knowledge_dir)
        for fact in INITIAL_FACTS:
            kb.add_fact(fact)

        facts_10 = kb.get_facts_for_age(10)
        facts_14 = kb.get_facts_for_age(14)
        facts_18 = kb.get_facts_for_age(18)

        # All should have content, but complexity should differ
        self.assertGreater(len(facts_10), 0)
        self.assertGreater(len(facts_14), 0)
        self.assertGreater(len(facts_18), 0)

        # At age 18, she should have more ADVANCED facts
        advanced_count_18 = sum(1 for f in facts_18 if f.complexity.value == 3)
        advanced_count_10 = sum(1 for f in facts_10 if f.complexity.value == 3)
        self.assertGreaterEqual(advanced_count_18, advanced_count_10)


if __name__ == "__main__":
    unittest.main()
