#!/usr/bin/env python3
import json
import os
import sys
from flask import Flask, render_template, request, jsonify
from pathlib import Path
from datetime import datetime, timedelta

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from avaos.kumon_student import (
    get_lesson, get_available_topics, load_progress, save_progress,
    record_lesson_completion, get_recommended_level, get_all_levels,
    get_adaptive_summary, MATH_EXERCISES, ENGLISH_EXERCISES
)

app = Flask(__name__, template_folder=Path(__file__).parent.parent / "templates")
KUMON_DATA_DIR = Path.home() / ".ava_os" / "kumon"
KUMON_DATA_DIR.mkdir(parents=True, exist_ok=True)

# ============================================================================
# PARENT DASHBOARD ROUTES
# ============================================================================

@app.route("/parent")
def parent_dashboard():
    """Parent dashboard - view progress and assign lessons."""
    return render_template("parent_dashboard.html")

@app.route("/api/parent/progress")
def api_parent_progress():
    """Get student progress summary."""
    progress = load_progress()

    # Calculate stats
    total_correct = progress.get("total_correct", 0)
    total_attempts = progress.get("total_attempts", 0)
    accuracy = (total_correct / total_attempts * 100) if total_attempts > 0 else 0

    return jsonify({
        "levels": get_all_levels(),
        "current_subject": progress["current_subject"],
        "streak": progress["streak"],
        "total_correct": total_correct,
        "total_attempts": total_attempts,
        "accuracy": round(accuracy, 1),
        "last_activity": progress["last_activity"],
        "completed_lessons": progress["completed_lessons"][-10:]  # Last 10
    })

@app.route("/api/parent/adaptive")
def api_parent_adaptive():
    """Adaptive-difficulty trend per subject, for parent visibility."""
    return jsonify({
        "math": get_adaptive_summary("math"),
        "english": get_adaptive_summary("english")
    })

@app.route("/api/parent/analytics")
def api_parent_analytics():
    """Get detailed analytics for parent."""
    progress = load_progress()
    completed = progress.get("completed_lessons", [])

    # Group by date
    by_date = {}
    for lesson in completed:
        date = lesson["date"].split("T")[0]
        if date not in by_date:
            by_date[date] = []
        by_date[date].append(lesson)

    # Calculate by subject
    by_subject = {}
    for lesson in completed:
        subj = lesson["subject"]
        if subj not in by_subject:
            by_subject[subj] = {"total": 0, "correct": 0}
        by_subject[subj]["total"] += lesson["total"]
        by_subject[subj]["correct"] += lesson["score"]

    return jsonify({
        "by_date": by_date,
        "by_subject": by_subject,
        "total_lessons": len(completed),
        "streak": progress["streak"]
    })

@app.route("/api/parent/assignments", methods=["GET", "POST"])
def api_parent_assignments():
    """Get or create assignments."""
    assignments_file = KUMON_DATA_DIR / "assignments.json"

    if request.method == "GET":
        if assignments_file.exists():
            with open(assignments_file) as f:
                assignments = json.load(f)
        else:
            assignments = []
        return jsonify(assignments)

    elif request.method == "POST":
        data = request.get_json()

        if assignments_file.exists():
            with open(assignments_file) as f:
                assignments = json.load(f)
        else:
            assignments = []

        new_assignment = {
            "id": len(assignments) + 1,
            "subject": data["subject"],
            "level": data["level"],
            "topic": data["topic"],
            "created_at": datetime.now().isoformat(),
            "status": "pending"
        }
        assignments.append(new_assignment)

        with open(assignments_file, "w") as f:
            json.dump(assignments, f, indent=2)

        return jsonify(new_assignment), 201

# ============================================================================
# STUDENT DASHBOARD ROUTES
# ============================================================================

@app.route("/student")
def student_dashboard():
    """Student dashboard - learn and practice."""
    return render_template("student_dashboard.html")

@app.route("/api/student/progress")
def api_student_progress():
    """Get student's current progress, including the adaptive level per subject."""
    progress = load_progress()
    progress["levels"] = get_all_levels()
    return jsonify(progress)

@app.route("/api/student/lesson")
def api_student_lesson():
    """Get a lesson for the student. Level defaults to the adaptive recommendation."""
    subject = request.args.get("subject", "math")
    level = request.args.get("level", type=int) or get_recommended_level(subject)
    topic = request.args.get("topic")

    if not topic:
        topics = get_available_topics(subject, level)
        if topics:
            topic = topics[0]
        else:
            return jsonify({"error": "No topics available"}), 404

    lesson = get_lesson(subject, level, topic)
    if not lesson:
        return jsonify({"error": "Lesson not found"}), 404

    return jsonify(lesson)

@app.route("/api/student/topics")
def api_student_topics():
    """Get available topics for a subject at its adaptive level."""
    subject = request.args.get("subject", "math")
    level = request.args.get("level", type=int) or get_recommended_level(subject)

    topics = get_available_topics(subject, level)
    return jsonify({"topics": topics, "level": level})

@app.route("/api/student/submit-lesson", methods=["POST"])
def api_submit_lesson():
    """Submit lesson results. The adaptive engine decides whether to level up/down."""
    data = request.get_json()

    subject = data.get("subject")
    level = data.get("level")
    topic = data.get("topic")
    score = data.get("score", 0)
    total = data.get("total", 0)

    progress, level_change = record_lesson_completion(subject, level, topic, score, total)
    progress["levels"] = get_all_levels()

    return jsonify({
        "success": True,
        "progress": progress,
        "level_change": level_change,
        "new_level": progress["levels"][subject]
    })

# ============================================================================
# HOME ROUTE
# ============================================================================

@app.route("/")
def index():
    """Home page - choose student or parent."""
    return render_template("index.html")

if __name__ == "__main__":
    import io
    if sys.stdout.encoding and sys.stdout.encoding.lower() != "utf-8":
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
        sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8")

    port = int(os.environ.get("PORT", 5001))

    print("\n" + "="*60)
    print("KUMON LEARNING DASHBOARD")
    print("="*60)
    print(f"\nStudent Dashboard:  http://localhost:{port}/student")
    print(f"Parent Dashboard:   http://localhost:{port}/parent")
    print("\n" + "="*60 + "\n")

    app.run(host="0.0.0.0", port=port, debug=False, use_reloader=False)
