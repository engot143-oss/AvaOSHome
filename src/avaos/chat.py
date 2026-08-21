"""
Simple chat interface for AVA OS - wires together the pipeline with voice I/O.

Handles:
1. User input (voice → text via SpeechRecognition)
2. AVA's response generation via Claude
3. Hallucination checking (extract claims, ground them, fallback check if needed)
4. Voice output (text → speech via pyttsx3)
5. Memory (conversation history + user profile)
6. Notifications (logs high-stakes advice for parent review)

Run with voice: python -m avaos.chat --voice
Run text-only: python -m avaos.chat
"""

from __future__ import annotations

import sys
from datetime import datetime
from pathlib import Path

import anthropic

from .criticality import classify as classify_criticality
from .evidence import Source, SourceType
from .fallback_check import run_fallback_check
from .knowledge import KnowledgeBase
from .knowledge_manager import initialize_knowledge_base
from .memory import Memory, ConversationTurn
from .pipeline import assess_response, resolve_fallback_checks
from .age_progression import AgeProgression, format_birthday_notification, format_birthday_message
from .learning_analytics import LearningAnalytics
from .safety import SafetyManager


SYSTEM_PROMPT = """\
You are AVA, a trusted AI guide for a 10-year-old girl learning about life, school, and financial responsibility.

Your role:
- Give honest, age-appropriate guidance on school (she wants to be a nurse), finances, and life skills
- Never make up facts or advice you're unsure about
- If you don't know something, say so clearly
- Be warm, encouraging, and treat her as an intelligent person

Topics you help with:
- School and career guidance (especially nursing)
- Financial literacy for kids (saving, budgeting, allowance, value of money)
- Life skills (friendships, managing emotions, time management, school stress)

Always be truthful. If something is uncertain, say "I'm not completely sure about this" rather than guess.
"""


class NotificationHandler:
    """Logs high-stakes advice for parent review."""

    def __init__(self, notification_file: Path):
        self.notification_file = notification_file
        self.notification_file.parent.mkdir(parents=True, exist_ok=True)

    def notify(self, topic: str, message: str) -> None:
        """Log a notification for the parent."""
        timestamp = datetime.now().isoformat()
        with open(self.notification_file, "a") as f:
            f.write(f"[{timestamp}] {topic}: {message}\n")


def get_user_input(voice_enabled: bool = False) -> str:
    """Get input from user (voice or text)."""
    if voice_enabled:
        try:
            import speech_recognition as sr

            recognizer = sr.Recognizer()
            with sr.Microphone() as source:
                print("[*] Listening...", end="", flush=True)
                audio = recognizer.listen(source, timeout=10)
                text = recognizer.recognize_google(audio)
                print(f"\r[OK] You: {text}")
                return text
        except Exception as e:
            print(f"[!] Voice input failed ({e}), please type instead:")
            return input("> ")
    else:
        return input("You: ")


def speak_response(text: str, voice_enabled: bool = False) -> None:
    """Output response via voice or text."""
    if voice_enabled:
        try:
            import pyttsx3

            engine = pyttsx3.init()
            engine.setProperty("rate", 150)  # slightly slower for clarity
            engine.say(text)
            engine.runAndWait()
        except Exception as e:
            print(f"[!] Voice output failed ({e})")
    print(f"\n[AVA] {text}\n")


def run_chat(
    user_name: str,
    user_age: int,
    memory_dir: Path = Path("~/.ava_os/memory").expanduser(),
    knowledge_dir: Path = Path("~/.ava_os/knowledge").expanduser(),
    voice_enabled: bool = False,
):
    """Main chat loop."""
    memory = Memory(memory_dir)
    kb = KnowledgeBase(knowledge_dir)
    notifications = NotificationHandler(memory_dir / "notifications.log")
    analytics = LearningAnalytics(memory_dir)
    client = anthropic.Anthropic()

    # Initialize knowledge base if needed
    if not knowledge_dir.joinpath("facts.jsonl").exists():
        print("[*] Initializing knowledge base on first run...")
        initialize_knowledge_base(knowledge_dir)

    # Initialize safety manager
    safety = SafetyManager(memory_dir)

    # Load or create profile
    profile = memory.load_or_create_profile(user_name, user_age)

    # Check for birthday progression
    age_progression = AgeProgression(memory_dir, knowledge_dir)
    milestone = age_progression.check_birthday(profile.name, profile.age, profile.date_of_birth)

    if milestone:
        # Birthday has passed - update age in profile
        new_profile = memory.update_profile(age=milestone.new_age)
        new_facts = age_progression.get_new_facts_for_age(milestone.old_age, milestone.new_age)

        # Show birthday message
        birthday_msg = format_birthday_message(milestone, new_facts)
        print(f"\n*** {birthday_msg} ***\n")

        # Log notification for parent
        notifications.notify("BIRTHDAY", format_birthday_notification(milestone))
        profile = new_profile

    print(f"Hi {profile.name}! I'm AVA. How can I help you today?\n")

    # Main loop
    while True:
        try:
            user_text = get_user_input(voice_enabled=voice_enabled)
            if user_text.lower() in ("exit", "quit", "bye"):
                print("Goodbye! Remember, you're doing great.")
                break

            # Validate message for safety
            is_safe, safety_msg = safety.validate_message(user_text)
            if not is_safe:
                print(f"[!] {safety_msg}")
                continue

            # Check if escalation to parent needed
            should_notify_parent = safety.should_escalate_to_parent(user_text)
            if should_notify_parent:
                notifications.notify(
                    "SAFETY_ESCALATION",
                    f"High-risk topic discussed: {user_text[:80]}"
                )

            # Classify the topic by checking criticality
            consequence_tier = classify_criticality(user_text)

            # Build messages for Claude (include recent context + knowledge base)
            recent = memory.recent_context(num_turns=6)
            kb_context = kb.build_context_for_age(user_age)

            system_with_kb = SYSTEM_PROMPT + "\n\n" + kb_context

            messages = [{"role": "user", "content": user_text}]
            if recent:
                messages = [{"role": "user", "content": f"Recent context:\n{recent}\n\nNew question: {user_text}"}]

            # Call Claude to generate AVA's response
            response = client.messages.create(
                model="claude-opus-5",
                max_tokens=500,
                system=system_with_kb,
                messages=messages,
            )
            ava_response = next(
                (b.text for b in response.content if b.type == "text"), ""
            )

            # Run through the hallucination pipeline
            assessments = assess_response(ava_response, sources=[])

            # For high-stakes claims, run fallback checks
            needs_check = [a for a in assessments if a.status.name == "NEEDS_FALLBACK_CHECK"]
            if needs_check:
                print("[*] Verifying claims with live search...", end="", flush=True)
                assessments = resolve_fallback_checks(
                    assessments, fallback_fn=run_fallback_check
                )
                print(" ✓")

            # Build final response from assessments
            final_response_lines = []
            for assessment in assessments:
                final_response_lines.append(assessment.rendered_text)
            final_response = " ".join(final_response_lines)

            # Check for notifications
            high_stakes_count = sum(
                1
                for a in assessments
                if a.status.name in ("NEEDS_FALLBACK_CHECK", "CONTRADICTED_LIVE", "UNVERIFIED_AFTER_LIVE_CHECK")
            )
            if high_stakes_count > 0:
                notifications.notify(
                    "CLAIM_VERIFICATION",
                    f"Response about '{user_text[:50]}...' contained high-stakes claims that needed verification",
                )

            # Parent notification for medical/financial advice
            if consequence_tier.tier.value >= 3:  # MEDIUM or higher
                notifications.notify(
                    consequence_tier.tier.name,
                    f"Advised on {consequence_tier.tier.name.lower()}-stakes topic: {user_text[:80]}",
                )

            # Record analytics
            topic = consequence_tier.tier.name.lower()
            analytics.record_discussion(topic, message_count=2)  # user + assistant

            # Save to memory
            memory.append_turn(
                ConversationTurn(
                    timestamp=datetime.now().isoformat(),
                    role="user",
                    text=user_text,
                    topic=topic,
                )
            )
            memory.append_turn(
                ConversationTurn(
                    timestamp=datetime.now().isoformat(),
                    role="assistant",
                    text=final_response,
                    topic=topic,
                    flagged_for_notification=high_stakes_count > 0,
                )
            )

            # Output response
            speak_response(final_response, voice_enabled=voice_enabled)

        except KeyboardInterrupt:
            print("\n\nGoodbye! 💙")
            break
        except Exception as e:
            print(f"⚠️  Error: {e}")
            notifications.notify("ERROR", str(e))


if __name__ == "__main__":
    voice = "--voice" in sys.argv
    run_chat("Daughter", age=10, voice_enabled=voice)
