"""
Parent-facing tools to manage AVA's knowledge base over time.

Simple CLI for:
- Adding new facts
- Updating existing facts
- Checking what the daughter has learned
- Viewing available knowledge for her current age
"""

from __future__ import annotations

from pathlib import Path

from .knowledge import KnowledgeBase, KnowledgeFact, Complexity, INITIAL_FACTS


def initialize_knowledge_base(kb_dir: Path) -> None:
    """Create the initial knowledge base."""
    kb = KnowledgeBase(kb_dir)
    print("Initializing knowledge base...")
    for fact in INITIAL_FACTS:
        kb.add_fact(fact)
    print(f"✅ Added {len(INITIAL_FACTS)} initial facts")


def show_knowledge_for_age(kb_dir: Path, age: int) -> None:
    """Show what knowledge is available for a given age."""
    kb = KnowledgeBase(kb_dir)
    topics = ["nursing", "finance", "life_skills"]

    print(f"\n📚 Knowledge base for {age}-year-old:\n")
    for topic in topics:
        facts = kb.get_facts_for_age(age, topic)
        if facts:
            print(f"\n{topic.replace('_', ' ').title()}:")
            for fact in facts:
                print(f"  • {fact.title} ({fact.complexity.name.lower()})")
        else:
            print(f"\n{topic.replace('_', ' ').title()}: (no content yet)")


def show_learned_topics(kb_dir: Path) -> None:
    """Show what the daughter has already learned."""
    kb = KnowledgeBase(kb_dir)
    learned = kb.get_learned_topics()

    if not learned:
        print("\n📚 No topics learned yet!")
        return

    print(f"\n📚 Topics learned ({len(learned)} total):\n")
    by_topic = {}
    for l in learned:
        if l.topic not in by_topic:
            by_topic[l.topic] = []
        by_topic[l.topic].append(l)

    for topic, items in sorted(by_topic.items()):
        print(f"{topic.replace('_', ' ').title()}: {len(items)} lessons")
        for item in items[-3:]:  # show 3 most recent
            print(f"  • {item.fact_id} (learned at age {item.learned_at_age})")


def add_custom_fact(kb_dir: Path) -> None:
    """Interactively add a new fact to the knowledge base."""
    print("\n📝 Add a new fact to the knowledge base\n")

    fact_id = input("Fact ID (e.g. 'nursing-04'): ").strip()
    topic = input("Topic (nursing/finance/life_skills/other): ").strip()
    title = input("Title (short name of the concept): ").strip()
    explanation = input("Explanation (the actual content to teach): ").strip()

    min_age = int(input("Minimum age (default 8): ") or "8")
    max_age = int(input("Maximum age (default 18): ") or "18")

    print("\nComplexity level:")
    print("1. BEGINNER (simple, concrete examples)")
    print("2. INTERMEDIATE (nuance, some numbers)")
    print("3. ADVANCED (technical detail, adult level)")
    complexity_choice = input("Choose (1-3, default 1): ").strip() or "1"
    complexity_map = {"1": Complexity.BEGINNER, "2": Complexity.INTERMEDIATE, "3": Complexity.ADVANCED}
    complexity = complexity_map.get(complexity_choice, Complexity.BEGINNER)

    verified = input("Has this been fact-checked? (y/n, default n): ").lower().startswith("y")
    source = input("Source/reference (optional): ").strip()
    parent_notes = input("Notes for yourself (optional): ").strip()

    fact = KnowledgeFact(
        id=fact_id,
        topic=topic,
        title=title,
        explanation=explanation,
        min_age=min_age,
        max_age=max_age,
        complexity=complexity,
        verified=verified,
        source=source,
        parent_notes=parent_notes,
    )

    kb = KnowledgeBase(kb_dir)
    kb.add_fact(fact)
    print(f"\n✅ Added fact: {title}")
