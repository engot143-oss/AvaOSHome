import json
import os
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Tuple

from avaos.adaptive_difficulty import AdaptiveDifficulty

KUMON_DATA_DIR = Path.home() / ".ava_os" / "kumon"
KUMON_DATA_DIR.mkdir(parents=True, exist_ok=True)

_adaptive = AdaptiveDifficulty(KUMON_DATA_DIR)

# Maps the adaptive engine's easy/medium/hard tiers onto our 1-3 levels
DIFFICULTY_TO_LEVEL = {"easy": 1, "medium": 2, "hard": 3}
LEVEL_TO_DIFFICULTY = {1: "easy", 2: "medium", 3: "hard"}

class KumonLesson:
    def __init__(self, level: int, subject: str, topic: str, questions: List[Dict]):
        self.level = level
        self.subject = subject  # "math" or "english"
        self.topic = topic
        self.questions = questions
        self.created_at = datetime.now().isoformat()

    def to_dict(self):
        return {
            "level": self.level,
            "subject": self.subject,
            "topic": self.topic,
            "questions": self.questions,
            "created_at": self.created_at
        }

class KumonExercise:
    def __init__(self, lesson_id: str, question_num: int, question: str, answer: str):
        self.lesson_id = lesson_id
        self.question_num = question_num
        self.question = question
        self.answer = answer
        self.user_answer: Optional[str] = None
        self.is_correct: Optional[bool] = None
        self.started_at = datetime.now().isoformat()
        self.completed_at: Optional[str] = None

    def submit_answer(self, user_answer: str) -> bool:
        self.user_answer = user_answer
        self.is_correct = self._check_answer(user_answer)
        self.completed_at = datetime.now().isoformat()
        return self.is_correct

    def _check_answer(self, user_answer: str) -> bool:
        return user_answer.strip().lower() == self.answer.strip().lower()

    def to_dict(self):
        return {
            "lesson_id": self.lesson_id,
            "question_num": self.question_num,
            "question": self.question,
            "user_answer": self.user_answer,
            "is_correct": self.is_correct,
            "started_at": self.started_at,
            "completed_at": self.completed_at,
            "time_taken_seconds": self._get_time_taken()
        }

    def _get_time_taken(self) -> Optional[float]:
        if self.started_at and self.completed_at:
            start = datetime.fromisoformat(self.started_at)
            end = datetime.fromisoformat(self.completed_at)
            return (end - start).total_seconds()
        return None

# Math exercises by level
MATH_EXERCISES = {
    1: {
        "Addition Basics": [
            {"q": "2 + 1", "a": "3"},
            {"q": "3 + 2", "a": "5"},
            {"q": "4 + 1", "a": "5"},
            {"q": "2 + 3", "a": "5"},
            {"q": "1 + 4", "a": "5"},
        ],
        "Subtraction Basics": [
            {"q": "5 - 2", "a": "3"},
            {"q": "4 - 1", "a": "3"},
            {"q": "5 - 3", "a": "2"},
            {"q": "3 - 1", "a": "2"},
        ]
    },
    2: {
        "Two-Digit Addition": [
            {"q": "10 + 5", "a": "15"},
            {"q": "12 + 8", "a": "20"},
            {"q": "15 + 10", "a": "25"},
            {"q": "20 + 5", "a": "25"},
        ],
        "Two-Digit Subtraction": [
            {"q": "15 - 5", "a": "10"},
            {"q": "20 - 8", "a": "12"},
            {"q": "25 - 10", "a": "15"},
        ]
    },
    3: {
        "Multiplication Basics": [
            {"q": "2 × 3", "a": "6"},
            {"q": "3 × 4", "a": "12"},
            {"q": "5 × 2", "a": "10"},
            {"q": "4 × 3", "a": "12"},
        ],
        "Three-Digit Addition": [
            {"q": "100 + 50", "a": "150"},
            {"q": "125 + 25", "a": "150"},
        ]
    }
}

# English exercises by level
ENGLISH_EXERCISES = {
    1: {
        "Sight Words": [
            {"q": "Spell: the", "a": "the"},
            {"q": "Spell: and", "a": "and"},
            {"q": "Spell: cat", "a": "cat"},
            {"q": "Spell: dog", "a": "dog"},
        ],
        "Simple Sentences": [
            {"q": "Complete: I am ___", "a": "happy"},
            {"q": "Complete: The cat is ___", "a": "black"},
        ]
    },
    2: {
        "Vocabulary": [
            {"q": "Spell: friend", "a": "friend"},
            {"q": "Spell: beautiful", "a": "beautiful"},
            {"q": "Spell: answer", "a": "answer"},
        ],
        "Reading Comprehension": [
            {"q": "What says 'moo'?", "a": "cow"},
            {"q": "What barks?", "a": "dog"},
        ]
    },
    3: {
        "Grammar": [
            {"q": "Choose: She ___ (go/goes)", "a": "goes"},
            {"q": "Choose: They ___ (is/are)", "a": "are"},
        ],
        "Punctuation": [
            {"q": "Is this a question? yes/no", "a": "no"},
        ]
    }
}

def get_lesson(subject: str, level: int, topic: str) -> Dict:
    """Get a lesson for the given subject, level, and topic."""
    if subject == "math":
        exercises = MATH_EXERCISES.get(level, {}).get(topic, [])
    elif subject == "english":
        exercises = ENGLISH_EXERCISES.get(level, {}).get(topic, [])
    else:
        return {}

    return {
        "subject": subject,
        "level": level,
        "topic": topic,
        "exercises": exercises,
        "total": len(exercises)
    }

def get_available_topics(subject: str, level: int) -> List[str]:
    """Get all available topics for a subject and level."""
    if subject == "math":
        topics = MATH_EXERCISES.get(level, {}).keys()
    elif subject == "english":
        topics = ENGLISH_EXERCISES.get(level, {}).keys()
    else:
        topics = []
    return list(topics)

MASTERY_ACCURACY_THRESHOLD = 0.6

def _topics_covered(progress: Dict, subject: str, level: int) -> set:
    """Topics at this level she's completed with at least a passing score."""
    return {
        lesson["topic"] for lesson in progress.get("completed_lessons", [])
        if lesson["subject"] == subject and lesson["level"] == level
        and lesson.get("total") and (lesson["score"] / lesson["total"]) >= MASTERY_ACCURACY_THRESHOLD
    }

def get_recommended_level(subject: str, progress: Optional[Dict] = None) -> int:
    """The level she should be practicing at.

    Driven by the adaptive engine's accuracy trend, but capped so she can't
    level up past a topic she's never actually attempted — advancing on one
    repeated easy topic while skipping the rest of the level isn't mastery.
    """
    _adaptive.initialize_concept(subject, subject)
    difficulty = _adaptive.get_current_difficulty(subject)
    adaptive_level = DIFFICULTY_TO_LEVEL.get(difficulty, 1)

    if progress is None:
        progress = load_progress()

    gated_level = 1
    for lvl in range(1, adaptive_level):
        required = set(get_available_topics(subject, lvl))
        covered = _topics_covered(progress, subject, lvl)
        if required and required.issubset(covered):
            gated_level = lvl + 1
        else:
            break

    return min(adaptive_level, gated_level)

def get_adaptive_summary(subject: str) -> Dict:
    """Trend/accuracy info for a subject, for the parent dashboard."""
    _adaptive.initialize_concept(subject, subject)
    summary = _adaptive.get_performance_summary(subject)
    summary["recommended_level"] = DIFFICULTY_TO_LEVEL.get(
        summary.get("current_difficulty", "easy"), 1
    )
    return summary

def load_progress() -> Dict:
    """Load student progress from disk."""
    progress_file = KUMON_DATA_DIR / "progress.json"
    if progress_file.exists():
        with open(progress_file) as f:
            return json.load(f)
    return {
        "current_subject": "math",
        "streak": 0,
        "last_activity": None,
        "completed_lessons": [],
        "total_correct": 0,
        "total_attempts": 0
    }

def get_all_levels() -> Dict[str, int]:
    """Adaptive-engine-recommended level for every subject, e.g. {'math': 2, 'english': 1}."""
    return {subject: get_recommended_level(subject) for subject in ("math", "english")}

def save_progress(progress: Dict):
    """Save student progress to disk."""
    progress_file = KUMON_DATA_DIR / "progress.json"
    with open(progress_file, "w") as f:
        json.dump(progress, f, indent=2)

def record_lesson_completion(subject: str, level: int, topic: str, score: int, total: int) -> Tuple[Dict, Optional[str]]:
    """Record that a lesson was completed. Returns (progress, level_change).

    level_change is "up" / "down" / None depending on how the adaptive
    engine reacted to this result — advancement requires several
    consistently strong lessons, not just one, matching Kumon's
    mastery-before-advancement approach.
    """
    progress = load_progress()

    _adaptive.initialize_concept(subject, subject)
    prev_level = get_recommended_level(subject, progress)

    today = datetime.now().date().isoformat()
    last_activity = progress.get("last_activity")

    # Update streak
    if last_activity == today:
        pass  # Already counted today
    elif last_activity == (datetime.now().date() - timedelta(days=1)).isoformat():
        progress["streak"] += 1
    else:
        progress["streak"] = 1

    progress["last_activity"] = today
    progress["total_correct"] += score
    progress["total_attempts"] += total
    progress["completed_lessons"].append({
        "subject": subject,
        "level": level,
        "topic": topic,
        "date": datetime.now().isoformat(),
        "score": score,
        "total": total
    })

    accuracy = score / total if total else 0
    _adaptive.record_performance(subject, accuracy)
    new_level = get_recommended_level(subject, progress)

    level_change = None
    if new_level > prev_level:
        level_change = "up"
    elif new_level < prev_level:
        level_change = "down"

    progress["current_subject"] = subject

    save_progress(progress)
    return progress, level_change
