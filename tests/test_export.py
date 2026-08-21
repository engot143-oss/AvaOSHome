"""
Tests for export and backup functionality.
"""

import sys
import tempfile
import unittest
import json
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from avaos.export import Exporter
from avaos.memory import Memory, ConversationTurn
from avaos.knowledge import KnowledgeBase, INITIAL_FACTS
from avaos.learning_analytics import LearningAnalytics
from datetime import datetime


class TestExport(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.memory_dir = Path(self.temp_dir.name) / "memory"
        self.knowledge_dir = Path(self.temp_dir.name) / "knowledge"
        self.memory_dir.mkdir()
        self.knowledge_dir.mkdir()

        # Setup test data
        memory = Memory(self.memory_dir)
        memory.load_or_create_profile("Test", 10)

        turn = ConversationTurn(
            timestamp=datetime.now().isoformat(),
            role="user",
            text="Test message",
            topic="nursing",
        )
        memory.append_turn(turn)

        kb = KnowledgeBase(self.knowledge_dir)
        for fact in INITIAL_FACTS:
            kb.add_fact(fact)

        analytics = LearningAnalytics(self.memory_dir)
        analytics.record_discussion("nursing", 2)

        self.exporter = Exporter(self.memory_dir, self.knowledge_dir)

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_export_conversations_json(self):
        """Should export conversations as JSON."""
        data = self.exporter.export_conversations_json()
        parsed = json.loads(data)

        self.assertIn("exported", parsed)
        self.assertIn("conversations", parsed)
        self.assertGreater(len(parsed["conversations"]), 0)

    def test_export_conversations_csv(self):
        """Should export conversations as CSV."""
        data = self.exporter.export_conversations_csv()

        self.assertIn("timestamp", data)
        self.assertIn("role", data)
        self.assertIn("topic", data)
        self.assertIn("user", data)

    def test_export_analytics_json(self):
        """Should export analytics as JSON."""
        data = self.exporter.export_analytics_json()
        parsed = json.loads(data)

        self.assertIn("report", parsed)
        self.assertIn("topics", parsed)

    def test_export_knowledge_base_json(self):
        """Should export knowledge base as JSON."""
        data = self.exporter.export_knowledge_base_json()
        parsed = json.loads(data)

        self.assertIn("topics", parsed)
        self.assertGreater(len(parsed["topics"]), 0)

    def test_export_profile_json(self):
        """Should export user profile as JSON."""
        data = self.exporter.export_profile_json()
        parsed = json.loads(data)

        self.assertIn("name", parsed)
        self.assertIn("age", parsed)
        self.assertEqual(parsed["name"], "Test")
        self.assertEqual(parsed["age"], 10)

    def test_export_full_backup_json(self):
        """Should export complete system backup."""
        data = self.exporter.export_full_backup_json()
        parsed = json.loads(data)

        self.assertIn("profile", parsed)
        self.assertIn("conversations", parsed)
        self.assertIn("analytics", parsed)
        self.assertIn("knowledge_base", parsed)

    def test_create_backup_files(self):
        """Should create backup files in directory."""
        backup_dir = Path(self.temp_dir.name) / "backup"
        files = self.exporter.create_backup_files(backup_dir)

        self.assertIn("profile", files)
        self.assertIn("conversations", files)
        self.assertIn("analytics", files)
        self.assertIn("knowledge_base", files)
        self.assertIn("full_backup", files)

        # Verify files exist
        for file_path in files.values():
            self.assertTrue(file_path.exists())

    def test_backup_summary(self):
        """Should generate backup summary."""
        summary = self.exporter.get_backup_summary()

        self.assertIn("profile_name", summary)
        self.assertIn("profile_age", summary)
        self.assertIn("total_conversations", summary)
        self.assertIn("topics_engaged", summary)
        self.assertEqual(summary["profile_name"], "Test")


if __name__ == "__main__":
    unittest.main()
