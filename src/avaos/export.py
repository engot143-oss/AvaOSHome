"""
Export and backup utilities for AVA OS.

Supports:
- Exporting conversation history (CSV/JSON)
- Exporting analytics reports
- Exporting knowledge base
- Full system backup
"""

from __future__ import annotations

import json
import csv
from datetime import datetime
from pathlib import Path
from io import StringIO

from .memory import Memory
from .learning_analytics import LearningAnalytics
from .knowledge import KnowledgeBase


class Exporter:
    """Handles data export in various formats."""

    def __init__(self, memory_dir: Path, knowledge_dir: Path):
        self.memory = Memory(memory_dir)
        self.analytics = LearningAnalytics(memory_dir)
        self.kb = KnowledgeBase(knowledge_dir)

    def export_conversations_json(self) -> str:
        """Export conversation history as JSON."""
        history = self.memory.load_history()
        data = {
            "exported": datetime.now().isoformat(),
            "total_turns": len(history),
            "conversations": [
                {
                    "timestamp": turn.timestamp,
                    "role": turn.role,
                    "text": turn.text,
                    "topic": turn.topic,
                }
                for turn in history
            ],
        }
        return json.dumps(data, indent=2)

    def export_conversations_csv(self) -> str:
        """Export conversation history as CSV."""
        history = self.memory.load_history()
        output = StringIO()
        writer = csv.DictWriter(
            output,
            fieldnames=["timestamp", "role", "topic", "text"],
        )

        writer.writeheader()
        for turn in history:
            writer.writerow(
                {
                    "timestamp": turn.timestamp,
                    "role": turn.role,
                    "topic": turn.topic,
                    "text": turn.text,
                }
            )

        return output.getvalue()

    def export_analytics_json(self) -> str:
        """Export analytics data as JSON."""
        export_data = self.analytics.export_analytics()
        return json.dumps(export_data, indent=2)

    def export_knowledge_base_json(self) -> str:
        """Export knowledge base as JSON."""
        all_topics = set()

        # Collect all topics
        for age in range(8, 19):
            facts = self.kb.get_facts_for_age(age)
            all_topics.update(f.topic for f in facts)

        data = {
            "exported": datetime.now().isoformat(),
            "topics": {},
        }

        for topic in sorted(all_topics):
            facts_by_age = {}
            for age in range(8, 19):
                facts = self.kb.get_facts_for_age(age, topic=topic)
                if facts:
                    facts_by_age[str(age)] = [
                        {
                            "id": f.id,
                            "title": f.title,
                            "explanation": f.explanation,
                            "complexity": f.complexity.name,
                            "verified": f.verified,
                        }
                        for f in facts
                    ]

            if facts_by_age:
                data["topics"][topic] = facts_by_age

        return json.dumps(data, indent=2)

    def export_profile_json(self) -> str:
        """Export user profile as JSON."""
        profile = self.memory.load_or_create_profile("Unknown", 10)
        return json.dumps(
            {
                "name": profile.name,
                "age": profile.age,
                "date_of_birth": profile.date_of_birth,
                "interests": list(profile.interests),
                "goals": list(profile.goals),
                "exported": datetime.now().isoformat(),
            },
            indent=2,
        )

    def export_full_backup_json(self) -> str:
        """Export complete system backup as JSON."""
        return json.dumps(
            {
                "exported": datetime.now().isoformat(),
                "profile": json.loads(self.export_profile_json()),
                "conversations": json.loads(self.export_conversations_json()),
                "analytics": json.loads(self.export_analytics_json()),
                "knowledge_base": json.loads(self.export_knowledge_base_json()),
            },
            indent=2,
        )

    def create_backup_files(self, backup_dir: Path) -> dict[str, Path]:
        """Create backup files in a directory."""
        backup_dir = Path(backup_dir)
        backup_dir.mkdir(parents=True, exist_ok=True)

        files = {}

        # Profile
        profile_file = backup_dir / "profile.json"
        profile_file.write_text(self.export_profile_json())
        files["profile"] = profile_file

        # Conversations
        conv_file = backup_dir / "conversations.json"
        conv_file.write_text(self.export_conversations_json())
        files["conversations"] = conv_file

        # Analytics
        analytics_file = backup_dir / "analytics.json"
        analytics_file.write_text(self.export_analytics_json())
        files["analytics"] = analytics_file

        # Knowledge Base
        kb_file = backup_dir / "knowledge_base.json"
        kb_file.write_text(self.export_knowledge_base_json())
        files["knowledge_base"] = kb_file

        # Full backup
        backup_file = (
            backup_dir / f"full_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        )
        backup_file.write_text(self.export_full_backup_json())
        files["full_backup"] = backup_file

        return files

    def get_backup_summary(self) -> dict:
        """Get summary of what will be exported."""
        history = self.memory.load_history()
        engagements = self.analytics.get_topic_engagement()
        profile = self.memory.load_or_create_profile("Unknown", 10)

        return {
            "profile_name": profile.name,
            "profile_age": profile.age,
            "total_conversations": len(history),
            "topics_engaged": len(engagements),
            "exported_at": datetime.now().isoformat(),
        }
