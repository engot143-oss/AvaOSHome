"""
Learning analytics for AVA OS.

Tracks:
- Topic engagement (how often discussed)
- Mastery progression (beginner → expert)
- Learning patterns (time spent, pace)
- Knowledge gaps (missed topics)
- Learning streaks (consistency)
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timedelta
from pathlib import Path
from collections import Counter
import json

from .memory import Memory


@dataclass
class TopicEngagement:
    """Tracks engagement with a specific topic."""
    topic: str
    times_discussed: int = 0
    total_messages: int = 0
    first_discussed: str | None = None
    last_discussed: str | None = None
    messages_per_discussion: float = 0.0

    def update(self, message_count: int = 1):
        """Record a discussion."""
        self.times_discussed += 1
        self.total_messages += message_count
        self.messages_per_discussion = self.total_messages / self.times_discussed
        if not self.first_discussed:
            self.first_discussed = datetime.now().isoformat()
        self.last_discussed = datetime.now().isoformat()


@dataclass
class MasteryLevel:
    """Tracks mastery of a specific topic."""
    topic: str
    level: int = 1  # 1-5: novice, beginner, intermediate, advanced, expert
    last_updated: str = field(default_factory=lambda: datetime.now().isoformat())
    discussions_at_level: int = 0
    confidence: float = 0.5  # 0.0-1.0


@dataclass
class LearningStreak:
    """Tracks learning consistency."""
    topic: str
    current_streak: int = 0  # days in a row
    longest_streak: int = 0
    last_discussion_date: str | None = None


@dataclass
class LearningReport:
    """Summary of learning progress."""
    total_conversations: int
    unique_topics: int
    topics_engaged: list[TopicEngagement]
    mastery_levels: dict[str, int]
    learning_streaks: dict[str, int]
    most_discussed_topic: str | None
    knowledge_gaps: list[str]
    learning_efficiency: float  # 0-1, based on topic coverage


class LearningAnalytics:
    """Analyzes learning patterns and progress."""

    def __init__(self, memory_dir: Path):
        self.memory = Memory(memory_dir)
        self.analytics_path = memory_dir / "analytics.json"
        self._load_or_create_analytics()

    def _load_or_create_analytics(self):
        """Load or initialize analytics data."""
        if self.analytics_path.exists():
            self.data = json.loads(self.analytics_path.read_text())
        else:
            self.data = {
                "topics": {},
                "mastery": {},
                "streaks": {},
                "updated": datetime.now().isoformat(),
            }
            self._save()

    def _save(self):
        """Persist analytics to disk."""
        self.data["updated"] = datetime.now().isoformat()
        self.analytics_path.write_text(json.dumps(self.data, indent=2))

    def record_discussion(self, topic: str, message_count: int = 1):
        """Record that a topic was discussed."""
        if topic not in self.data["topics"]:
            self.data["topics"][topic] = {
                "times_discussed": 0,
                "total_messages": 0,
                "first_discussed": None,
                "last_discussed": None,
            }

        topic_data = self.data["topics"][topic]
        topic_data["times_discussed"] += 1
        topic_data["total_messages"] += message_count
        if not topic_data["first_discussed"]:
            topic_data["first_discussed"] = datetime.now().isoformat()
        topic_data["last_discussed"] = datetime.now().isoformat()

        self._update_streak(topic)
        self._save()

    def _update_streak(self, topic: str):
        """Update learning streak for a topic."""
        if topic not in self.data["streaks"]:
            self.data["streaks"][topic] = {
                "current_streak": 0,
                "longest_streak": 0,
                "last_discussion_date": None,
            }

        streak_data = self.data["streaks"][topic]
        today = datetime.now().date().isoformat()

        if not streak_data["last_discussion_date"]:
            streak_data["current_streak"] = 1
            streak_data["longest_streak"] = 1
        else:
            last_date = datetime.fromisoformat(streak_data["last_discussion_date"]).date()
            today_date = datetime.now().date()
            days_diff = (today_date - last_date).days

            if days_diff == 0:
                # Same day, don't increment streak
                pass
            elif days_diff == 1:
                # Consecutive day, increment streak
                streak_data["current_streak"] += 1
                streak_data["longest_streak"] = max(
                    streak_data["longest_streak"],
                    streak_data["current_streak"]
                )
            else:
                # Streak broken, reset
                streak_data["current_streak"] = 1

        streak_data["last_discussion_date"] = today

    def set_mastery(self, topic: str, level: int):
        """Set mastery level for a topic (1-5)."""
        level = max(1, min(5, level))  # Clamp to 1-5
        if topic not in self.data["mastery"]:
            self.data["mastery"][topic] = {
                "level": level,
                "last_updated": datetime.now().isoformat(),
                "discussions_at_level": 0,
            }
        else:
            self.data["mastery"][topic]["level"] = level
            self.data["mastery"][topic]["last_updated"] = datetime.now().isoformat()
        self._save()

    def get_topic_engagement(self) -> list[TopicEngagement]:
        """Get engagement for all topics."""
        engagements = []
        for topic, data in self.data["topics"].items():
            eng = TopicEngagement(
                topic=topic,
                times_discussed=data["times_discussed"],
                total_messages=data["total_messages"],
                first_discussed=data["first_discussed"],
                last_discussed=data["last_discussed"],
            )
            if eng.times_discussed > 0:
                eng.messages_per_discussion = eng.total_messages / eng.times_discussed
            engagements.append(eng)

        # Sort by engagement (times discussed)
        return sorted(engagements, key=lambda e: e.times_discussed, reverse=True)

    def get_mastery_levels(self) -> dict[str, int]:
        """Get current mastery level for each topic."""
        return {
            topic: data["level"]
            for topic, data in self.data["mastery"].items()
        }

    def get_learning_streaks(self) -> dict[str, int]:
        """Get current learning streaks for each topic."""
        return {
            topic: data["current_streak"]
            for topic, data in self.data["streaks"].items()
        }

    def get_knowledge_gaps(self, all_topics: list[str]) -> list[str]:
        """Identify topics that haven't been discussed."""
        discussed = set(self.data["topics"].keys())
        all_topics_set = set(all_topics)
        return sorted(list(all_topics_set - discussed))

    def generate_report(self, all_topics: list[str]) -> LearningReport:
        """Generate a comprehensive learning report."""
        history = self.memory.load_history()
        total_conversations = len(history)

        engagements = self.get_topic_engagement()
        mastery = self.get_mastery_levels()
        streaks = self.get_learning_streaks()
        gaps = self.get_knowledge_gaps(all_topics)

        most_discussed = engagements[0].topic if engagements else None

        # Calculate learning efficiency (topics covered / total topics)
        unique_topics = len(self.data["topics"])
        learning_efficiency = unique_topics / len(all_topics) if all_topics else 0

        return LearningReport(
            total_conversations=total_conversations,
            unique_topics=unique_topics,
            topics_engaged=engagements,
            mastery_levels=mastery,
            learning_streaks=streaks,
            most_discussed_topic=most_discussed,
            knowledge_gaps=gaps,
            learning_efficiency=learning_efficiency,
        )

    def get_recommendations(self) -> list[str]:
        """Suggest topics to focus on next."""
        recommendations = []

        # Recommend topics not yet discussed
        for topic, data in self.data["topics"].items():
            if data["times_discussed"] == 1:
                recommendations.append(f"Review {topic} - only discussed once")

        # Recommend increasing mastery in high-engagement topics
        mastery = self.get_mastery_levels()
        engagement = self.get_topic_engagement()

        for eng in engagement[:3]:  # Top 3 topics
            current_mastery = mastery.get(eng.topic, 1)
            if current_mastery < 5:
                next_level = current_mastery + 1
                recommendations.append(
                    f"Push {eng.topic} from level {current_mastery} to {next_level}"
                )

        return recommendations

    def export_analytics(self) -> dict:
        """Export all analytics data."""
        report = self.generate_report([
            topic for topic in self.data["topics"].keys()
        ])

        return {
            "report": {
                "total_conversations": report.total_conversations,
                "unique_topics": report.unique_topics,
                "learning_efficiency": report.learning_efficiency,
                "most_discussed_topic": report.most_discussed_topic,
            },
            "topics": {
                eng.topic: {
                    "times_discussed": eng.times_discussed,
                    "total_messages": eng.total_messages,
                    "messages_per_discussion": eng.messages_per_discussion,
                    "mastery_level": report.mastery_levels.get(eng.topic, 1),
                    "streak": report.learning_streaks.get(eng.topic, 0),
                }
                for eng in report.topics_engaged
            },
            "recommendations": self.get_recommendations(),
        }


def format_learning_report(report: LearningReport) -> str:
    """Format a learning report as readable text."""
    lines = [
        f"Total Conversations: {report.total_conversations}",
        f"Topics Engaged: {report.unique_topics}",
        f"Learning Efficiency: {report.learning_efficiency * 100:.1f}%",
        "",
        "Top Topics:",
    ]

    for eng in report.topics_engaged[:3]:
        lines.append(
            f"  • {eng.topic}: {eng.times_discussed}x "
            f"({eng.messages_per_discussion:.1f} messages/discussion)"
        )

    if report.knowledge_gaps:
        lines.append(f"\nKnowledge Gaps ({len(report.knowledge_gaps)}):")
        for gap in report.knowledge_gaps[:3]:
            lines.append(f"  • {gap}")
        if len(report.knowledge_gaps) > 3:
            lines.append(f"  ... and {len(report.knowledge_gaps) - 3} more")

    return "\n".join(lines)
