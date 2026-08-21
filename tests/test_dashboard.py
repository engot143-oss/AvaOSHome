"""
Unit tests for the parental dashboard.
"""

import sys
import tempfile
import unittest
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from avaos.dashboard import DashboardServer
from avaos.memory import Memory, ConversationTurn
from avaos.knowledge import KnowledgeBase, INITIAL_FACTS
from avaos.chat import NotificationHandler


class TestDashboard(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.memory_dir = Path(self.temp_dir.name) / "memory"
        self.knowledge_dir = Path(self.temp_dir.name) / "knowledge"
        self.memory_dir.mkdir(parents=True, exist_ok=True)
        self.knowledge_dir.mkdir(parents=True, exist_ok=True)

        self.server = DashboardServer(
            memory_dir=self.memory_dir,
            knowledge_dir=self.knowledge_dir,
            port=5001,
        )
        self.client = self.server.app.test_client()

        # Populate test data
        self._setup_test_data()

    def tearDown(self):
        self.temp_dir.cleanup()

    def _setup_test_data(self):
        """Create sample data for testing."""
        # Add conversations
        memory = Memory(self.memory_dir)
        memory.load_or_create_profile("Test Daughter", 10)

        for i, topic in enumerate(["nursing", "finance", "nursing"]):
            user_turn = ConversationTurn(
                timestamp=datetime.now().isoformat(),
                role="user",
                text=f"Question {i+1} about {topic}",
                topic=topic,
            )
            memory.append_turn(user_turn)

            assistant_turn = ConversationTurn(
                timestamp=datetime.now().isoformat(),
                role="assistant",
                text=f"Answer {i+1} about {topic}",
                topic=topic,
            )
            memory.append_turn(assistant_turn)

        # Add notifications
        notifications = NotificationHandler(self.memory_dir / "notifications.log")
        notifications.notify("NURSING", "Discussed nursing career")
        notifications.notify("FINANCIAL", "Discussed savings")

        # Add knowledge
        kb = KnowledgeBase(self.knowledge_dir)
        for fact in INITIAL_FACTS:
            kb.add_fact(fact)

    def test_dashboard_loads(self):
        """Dashboard homepage should load."""
        response = self.client.get("/")
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"AVA OS", response.data)
        self.assertIn(b"Parental Dashboard", response.data)

    def test_stats_endpoint(self):
        """Stats endpoint should return correct counts."""
        response = self.client.get("/api/stats")
        self.assertEqual(response.status_code, 200)

        data = response.get_json()
        self.assertEqual(data["conversation_turns"], 6)  # 3 Q&A pairs
        self.assertEqual(data["notifications"], 2)
        self.assertEqual(data["topics_learned"], 0)  # None learned yet
        self.assertIn("nursing", data["topics_discussed"])

    def test_conversations_endpoint(self):
        """Conversations endpoint should return history."""
        response = self.client.get("/api/conversations")
        self.assertEqual(response.status_code, 200)

        data = response.get_json()
        self.assertEqual(len(data), 6)
        self.assertEqual(data[0]["role"], "assistant")  # Most recent first
        self.assertIn("topic", data[0])

    def test_conversations_filter_by_topic(self):
        """Should filter conversations by topic."""
        response = self.client.get("/api/conversations?topic=nursing")
        self.assertEqual(response.status_code, 200)

        data = response.get_json()
        self.assertTrue(all(c["topic"] == "nursing" for c in data))
        self.assertEqual(len(data), 4)  # 2 nursing Q&A pairs

    def test_conversations_limit(self):
        """Should respect limit parameter."""
        response = self.client.get("/api/conversations?limit=2")
        self.assertEqual(response.status_code, 200)

        data = response.get_json()
        self.assertEqual(len(data), 2)

    def test_notifications_endpoint(self):
        """Notifications endpoint should return logs."""
        response = self.client.get("/api/notifications")
        self.assertEqual(response.status_code, 200)

        data = response.get_json()
        self.assertEqual(len(data), 2)
        self.assertEqual(data[0]["topic"], "FINANCIAL")  # Most recent first
        self.assertIn("message", data[0])

    def test_knowledge_endpoint(self):
        """Knowledge endpoint should return age-appropriate facts."""
        response = self.client.get("/api/knowledge?age=10")
        self.assertEqual(response.status_code, 200)

        data = response.get_json()
        self.assertGreater(len(data), 0)
        # All should have required fields
        for fact in data:
            self.assertIn("id", fact)
            self.assertIn("title", fact)
            self.assertIn("complexity", fact)

    def test_knowledge_filter_by_topic(self):
        """Should filter knowledge by topic."""
        response = self.client.get("/api/knowledge?age=10&topic=nursing")
        self.assertEqual(response.status_code, 200)

        data = response.get_json()
        self.assertTrue(all(f["topic"] == "nursing" for f in data))

    def test_knowledge_filter_by_age(self):
        """Should return facts for correct age."""
        response_10 = self.client.get("/api/knowledge?age=10")
        response_16 = self.client.get("/api/knowledge?age=16")

        self.assertEqual(response_10.status_code, 200)
        self.assertEqual(response_16.status_code, 200)

        # Should have some facts at both ages
        data_10 = response_10.get_json()
        data_16 = response_16.get_json()

        self.assertGreater(len(data_10), 0)
        # Note: at age 16, some finance facts won't be available

    def test_learned_endpoint(self):
        """Learned endpoint should return tracking data."""
        response = self.client.get("/api/learned")
        self.assertEqual(response.status_code, 200)

        data = response.get_json()
        # Initially empty
        self.assertEqual(len(data), 0)

    def test_empty_conversations(self):
        """Should handle empty conversation history gracefully."""
        empty_dir = Path(self.temp_dir.name) / "empty"
        empty_dir.mkdir()
        server = DashboardServer(
            memory_dir=empty_dir,
            knowledge_dir=empty_dir,
            port=5002,
        )
        client = server.app.test_client()

        response = client.get("/api/conversations")
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertEqual(len(data), 0)

    def test_empty_notifications(self):
        """Should handle empty notifications gracefully."""
        response = self.client.get("/api/notifications")
        # Create a new server with no notifications
        empty_dir = Path(self.temp_dir.name) / "empty2"
        empty_dir.mkdir()
        server = DashboardServer(
            memory_dir=empty_dir,
            knowledge_dir=empty_dir,
            port=5003,
        )
        client = server.app.test_client()

        response = client.get("/api/notifications")
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertEqual(len(data), 0)


if __name__ == "__main__":
    unittest.main()
