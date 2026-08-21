"""
Age-progressive knowledge base for AVA OS.

Stores curated, verified facts about topics the daughter should learn,
tagged with age ranges. As she grows, the system automatically selects
more sophisticated content while keeping simpler explanations as fallback.

Structure:
- Topics: nursing, finance, life_skills, school, etc.
- Each fact is tagged with min_age, max_age, complexity level
- Parent can add, update, or deprecate facts over time
- System tracks which facts have been "taught" to avoid repetition
"""

from __future__ import annotations

import json
from dataclasses import dataclass, asdict, field
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any


class Complexity(Enum):
    """How abstract/sophisticated the explanation is."""
    BEGINNER = 1      # 8-10 years old: simple, concrete examples
    INTERMEDIATE = 2  # 11-14 years old: nuance, cause/effect, some numbers
    ADVANCED = 3      # 15+ years old: technical detail, edge cases, adult perspective


@dataclass(frozen=True)
class KnowledgeFact:
    """One verified fact or concept the system can teach."""
    id: str                                  # unique id, e.g. "nursing-01"
    topic: str                               # "nursing", "finance", "life_skills"
    title: str                               # "What nurses actually do"
    explanation: str                         # The actual content to teach
    min_age: int = 8
    max_age: int = 18
    complexity: Complexity = Complexity.BEGINNER
    verified: bool = True                    # Has this been fact-checked?
    last_updated: str = field(default_factory=lambda: datetime.now().isoformat())
    source: str = ""                         # Where this came from (book, URL, expert, etc.)
    parent_notes: str = ""                   # Notes for the parent


@dataclass(frozen=True)
class LearnedTopic:
    """Tracks what the daughter has already learned about."""
    topic: str
    fact_id: str
    learned_at_age: int
    date_learned: str = field(default_factory=lambda: datetime.now().isoformat())
    mastery_level: int = 1                   # 1-3: beginner, intermediate, advanced


class KnowledgeBase:
    """Manages age-progressive knowledge for the system."""

    def __init__(self, kb_dir: Path):
        self.kb_dir = Path(kb_dir)
        self.kb_dir.mkdir(parents=True, exist_ok=True)
        self._facts_path = self.kb_dir / "facts.jsonl"
        self._learned_path = self.kb_dir / "learned.jsonl"

    def add_fact(self, fact: KnowledgeFact) -> None:
        """Add a new fact to the knowledge base."""
        with open(self._facts_path, "a") as f:
            f.write(json.dumps(asdict(fact, dict_factory=self._encode_enums)) + "\n")

    def _encode_enums(self, field_dict):
        """Helper to serialize enums as strings."""
        return {
            k: v.name if isinstance(v, Enum) else v
            for k, v in field_dict
        }

    def get_facts_for_age(self, current_age: int, topic: str | None = None) -> list[KnowledgeFact]:
        """Get all facts appropriate for a given age."""
        if not self._facts_path.exists():
            return []

        facts = []
        for line in self._facts_path.read_text().splitlines():
            if not line.strip():
                continue
            data = json.loads(line)
            if data.get("min_age", 8) <= current_age <= data.get("max_age", 18):
                if topic is None or data.get("topic") == topic:
                    data["complexity"] = Complexity[data.get("complexity", "BEGINNER")]
                    facts.append(KnowledgeFact(**data))

        # Sort by complexity so simpler explanations come first
        return sorted(facts, key=lambda f: f.complexity.value)

    def mark_learned(self, topic: str, fact_id: str, current_age: int) -> None:
        """Record that the daughter has learned a fact."""
        learned = LearnedTopic(
            topic=topic,
            fact_id=fact_id,
            learned_at_age=current_age,
        )
        with open(self._learned_path, "a") as f:
            f.write(json.dumps(asdict(learned)) + "\n")

    def get_learned_topics(self) -> list[LearnedTopic]:
        """Get all topics the daughter has learned about."""
        if not self._learned_path.exists():
            return []
        learned = []
        for line in self._learned_path.read_text().splitlines():
            if line.strip():
                learned.append(LearnedTopic(**json.loads(line)))
        return learned

    def build_context_for_age(self, current_age: int, topics: list[str] | None = None) -> str:
        """Build a prompt with age-appropriate facts for Claude to use."""
        target_topics = topics or ["nursing", "finance", "life_skills"]
        lines = [f"Knowledge base for {current_age}-year-old:\n"]

        for topic in target_topics:
            facts = self.get_facts_for_age(current_age, topic)
            if facts:
                lines.append(f"\n## {topic.replace('_', ' ').title()}")
                for fact in facts[:3]:  # top 3 most relevant per topic
                    lines.append(f"- **{fact.title}**: {fact.explanation}")

        return "\n".join(lines)


# Initial curated knowledge base
INITIAL_FACTS = [
    # NURSING (for a 10-year-old who wants to be a nurse)
    KnowledgeFact(
        id="nursing-01",
        topic="nursing",
        title="What nurses actually do every day",
        explanation=(
            "Nurses help people who are sick or hurt feel better. They check how "
            "patients are feeling, give medicine, change bandages, and talk to "
            "doctors to make sure patients get the right care. It's like being a "
            "helper and a detective at the same time."
        ),
        min_age=8,
        max_age=11,
        complexity=Complexity.BEGINNER,
        source="Career guides for kids",
    ),
    KnowledgeFact(
        id="nursing-02",
        topic="nursing",
        title="Different types of nursing jobs",
        explanation=(
            "There are many kinds of nurses: emergency room nurses (help in sudden "
            "situations), pediatric nurses (work with kids), surgical nurses (help "
            "during operations), and school nurses (work in schools). Each one needs "
            "different skills, but they all help people."
        ),
        min_age=10,
        max_age=14,
        complexity=Complexity.INTERMEDIATE,
        source="Career guides",
    ),
    KnowledgeFact(
        id="nursing-03",
        topic="nursing",
        title="How to become a nurse",
        explanation=(
            "To be a nurse, you need to: (1) do well in school, especially science; "
            "(2) go to a nursing program in college (usually 2-4 years); (3) pass a "
            "test called the NCLEX; (4) get a license. You can start with an Associate "
            "degree (2 years) or Bachelor's (4 years). Most new nurses earn $35,000-45,000 "
            "their first year."
        ),
        min_age=11,
        max_age=18,
        complexity=Complexity.INTERMEDIATE,
        source="Bureau of Labor Statistics",
    ),
    # FINANCIAL LITERACY (for a 10-year-old)
    KnowledgeFact(
        id="finance-01",
        topic="finance",
        title="What money is and why it matters",
        explanation=(
            "Money is how we trade for things we need or want. Instead of trading "
            "a chicken for bread, we use money. The more money you have, the more "
            "choices you have — like going to school, buying food, or saving for "
            "something special."
        ),
        min_age=8,
        max_age=10,
        complexity=Complexity.BEGINNER,
        source="Financial literacy for kids",
    ),
    KnowledgeFact(
        id="finance-02",
        topic="finance",
        title="Earning money: allowance and chores",
        explanation=(
            "You can earn money by doing chores or a job. An allowance is money "
            "your parents give you for doing responsibilities around the house. A "
            "job is when someone pays you for work (like babysitting or yard work). "
            "If you earn $10/week, that's $520/year — enough to buy something nice!"
        ),
        min_age=9,
        max_age=12,
        complexity=Complexity.BEGINNER,
        source="Financial literacy curricula",
    ),
    KnowledgeFact(
        id="finance-03",
        topic="finance",
        title="Saving money for goals",
        explanation=(
            "Instead of spending all your money right away, you can save it. If you "
            "save $5/week, in 20 weeks you'll have $100 for something bigger (like "
            "headphones or a camera). The longer you save, the more you can buy. This "
            "is called having a 'savings goal.'"
        ),
        min_age=9,
        max_age=12,
        complexity=Complexity.BEGINNER,
        source="Financial literacy curricula",
    ),
    KnowledgeFact(
        id="finance-04",
        topic="finance",
        title="How banks work and why saving there helps",
        explanation=(
            "A bank is a place that keeps your money safe and even pays YOU a tiny "
            "bit extra for letting them use it (called 'interest'). If you put $100 "
            "in a bank savings account, after a year you might have $101. It's slow, "
            "but your money is safe and growing."
        ),
        min_age=10,
        max_age=14,
        complexity=Complexity.INTERMEDIATE,
        source="Financial literacy curricula",
    ),
    # LIFE SKILLS
    KnowledgeFact(
        id="life-01",
        topic="life_skills",
        title="Dealing with tough feelings",
        explanation=(
            "Everyone gets sad, angry, or scared sometimes. That's normal. When you "
            "feel bad, you can: (1) talk to someone you trust, (2) take deep breaths, "
            "(3) do something you enjoy, (4) write about how you feel. These feelings "
            "usually go away after a while."
        ),
        min_age=8,
        max_age=14,
        complexity=Complexity.BEGINNER,
        source="Social-emotional learning curriculum",
    ),
    KnowledgeFact(
        id="life-02",
        topic="life_skills",
        title="How to handle friend drama",
        explanation=(
            "Sometimes friends disagree or hurt your feelings. Try this: (1) talk to "
            "them calmly about how you feel, (2) listen to their side, (3) find a "
            "compromise, (4) if it doesn't work, take a break from that friendship "
            "for a while. Real friends can work through disagreements."
        ),
        min_age=9,
        max_age=15,
        complexity=Complexity.INTERMEDIATE,
        source="Conflict resolution for kids",
    ),
    KnowledgeFact(
        id="life-03",
        topic="life_skills",
        title="Time management: getting things done without stress",
        explanation=(
            "You can manage your time by: (1) breaking big tasks into smaller ones, "
            "(2) doing the hard stuff first, (3) taking breaks, (4) not waiting until "
            "the last minute. If you spend 30 minutes/day on homework, you finish "
            "before bedtime. If you wait until night, you're stressed."
        ),
        min_age=10,
        max_age=16,
        complexity=Complexity.INTERMEDIATE,
        source="Productivity for students",
    ),
]
