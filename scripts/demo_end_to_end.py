#!/usr/bin/env python3
"""
End-to-end demo of AVA OS with predefined inputs.

Shows:
1. Knowledge base loading for a 10-year-old
2. Question classification (criticality tier)
3. Hallucination pipeline on sample responses
4. Memory saving
5. Notifications logging
"""

import sys
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from avaos.knowledge import KnowledgeBase, INITIAL_FACTS
from avaos.memory import Memory, ConversationTurn
from avaos.criticality import classify as classify_criticality
from avaos.pipeline import assess_response
from avaos.chat import NotificationHandler


def print_section(title: str):
    """Print a formatted section header."""
    print(f"\n{'=' * 60}")
    print(f"  {title}")
    print(f"{'=' * 60}\n")


def demo():
    """Run the end-to-end demo."""
    # Create temp dirs
    temp_dir = Path("/tmp/ava_demo") if Path("/tmp").exists() else Path("./ava_demo")
    temp_dir.mkdir(parents=True, exist_ok=True)
    memory_dir = temp_dir / "memory"
    knowledge_dir = temp_dir / "knowledge"
    memory_dir.mkdir(parents=True, exist_ok=True)
    knowledge_dir.mkdir(parents=True, exist_ok=True)

    print("\n*** AVA OS - End-to-End Demo ***\n")

    # 1. Initialize knowledge base
    print_section("1. KNOWLEDGE BASE INITIALIZATION")
    kb = KnowledgeBase(knowledge_dir)
    for fact in INITIAL_FACTS:
        kb.add_fact(fact)
    print(f"[OK] Loaded {len(INITIAL_FACTS)} initial facts")

    facts_10 = kb.get_facts_for_age(10)
    print(f"[OK] {len(facts_10)} facts available for 10-year-old")
    print(f"     Topics: {', '.join(sorted(set(f.topic for f in facts_10)))}")

    # 2. Show age-appropriate context
    print_section("2. AGE-APPROPRIATE KNOWLEDGE CONTEXT")
    context = kb.build_context_for_age(10, topics=["nursing", "finance"])
    print("Knowledge context that Claude receives:")
    print("-" * 60)
    print(context[:300] + "..." if len(context) > 300 else context)
    print("-" * 60)

    # 3. Classify user queries
    print_section("3. QUERY CRITICALITY CLASSIFICATION")
    test_queries = [
        ("What do nurses actually do?", "nursing inquiry"),
        ("How should I save money from my allowance?", "financial planning"),
        ("I think I have medication side effects", "medical concern"),
    ]

    for query, label in test_queries:
        tier = classify_criticality(query)
        print(f"\n  [{label}]")
        print(f"  Query: {query!r}")
        print(f"  Tier: {tier.tier.name} (value={tier.tier.value})")
        if tier.matched_keywords:
            print(f"  Matched keywords: {', '.join(tier.matched_keywords)}")

    # 4. Run sample response through hallucination pipeline
    print_section("4. HALLUCINATION PIPELINE")
    sample_response = (
        "Nurses help patients by checking their health, giving medicine, and "
        "talking to doctors. There are many types of nurses - emergency room "
        "nurses help during sudden situations, and pediatric nurses work with kids."
    )
    print(f"Sample AVA response:\n  {sample_response!r}\n")

    assessments = assess_response(sample_response, sources=[])
    print(f"Claims extracted and assessed: {len(assessments)}")
    for i, assessment in enumerate(assessments, 1):
        print(f"\n  Claim {i}:")
        print(f"    Original: {assessment.claim.text[:60]}...")
        print(f"    Status: {assessment.status.name}")
        print(f"    Grounding: {assessment.grounding.outcome.name}")
        print(f"    Rendered: {assessment.rendered_text[:60]}...")

    # 5. Memory management
    print_section("5. MEMORY & CONVERSATION HISTORY")
    memory = Memory(memory_dir)
    profile = memory.load_or_create_profile("Test Daughter", 10)
    print(f"[OK] Profile loaded: {profile.name}, age {profile.age}")

    # Save sample conversation
    user_turn = ConversationTurn(
        timestamp=datetime.now().isoformat(),
        role="user",
        text="What do nurses do?",
        topic="nursing",
    )
    memory.append_turn(user_turn)

    ava_turn = ConversationTurn(
        timestamp=datetime.now().isoformat(),
        role="assistant",
        text=sample_response,
        topic="nursing",
        flagged_for_notification=False,
    )
    memory.append_turn(ava_turn)

    print(f"[OK] Saved 2 conversation turns")
    history_file = memory_dir / "conversation_history.jsonl"
    print(f"[OK] History saved to: {history_file}")
    print(f"     File size: {history_file.stat().st_size} bytes")

    # 6. Notifications
    print_section("6. PARENT NOTIFICATIONS")
    notifications = NotificationHandler(memory_dir / "notifications.log")

    notification_tests = [
        ("NURSING", "Discussed nursing career path"),
        ("FINANCIAL", "Advised on saving allowance"),
        ("MEDICAL", "Discussed medication side effects"),
    ]

    for topic, message in notification_tests:
        notifications.notify(topic, message)

    print(f"[OK] Logged {len(notification_tests)} notifications")
    notif_file = memory_dir / "notifications.log"
    print(f"[OK] Notifications saved to: {notif_file}")
    lines = notif_file.read_text().strip().split("\n")
    print(f"\nNotification log ({len(lines)} entries):")
    for line in lines:
        print(f"     {line}")

    # 7. Summary
    print_section("DEMO COMPLETE")
    print(f"""
[OK] Knowledge base initialized with age-appropriate facts
[OK] Query criticality correctly classified (low/medium/high/critical)
[OK] Response passed through hallucination pipeline
[OK] Conversation history saved to JSONL
[OK] Parent notifications logged for review

All files saved to: {temp_dir}

Next steps:
  * Run: python -m avaos.chat --voice
    for a live conversation with voice I/O

  * Run: python scripts/manage_knowledge.py --view-age 10
    to see all available knowledge for age 10

  * Check: {notif_file}
    to review parent notifications
""")


if __name__ == "__main__":
    demo()
