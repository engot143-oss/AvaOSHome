"""
Tests for faith and character curriculum.
"""

import json
import tempfile
from pathlib import Path
import sys

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

from avaos.faith_curriculum import FaithCurriculum


def test_faith_curriculum_initialization():
    """Test FaithCurriculum initializes correctly."""
    with tempfile.TemporaryDirectory() as tmpdir:
        memory_dir = Path(tmpdir)
        faith = FaithCurriculum(memory_dir)

        assert faith.memory_dir == memory_dir
        assert faith.progress_file == memory_dir / 'faith_progress.json'
        assert len(faith.FAITH_CURRICULUM) > 0


def test_get_lessons_for_age():
    """Test getting lessons for specific ages."""
    with tempfile.TemporaryDirectory() as tmpdir:
        memory_dir = Path(tmpdir)
        faith = FaithCurriculum(memory_dir)

        # Age 10 should have foundation lessons
        lessons_10 = faith.get_lessons_for_age(10)
        assert len(lessons_10) > 0
        assert lessons_10[0]['id'].startswith('faith-10-')

        # Age 12 should have character lessons
        lessons_12 = faith.get_lessons_for_age(12)
        assert len(lessons_12) > 0
        assert lessons_12[0]['id'].startswith('faith-12-')

        # Age 14 should have purpose lessons
        lessons_14 = faith.get_lessons_for_age(14)
        assert len(lessons_14) > 0
        assert lessons_14[0]['id'].startswith('faith-14-')


def test_record_prayer():
    """Test recording prayers."""
    with tempfile.TemporaryDirectory() as tmpdir:
        memory_dir = Path(tmpdir)
        faith = FaithCurriculum(memory_dir)

        faith.record_prayer("2026-08-19", "Gratitude")

        # Check prayer was recorded
        progress = faith.progress_data
        assert len(progress['daily_prayers']) > 0
        assert progress['daily_prayers'][0]['subject'] == 'Gratitude'


def test_record_reflection():
    """Test recording reflections."""
    with tempfile.TemporaryDirectory() as tmpdir:
        memory_dir = Path(tmpdir)
        faith = FaithCurriculum(memory_dir)

        reflection_text = "Today I saw God's love in helping my friend"
        faith.record_reflection(reflection_text, "How did I see God's love?")

        progress = faith.progress_data
        assert len(progress['reflections']) > 0
        assert progress['reflections'][0]['reflection'] == reflection_text


def test_record_value_demonstrated():
    """Test recording values demonstrated."""
    with tempfile.TemporaryDirectory() as tmpdir:
        memory_dir = Path(tmpdir)
        faith = FaithCurriculum(memory_dir)

        faith.record_value_demonstrated("integrity", "Told truth even when hard")

        progress = faith.progress_data
        assert len(progress['values_demonstrated']) > 0
        assert progress['values_demonstrated'][0]['value'] == 'integrity'


def test_daily_reflection_prompt():
    """Test getting daily reflection prompts."""
    with tempfile.TemporaryDirectory() as tmpdir:
        memory_dir = Path(tmpdir)
        faith = FaithCurriculum(memory_dir)

        prompt = faith.get_daily_reflection_prompt()
        assert isinstance(prompt, str)
        assert len(prompt) > 0
        assert prompt in faith.DAILY_REFLECTIONS


def test_spiritual_summary():
    """Test getting spiritual development summary."""
    with tempfile.TemporaryDirectory() as tmpdir:
        memory_dir = Path(tmpdir)
        faith = FaithCurriculum(memory_dir)

        # Record some activity
        faith.record_prayer("2026-08-19", "Gratitude")
        faith.record_value_demonstrated("kindness", "Helped sister")

        summary = faith.get_spiritual_summary(10)

        assert summary['current_age'] == 10
        assert summary['level'] == 'FOUNDATION'
        assert summary['prayers_this_month'] >= 1
        assert summary['values_demonstrated'] >= 1
        assert 'protective_factors' in summary
        assert 'today_reflection' in summary


def test_protective_factors():
    """Test assessment of protective factors against addiction."""
    with tempfile.TemporaryDirectory() as tmpdir:
        memory_dir = Path(tmpdir)
        faith = FaithCurriculum(memory_dir)

        # No activity yet
        summary = faith.get_spiritual_summary(10)
        factors = summary['protective_factors']

        assert factors['faith_foundation'] == False
        assert factors['prayer_practice'] == False
        assert factors['value_demonstration'] == False
        assert factors['overall_strength'] == 'Developing'

        # Add activity
        faith.record_prayer("2026-08-19", "Gratitude")
        faith.record_value_demonstrated("courage", "Stood up for friend")
        faith.record_value_demonstrated("integrity", "Told truth")

        summary = faith.get_spiritual_summary(10)
        factors = summary['protective_factors']

        # Note: Would be stronger with lessons and church attendance
        assert factors['prayer_practice'] == True
        assert factors['value_demonstration'] == True


def test_parent_report():
    """Test generating parent report."""
    with tempfile.TemporaryDirectory() as tmpdir:
        memory_dir = Path(tmpdir)
        faith = FaithCurriculum(memory_dir)

        report = faith.get_parent_report()

        assert isinstance(report, str)
        assert 'SPIRITUAL DEVELOPMENT REPORT' in report
        assert 'Protective Factors Against Addiction' in report
        assert 'Research Note' in report


def test_faith_curriculum_content_structure():
    """Test that faith curriculum has proper structure."""
    with tempfile.TemporaryDirectory() as tmpdir:
        memory_dir = Path(tmpdir)
        faith = FaithCurriculum(memory_dir)

        # Check each age has proper structure
        for age in [10, 12, 14, 16]:
            if age in faith.FAITH_CURRICULUM:
                curriculum = faith.FAITH_CURRICULUM[age]
                assert 'level' in curriculum
                assert 'topics' in curriculum

                # Each topic should have required fields
                for topic in curriculum['topics']:
                    assert 'id' in topic
                    assert 'title' in topic
                    assert 'description' in topic
                    assert 'key_lessons' in topic or 'practice' in topic or 'activity' in topic


def test_lesson_progression():
    """Test that lessons progress with age."""
    with tempfile.TemporaryDirectory() as tmpdir:
        memory_dir = Path(tmpdir)
        faith = FaithCurriculum(memory_dir)

        lessons_10 = faith.get_lessons_for_age(10)
        lessons_12 = faith.get_lessons_for_age(12)
        lessons_14 = faith.get_lessons_for_age(14)

        # Age 10 should focus on foundation
        assert any('God' in l['title'] or 'Prayer' in l['title'] for l in lessons_10)

        # Age 12 should focus on character
        assert any('Integrity' in l['title'] or 'Courage' in l['title'] for l in lessons_12)

        # Age 14 should focus on purpose and decisions
        assert any('Purpose' in l['title'] or 'Decision' in l['title'] for l in lessons_14)


def test_addiction_resistance_lesson():
    """Test that age-appropriate addiction resistance lessons exist."""
    with tempfile.TemporaryDirectory() as tmpdir:
        memory_dir = Path(tmpdir)
        faith = FaithCurriculum(memory_dir)

        # Age 12+ should have temptation resistance
        lessons_12 = faith.get_lessons_for_age(12)
        temptation_lessons = [l for l in lessons_12 if 'Temptation' in l['title']]
        assert len(temptation_lessons) > 0

        # Age 14+ should have addiction resistance
        lessons_14 = faith.get_lessons_for_age(14)
        addiction_lessons = [l for l in lessons_14 if 'Addiction' in l['title']]
        assert len(addiction_lessons) > 0


if __name__ == '__main__':
    test_faith_curriculum_initialization()
    test_get_lessons_for_age()
    test_record_prayer()
    test_record_reflection()
    test_record_value_demonstrated()
    test_daily_reflection_prompt()
    test_spiritual_summary()
    test_protective_factors()
    test_parent_report()
    test_faith_curriculum_content_structure()
    test_lesson_progression()
    test_addiction_resistance_lesson()

    print("All faith curriculum tests passed!")
