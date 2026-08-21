"""
Age progression system for AVA OS.

Automatically unlocks age-appropriate content as the daughter grows.
Tracks milestones (birthdays) and notifies parent of new knowledge levels.

Core concept:
- User profile stores date_of_birth
- On each conversation, check if birthday has passed
- If so, increment age and unlock INTERMEDIATE/ADVANCED facts
- Notify parent of milestone
"""

from __future__ import annotations

from datetime import datetime, date
from pathlib import Path
from dataclasses import dataclass

from .memory import Memory
from .knowledge import KnowledgeBase, LearnedTopic


@dataclass(frozen=True)
class BirthdayMilestone:
    """Represents a birthday milestone."""
    old_age: int
    new_age: int
    date: str  # ISO format
    new_facts_available: int  # How many new facts unlocked


class AgeProgression:
    """Manages age-based knowledge progression."""

    def __init__(self, memory_dir: Path, knowledge_dir: Path):
        self.memory = Memory(memory_dir)
        self.kb = KnowledgeBase(knowledge_dir)

    def calculate_current_age(self, date_of_birth: str) -> int:
        """Calculate age from date of birth (ISO format YYYY-MM-DD)."""
        birth = datetime.fromisoformat(date_of_birth).date()
        today = date.today()
        age = today.year - birth.year
        # Adjust if birthday hasn't happened this year
        if (today.month, today.day) < (birth.month, birth.day):
            age -= 1
        return age

    def check_birthday(self, profile_name: str, profile_age: int, date_of_birth: str | None) -> BirthdayMilestone | None:
        """
        Check if a birthday has passed.

        Returns BirthdayMilestone if age has increased, None otherwise.
        """
        if not date_of_birth:
            return None

        current_age = self.calculate_current_age(date_of_birth)

        if current_age > profile_age:
            # Birthday has passed - age progressed
            # Count new facts available at new age
            old_facts = self.kb.get_facts_for_age(profile_age)
            new_facts = self.kb.get_facts_for_age(current_age)
            new_facts_count = len(new_facts) - len(old_facts)

            return BirthdayMilestone(
                old_age=profile_age,
                new_age=current_age,
                date=datetime.now().isoformat(),
                new_facts_available=new_facts_count,
            )

        return None

    def get_new_facts_for_age(self, old_age: int, new_age: int) -> list:
        """Get facts that become available after birthday."""
        old_facts = set(f.id for f in self.kb.get_facts_for_age(old_age))
        new_facts = self.kb.get_facts_for_age(new_age)
        return [f for f in new_facts if f.id not in old_facts]

    def get_complexity_progression(self, topic: str, age: int) -> list:
        """Get facts for a topic, sorted by complexity level (for birthday context)."""
        facts = self.kb.get_facts_for_age(age, topic=topic)
        return sorted(facts, key=lambda f: f.complexity.value)


def format_birthday_notification(milestone: BirthdayMilestone) -> str:
    """Format a birthday milestone as a notification message."""
    return (
        f"Birthday milestone! She's now {milestone.new_age} years old. "
        f"{milestone.new_facts_available} new knowledge topics unlocked. "
        f"Check the knowledge base for more sophisticated explanations."
    )


def format_birthday_message(milestone: BirthdayMilestone, new_facts: list) -> str:
    """Format a birthday message for display to the daughter."""
    topics = ", ".join(set(f.topic for f in new_facts))
    return (
        f"Happy Birthday! You're now {milestone.new_age} years old! "
        f"I've unlocked new lessons about {topics} "
        f"that are more suited to your age."
    )
