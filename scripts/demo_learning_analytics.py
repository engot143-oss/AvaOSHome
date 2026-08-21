#!/usr/bin/env python3
"""
Demo of AVA OS learning analytics and tracking.

Shows:
- Recording topic discussions
- Tracking mastery levels
- Learning streaks
- Knowledge gaps
- Generating comprehensive reports
- Providing recommendations
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from avaos.learning_analytics import LearningAnalytics, format_learning_report
from avaos.memory import Memory


def print_section(title: str):
    """Print a formatted section header."""
    print(f"\n{'=' * 60}")
    print(f"  {title}")
    print(f"{'=' * 60}\n")


def demo():
    """Run the learning analytics demo."""
    import tempfile
    temp_dir = tempfile.TemporaryDirectory()
    temp_path = Path(temp_dir.name)
    memory_dir = temp_path / "memory"
    memory_dir.mkdir()

    print("\n*** AVA OS - Learning Analytics Demo ***\n")

    # Initialize
    memory = Memory(memory_dir)
    memory.load_or_create_profile("Sarah", 10)

    analytics = LearningAnalytics(memory_dir)

    # 1. Record discussions
    print_section("1. RECORD TOPIC DISCUSSIONS")
    discussions = [
        ("nursing", 5),
        ("nursing", 3),
        ("finance", 4),
        ("nursing", 6),
        ("life_skills", 2),
        ("finance", 3),
    ]

    for topic, messages in discussions:
        analytics.record_discussion(topic, messages)
        print(f"[OK] Recorded: {topic} ({messages} messages)")

    # 2. Set mastery levels
    print_section("2. SET MASTERY LEVELS")
    mastery = [("nursing", 3), ("finance", 2), ("life_skills", 1)]

    for topic, level in mastery:
        analytics.set_mastery(topic, level)
        print(f"[OK] {topic}: Level {level}/5")

    # 3. Show topic engagement
    print_section("3. TOPIC ENGAGEMENT")
    engagements = analytics.get_topic_engagement()

    for eng in engagements:
        print(f"\n{eng.topic.upper()}:")
        print(f"  Times discussed: {eng.times_discussed}")
        print(f"  Total messages: {eng.total_messages}")
        print(f"  Avg per discussion: {eng.messages_per_discussion:.1f}")

    # 4. Show mastery levels
    print_section("4. MASTERY LEVELS")
    mastery_levels = analytics.get_mastery_levels()

    for topic, level in sorted(mastery_levels.items()):
        bar = "[" + "=" * level + " " * (5 - level) + "]"
        print(f"{topic:15} {bar} Level {level}/5")

    # 5. Show learning streaks
    print_section("5. LEARNING STREAKS")
    streaks = analytics.get_learning_streaks()

    for topic, streak in sorted(streaks.items()):
        print(f"{topic}: {streak} day streak")

    # 6. Identify knowledge gaps
    print_section("6. KNOWLEDGE GAPS")
    all_topics = ["nursing", "finance", "life_skills", "school", "nutrition"]
    gaps = analytics.get_knowledge_gaps(all_topics)

    if gaps:
        print(f"Topics not yet discussed ({len(gaps)}):")
        for gap in gaps:
            print(f"  • {gap}")
    else:
        print("No knowledge gaps - all topics covered!")

    # 7. Generate comprehensive report
    print_section("7. LEARNING REPORT")
    report = analytics.generate_report(all_topics)
    formatted = format_learning_report(report)
    print(formatted)

    # 8. Get recommendations
    print_section("8. LEARNING RECOMMENDATIONS")
    recommendations = analytics.get_recommendations()

    if recommendations:
        for i, rec in enumerate(recommendations[:5], 1):
            print(f"{i}. {rec}")
    else:
        print("Keep up the great work!")

    # 9. Export analytics
    print_section("9. EXPORT ANALYTICS")
    export = analytics.export_analytics()

    print(f"Report Summary:")
    for key, value in export["report"].items():
        if isinstance(value, float):
            print(f"  {key}: {value * 100:.1f}%" if key == "learning_efficiency" else f"  {key}: {value:.1f}")
        else:
            print(f"  {key}: {value}")

    print(f"\nTopics in Export: {len(export['topics'])}")
    print(f"Recommendations: {len(export['recommendations'])}")

    print_section("DEMO COMPLETE")
    print("""
Learning Analytics Features:

1. **Topic Engagement** — Track how often topics are discussed
2. **Mastery Levels** — Rate proficiency in each topic (1-5)
3. **Learning Streaks** — Monitor consistency (daily learning)
4. **Knowledge Gaps** — Identify topics to focus on
5. **Learning Reports** — Comprehensive progress summaries
6. **Recommendations** — Personalized suggestions for improvement

Dashboard Integration:
- View all analytics in the "Analytics" tab
- See engagement metrics
- Track mastery progression
- Monitor learning streaks
- Get personalized recommendations

Export analytics as JSON for external analysis or record-keeping.
""")

    temp_dir.cleanup()


if __name__ == "__main__":
    demo()
