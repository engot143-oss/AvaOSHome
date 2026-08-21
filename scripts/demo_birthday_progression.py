#!/usr/bin/env python3
"""
Demo of AVA OS birthday progression feature.

Shows:
- Setting a date of birth
- Detecting when birthday has passed
- Unlocking new age-appropriate facts
- Notifying parent of milestone
"""

import sys
from datetime import datetime, date, timedelta
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from avaos.memory import Memory
from avaos.knowledge import KnowledgeBase, INITIAL_FACTS
from avaos.age_progression import AgeProgression, format_birthday_notification, format_birthday_message


def print_section(title: str):
    """Print a formatted section header."""
    print(f"\n{'=' * 60}")
    print(f"  {title}")
    print(f"{'=' * 60}\n")


def demo():
    """Run the birthday progression demo."""
    # Setup temp directories
    import tempfile
    temp_dir = tempfile.TemporaryDirectory()
    temp_path = Path(temp_dir.name)
    memory_dir = temp_path / "memory"
    knowledge_dir = temp_path / "knowledge"
    memory_dir.mkdir()
    knowledge_dir.mkdir()

    print("\n*** AVA OS - Birthday Progression Demo ***\n")

    # 1. Initialize knowledge base
    print_section("1. KNOWLEDGE BASE")
    kb = KnowledgeBase(knowledge_dir)
    for fact in INITIAL_FACTS:
        kb.add_fact(fact)

    facts_10 = kb.get_facts_for_age(10)
    facts_11 = kb.get_facts_for_age(11)
    print(f"[OK] Knowledge base initialized")
    print(f"     Age 10: {len(facts_10)} facts")
    print(f"     Age 11: {len(facts_11)} facts")

    # 2. Create user profile with date of birth
    print_section("2. CREATE USER PROFILE WITH DATE OF BIRTH")
    memory = Memory(memory_dir)

    today = date.today()
    # Born 10 years ago, tomorrow (so birthday is tomorrow)
    birthday_tomorrow = date(today.year - 10, today.month, today.day) + timedelta(days=1)
    dob_str = birthday_tomorrow.isoformat()

    profile = memory.load_or_create_profile("Sarah", 10, date_of_birth=dob_str)
    print(f"[OK] Profile created")
    print(f"     Name: {profile.name}")
    print(f"     Current age: {profile.age}")
    print(f"     Date of birth: {profile.date_of_birth}")

    # 3. Check for birthday (before it happens)
    print_section("3. CHECK FOR BIRTHDAY (NOT YET)")
    progression = AgeProgression(memory_dir, knowledge_dir)
    milestone = progression.check_birthday(profile.name, profile.age, profile.date_of_birth)

    if milestone:
        print("[OK] Birthday detected!")
        print(f"     Old age: {milestone.old_age}")
        print(f"     New age: {milestone.new_age}")
        print(f"     New facts: {milestone.new_facts_available}")
    else:
        print("[OK] No birthday yet (or birthday is tomorrow)")

    # 4. Simulate birthday by creating profile with birthday in the past
    print_section("4. SIMULATE BIRTHDAY (CHANGE DOB)")
    today = date.today()
    # Born 10 years ago, yesterday (birthday already passed)
    birthday_yesterday = date(today.year - 10, today.month, today.day) - timedelta(days=1)
    dob_str_past = birthday_yesterday.isoformat()

    profile_past = memory.load_or_create_profile("Sarah", 10, date_of_birth=dob_str_past)
    print(f"[OK] Profile updated with past birthday")
    print(f"     Date of birth: {profile_past.date_of_birth}")

    # 5. Detect birthday
    print_section("5. DETECT BIRTHDAY")
    milestone = progression.check_birthday(profile_past.name, profile_past.age, profile_past.date_of_birth)

    if milestone:
        print("[OK] Birthday detected!")
        print(f"     Old age: {milestone.old_age}")
        print(f"     New age: {milestone.new_age}")
        print(f"     New facts available: {milestone.new_facts_available}")

        # 6. Get new facts
        print_section("6. NEW FACTS UNLOCKED")
        new_facts = progression.get_new_facts_for_age(milestone.old_age, milestone.new_age)

        if new_facts:
            print(f"[OK] {len(new_facts)} new facts unlocked:")
            for fact in new_facts[:5]:  # Show first 5
                print(f"     • {fact.title} (complexity: {fact.complexity.name})")
            if len(new_facts) > 5:
                print(f"     ... and {len(new_facts) - 5} more")
        else:
            print("[OK] No new facts at this age")

        # 7. Show notifications
        print_section("7. NOTIFICATIONS FOR PARENT")
        notif = format_birthday_notification(milestone)
        print(f"Parent notification:")
        print(f"  {notif}")

        # 8. Show birthday message to daughter
        print_section("8. BIRTHDAY MESSAGE FOR DAUGHTER")
        msg = format_birthday_message(milestone, new_facts)
        print(f"AVA says:")
        print(f"  {msg}")

        # 9. Show complexity progression
        print_section("9. KNOWLEDGE PROGRESSION BY COMPLEXITY")
        for topic in ["nursing", "finance"]:
            facts_at_age = progression.get_complexity_progression(topic, milestone.new_age)
            if facts_at_age:
                print(f"\n{topic.title()} (at age {milestone.new_age}):")
                for fact in facts_at_age[:2]:
                    print(f"  • {fact.title}")
                    print(f"    Complexity: {fact.complexity.name}")

    else:
        print("[OK] Birthday progression workflow complete")

    print_section("DEMO COMPLETE")
    print("""
How birthday progression works:

1. Parent sets daughter's date of birth when creating profile
2. At each login, AVA checks if birthday has passed
3. If birthday passed, age is incremented
4. New age-appropriate facts become available
5. Daughter is greeted with birthday message
6. Parent receives notification of milestone

This allows AVA to naturally mature with your daughter:
- Age 10: Simple explanations (nursing basics, allowance)
- Age 12: Intermediate explanations (nursing specialties, compound interest)
- Age 16+: Advanced explanations (nursing education, investment strategy)

Next time your daughter logs in after her birthday,
she'll automatically see more sophisticated content.
""")

    temp_dir.cleanup()


if __name__ == "__main__":
    demo()
