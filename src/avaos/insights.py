"""
Advanced insights for AVA OS.

Tracks:
- Sentiment analysis of conversations
- Emotional patterns over time
- Learning velocity (pace of progress)
- Engagement trends
- Stress indicators
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from datetime import datetime, timedelta
from pathlib import Path
from collections import Counter
import json

from .memory import Memory
from .learning_analytics import LearningAnalytics


class SentimentAnalyzer:
    """Simple sentiment analysis for text."""

    # Positive indicators
    POSITIVE_WORDS = {
        "happy", "great", "love", "awesome", "good", "excellent", "fun",
        "amazing", "wonderful", "fantastic", "thank", "appreciate", "proud",
        "excited", "perfect", "best", "accomplished",
    }

    # Negative indicators
    NEGATIVE_WORDS = {
        "sad", "frustrated", "angry", "hate", "bad", "terrible", "awful",
        "horrible", "frustrated", "stress", "anxious", "worried", "confused",
        "stuck", "lost", "difficult", "hard", "fail", "failure",
    }

    # Stress indicators
    STRESS_WORDS = {
        "stressed", "anxiety", "anxious", "panic", "overwhelm", "tired",
        "exhausted", "burned out", "pressure", "deadline", "test",
    }

    @staticmethod
    def analyze(text: str) -> dict:
        """Analyze sentiment of text."""
        lowered = text.lower()

        positive_count = sum(1 for word in SentimentAnalyzer.POSITIVE_WORDS if word in lowered)
        negative_count = sum(1 for word in SentimentAnalyzer.NEGATIVE_WORDS if word in lowered)
        stress_count = sum(1 for word in SentimentAnalyzer.STRESS_WORDS if word in lowered)

        total = positive_count + negative_count
        if total == 0:
            sentiment = "neutral"
            score = 0.0
        else:
            score = (positive_count - negative_count) / total
            if score > 0.3:
                sentiment = "positive"
            elif score < -0.3:
                sentiment = "negative"
            else:
                sentiment = "neutral"

        return {
            "sentiment": sentiment,
            "score": score,  # -1.0 to 1.0
            "positive_count": positive_count,
            "negative_count": negative_count,
            "stress_level": min(1.0, stress_count / 3.0),  # 0.0 to 1.0
        }


@dataclass(frozen=True)
class EmotionalCheckpoint:
    """Snapshot of emotional state at a time."""
    timestamp: str
    sentiment: str
    stress_level: float
    topic: str
    engagement_level: str  # low, medium, high


class InsightEngine:
    """Generates advanced insights about learning progress."""

    def __init__(self, memory_dir: Path):
        self.memory = Memory(memory_dir)
        self.analytics = LearningAnalytics(memory_dir)
        self.analyzer = SentimentAnalyzer()
        self.insights_file = memory_dir / "insights.json"
        self._load_or_create_insights()

    def _load_or_create_insights(self):
        """Load or initialize insights data."""
        if self.insights_file.exists():
            self.data = json.loads(self.insights_file.read_text())
        else:
            self.data = {
                "emotional_checkpoints": [],
                "updated": datetime.now().isoformat(),
            }
            self._save()

    def _save(self):
        """Persist insights to disk."""
        self.data["updated"] = datetime.now().isoformat()
        self.insights_file.write_text(json.dumps(self.data, indent=2))

    def analyze_sentiment(self, text: str) -> dict:
        """Analyze sentiment of a message."""
        return self.analyzer.analyze(text)

    def record_emotional_checkpoint(self, sentiment: str, stress_level: float, topic: str):
        """Record emotional state."""
        checkpoint = {
            "timestamp": datetime.now().isoformat(),
            "sentiment": sentiment,
            "stress_level": stress_level,
            "topic": topic,
        }
        self.data["emotional_checkpoints"].append(checkpoint)
        self._save()

    def get_emotional_trend(self, days: int = 7) -> dict:
        """Get emotional trend over last N days."""
        cutoff = datetime.now() - timedelta(days=days)

        checkpoints = [
            cp
            for cp in self.data["emotional_checkpoints"]
            if datetime.fromisoformat(cp["timestamp"]) > cutoff
        ]

        if not checkpoints:
            return {
                "period_days": days,
                "checkpoints": 0,
                "avg_sentiment": 0.0,
                "avg_stress": 0.0,
            }

        sentiments = {
            "positive": sum(1 for cp in checkpoints if cp["sentiment"] == "positive"),
            "neutral": sum(1 for cp in checkpoints if cp["sentiment"] == "neutral"),
            "negative": sum(1 for cp in checkpoints if cp["sentiment"] == "negative"),
        }

        avg_stress = sum(cp["stress_level"] for cp in checkpoints) / len(checkpoints)

        return {
            "period_days": days,
            "checkpoints": len(checkpoints),
            "sentiment_distribution": sentiments,
            "avg_stress_level": avg_stress,
        }

    def calculate_learning_velocity(self) -> dict:
        """Calculate pace of learning progress."""
        history = self.memory.load_history()
        if len(history) < 2:
            return {
                "velocity": 0.0,
                "trend": "insufficient_data",
                "discussions_per_day": 0.0,
            }

        first_date = datetime.fromisoformat(history[0].timestamp).date()
        last_date = datetime.fromisoformat(history[-1].timestamp).date()
        days_active = (last_date - first_date).days + 1

        if days_active == 0:
            return {
                "velocity": 0.0,
                "trend": "insufficient_data",
                "discussions_per_day": 0.0,
            }

        discussions_per_day = len(history) / days_active

        # Trend: increasing, stable, or decreasing
        if len(history) > 10:
            first_half_rate = len(history[:5]) / 5
            second_half_rate = len(history[-5:]) / 5
            if second_half_rate > first_half_rate * 1.2:
                trend = "accelerating"
            elif second_half_rate < first_half_rate * 0.8:
                trend = "decelerating"
            else:
                trend = "stable"
        else:
            trend = "insufficient_data"

        return {
            "velocity": discussions_per_day,
            "trend": trend,
            "discussions_per_day": discussions_per_day,
            "days_active": days_active,
        }

    def get_engagement_patterns(self) -> dict:
        """Identify engagement patterns."""
        engagements = self.analytics.get_topic_engagement()

        if not engagements:
            return {
                "primary_interest": None,
                "secondary_interests": [],
                "focus_level": "low",
            }

        # Sort by engagement
        sorted_eng = sorted(engagements, key=lambda e: e.times_discussed, reverse=True)

        primary = sorted_eng[0].topic if sorted_eng else None
        secondary = [e.topic for e in sorted_eng[1:4]] if len(sorted_eng) > 1 else []

        # Calculate focus (concentration on top topics)
        if len(sorted_eng) > 0:
            top_3_discussions = sum(e.times_discussed for e in sorted_eng[:3])
            total_discussions = sum(e.times_discussed for e in sorted_eng)
            focus_ratio = top_3_discussions / total_discussions if total_discussions > 0 else 0
            focus_level = "high" if focus_ratio > 0.6 else "medium" if focus_ratio > 0.4 else "low"
        else:
            focus_level = "low"

        return {
            "primary_interest": primary,
            "secondary_interests": secondary,
            "focus_level": focus_level,
        }

    def identify_stress_indicators(self) -> list[str]:
        """Identify potential stress or disengagement."""
        indicators = []

        # Check emotional trend
        trend = self.get_emotional_trend(7)
        if trend["checkpoints"] > 0 and trend["avg_stress_level"] > 0.7:
            indicators.append("High stress levels in recent conversations")

        # Check velocity
        velocity = self.calculate_learning_velocity()
        if velocity["trend"] == "decelerating":
            indicators.append("Learning pace is slowing down")

        # Check negative sentiment
        if "sentiment_distribution" in trend:
            negative_count = trend["sentiment_distribution"].get("negative", 0)
            if negative_count > 2:
                indicators.append("Multiple conversations with negative sentiment")

        return indicators

    def get_insights_summary(self) -> dict:
        """Generate comprehensive insights summary."""
        return {
            "emotional_trend": self.get_emotional_trend(7),
            "learning_velocity": self.calculate_learning_velocity(),
            "engagement_patterns": self.get_engagement_patterns(),
            "stress_indicators": self.identify_stress_indicators(),
            "generated_at": datetime.now().isoformat(),
        }
