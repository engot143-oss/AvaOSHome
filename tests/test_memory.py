import sys
import json
import tempfile
import unittest
from pathlib import Path
from datetime import datetime

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from avaos.memory import Memory, ConversationTurn, UserProfile


class TestMemory(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.memory = Memory(Path(self.temp_dir.name))

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_create_and_load_profile(self):
        profile = self.memory.load_or_create_profile("Emma", age=10)
        self.assertEqual(profile.name, "Emma")
        self.assertEqual(profile.age, 10)

        reloaded = self.memory.load_or_create_profile("Emma", age=10)
        self.assertEqual(reloaded.name, "Emma")

    def test_update_interests_and_goals(self):
        self.memory.load_or_create_profile("Emma", age=10)
        updated = self.memory.update_profile(
            interests=("nursing", "science"),
            goals=("learn anatomy", "get good grades"),
        )
        self.assertEqual(updated.interests, ("nursing", "science"))
        self.assertEqual(updated.goals, ("learn anatomy", "get good grades"))

        reloaded = self.memory.load_or_create_profile("Emma", age=10)
        self.assertEqual(reloaded.interests, ("nursing", "science"))

    def test_append_and_load_conversation_turns(self):
        turn1 = ConversationTurn(
            timestamp=datetime.now().isoformat(),
            role="user",
            text="What's the nursing career path?",
            topic="school",
        )
        turn2 = ConversationTurn(
            timestamp=datetime.now().isoformat(),
            role="assistant",
            text="Nursing requires...",
            topic="school",
        )
        self.memory.append_turn(turn1)
        self.memory.append_turn(turn2)

        history = self.memory.load_history()
        self.assertEqual(len(history), 2)
        self.assertEqual(history[0].role, "user")
        self.assertEqual(history[1].role, "assistant")

    def test_recent_context_formatting(self):
        now = datetime.now().isoformat()
        self.memory.append_turn(ConversationTurn(timestamp=now, role="user", text="Hi"))
        self.memory.append_turn(ConversationTurn(timestamp=now, role="assistant", text="Hello!"))

        context = self.memory.recent_context(num_turns=2)
        self.assertIn("User: Hi", context)
        self.assertIn("Assistant: Hello!", context)


if __name__ == "__main__":
    unittest.main()
