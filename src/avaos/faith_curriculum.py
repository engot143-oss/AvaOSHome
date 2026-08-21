"""
Faith and character development curriculum for AVA OS.

Age-progressive spiritual guidance:
- Age 10-11: Foundation (God, prayer, values, kindness)
- Age 12-14: Character (integrity, courage, wisdom, service)
- Age 15-17: Purpose (calling, life direction, resisting temptation)
- Age 18+: Discipleship (leading others, deep faith)

Research-backed outcomes:
- Kids with faith have lower addiction rates
- Regular prayer/reflection builds resilience
- Community (church) provides support network
- Values-based decisions improve life outcomes
"""

from __future__ import annotations

import json
from pathlib import Path
from datetime import datetime


class FaithCurriculum:
    """Manage faith and character development."""

    FAITH_CURRICULUM = {
        10: {
            'level': 'FOUNDATION',
            'topics': [
                {
                    'id': 'faith-10-01',
                    'title': 'God Loves You',
                    'description': 'God created you and loves you unconditionally. You are valued and special.',
                    'key_lessons': [
                        'You are made in God\'s image',
                        'God loves you no matter what',
                        'You can talk to God anytime',
                        'Prayer is a conversation with God'
                    ],
                    'daily_practice': 'Pray for 5 minutes: thank God, ask for help, say sorry if needed',
                    'activity': 'Write down 3 ways you feel God\'s love in your life'
                },
                {
                    'id': 'faith-10-02',
                    'title': 'The Bible is God\'s Word',
                    'description': 'The Bible teaches us how to live, what\'s right and wrong, and tells God\'s story.',
                    'key_lessons': [
                        'Bible is our guide for living',
                        'Stories show God\'s love through history',
                        'We can find answers in the Bible',
                        'Reading the Bible brings us closer to God'
                    ],
                    'daily_practice': 'Read one Bible verse a day (Psalms are good for kids)',
                    'activity': 'Find a Bible verse that means something to you'
                },
                {
                    'id': 'faith-10-03',
                    'title': 'Kindness and Helping Others',
                    'description': 'Jesus taught us to be kind and help others. This is how we show God\'s love.',
                    'key_lessons': [
                        'Kindness is powerful',
                        'Helping others pleases God',
                        'Small acts of kindness matter',
                        'Jesus always helped people'
                    ],
                    'activity': 'Do one act of kindness today - help a friend, family, or stranger'
                },
                {
                    'id': 'faith-10-04',
                    'title': 'Making Good Choices',
                    'description': 'God gives us wisdom to make good choices. Ask yourself: Would Jesus do this?',
                    'key_lessons': [
                        'God guides our choices',
                        'Right choices have good outcomes',
                        'Wrong choices have bad outcomes',
                        'Prayer helps us choose wisely'
                    ],
                    'activity': 'When facing a choice, ask: Is this kind? Is this right? Does it honor God?'
                }
            ]
        },
        12: {
            'level': 'CHARACTER',
            'topics': [
                {
                    'id': 'faith-12-01',
                    'title': 'Integrity - Doing Right When No One\'s Watching',
                    'description': 'Integrity means your actions match your values whether people see you or not.',
                    'key_lessons': [
                        'Integrity is your character foundation',
                        'Dishonesty always comes to light',
                        'People trust those with integrity',
                        'God always sees the truth'
                    ],
                    'examples': [
                        'Telling truth even if it costs you',
                        'Keeping promises when hard',
                        'Being honest about mistakes',
                        'Doing homework yourself (not cheating)'
                    ],
                    'activity': 'This week, choose integrity over convenience once. Notice how you feel.'
                },
                {
                    'id': 'faith-12-02',
                    'title': 'Courage - Standing for What\'s Right',
                    'description': 'Courage is not fearlessness - it\'s doing right even when afraid.',
                    'key_lessons': [
                        'Courage means facing fear for what\'s right',
                        'Peer pressure is normal but resistible',
                        'One person can make a difference',
                        'God gives us strength when we\'re afraid'
                    ],
                    'examples': [
                        'Saying no to friends pressuring you to do wrong',
                        'Standing up for someone being bullied',
                        'Admitting a mistake to authority',
                        'Doing something hard because it\'s right'
                    ],
                    'activity': 'Identify one area where you need courage. Pray for strength.'
                },
                {
                    'id': 'faith-12-03',
                    'title': 'Resisting Temptation and Bad Influences',
                    'description': 'Everyone faces temptation. Here\'s how to recognize and resist it.',
                    'key_lessons': [
                        'Temptation starts small',
                        'One bad choice makes the next easier',
                        'God gives us a way to escape temptation',
                        'True friends help you stay strong'
                    ],
                    'warning_signs': [
                        'Friends encouraging bad behavior',
                        'Secrets (if it\'s secret, it\'s probably wrong)',
                        'Feeling guilty before/after',
                        'Knowing you\'re disappointing God'
                    ],
                    'resistance_strategy': [
                        'Know your weaknesses',
                        'Avoid people/places that tempt you',
                        'Have accountability partners',
                        'Pray for strength',
                        'Remember the consequences'
                    ],
                    'activity': 'Identify your biggest temptation. Create an action plan to resist.'
                },
                {
                    'id': 'faith-12-04',
                    'title': 'Community and Church - You Need Others',
                    'description': 'Church and faith community provide support, accountability, and belonging.',
                    'key_lessons': [
                        'You\'re not meant to go through life alone',
                        'Church is your spiritual family',
                        'Community keeps you accountable',
                        'Shared faith strengthens individual faith'
                    ],
                    'benefits': [
                        'Friends with same values',
                        'Adults who care about you',
                        'Teaching and guidance',
                        'Support during hard times',
                        'Celebration during good times'
                    ],
                    'activity': 'If you go to church, talk to one new person. If not, visit one.'
                }
            ]
        },
        14: {
            'level': 'PURPOSE',
            'topics': [
                {
                    'id': 'faith-14-01',
                    'title': 'Your Unique Purpose and Calling',
                    'description': 'God created you for a reason. You have gifts and talents meant to be used.',
                    'key_lessons': [
                        'God has a plan for your life',
                        'Your gifts aren\'t accidents',
                        'Purpose grows as you mature',
                        'Following God\'s calling brings fulfillment'
                    ],
                    'reflection_questions': [
                        'What am I naturally good at?',
                        'What makes me come alive?',
                        'What problems do I want to solve?',
                        'How could my gifts help others?'
                    ],
                    'activity': 'Journal: What do you think God created you to do?'
                },
                {
                    'id': 'faith-14-02',
                    'title': 'Resisting Addiction and Destructive Behaviors',
                    'description': 'Addiction destroys futures. Faith and community help you stay free.',
                    'research': 'Studies show kids with strong faith/church have significantly lower addiction rates.',
                    'key_lessons': [
                        'Addiction is engineered to hook you',
                        'One choice can derail your future',
                        'Recovery is hard but possible',
                        'Faith provides strength and community support'
                    ],
                    'protective_factors': [
                        'Strong faith foundation',
                        'Active church community',
                        'Clear values and purpose',
                        'Accountability partners',
                        'Distance from bad influences',
                        'Healthy coping mechanisms'
                    ],
                    'activity': 'List your protective factors. Strengthen the weakest one.'
                },
                {
                    'id': 'faith-14-03',
                    'title': 'Making Life Decisions Through Faith',
                    'description': 'School, friends, future - use faith to guide major decisions.',
                    'key_lessons': [
                        'God wants what\'s best for you',
                        'Pray before major decisions',
                        'Seek wise counsel',
                        'Trust God even when uncertain'
                    ],
                    'decision_framework': [
                        'Does this align with God\'s values?',
                        'Would Jesus approve?',
                        'What would my faith mentors say?',
                        'Will this move me toward my purpose?',
                        'Am I at peace about this decision?'
                    ],
                    'activity': 'Apply this framework to a real decision you\'re facing.'
                }
            ]
        },
        16: {
            'level': 'DISCIPLESHIP',
            'topics': [
                {
                    'id': 'faith-16-01',
                    'title': 'Deep Faith and Personal Relationship with God',
                    'description': 'Move beyond habit to real, personal relationship with God.',
                    'key_lessons': [
                        'Faith becomes personal choice',
                        'Prayer deepens the relationship',
                        'Bible study reveals God\'s character',
                        'Your faith becomes your own'
                    ],
                    'practice': [
                        'Daily prayer (not just words)',
                        'Regular Bible study and reflection',
                        'Journaling your spiritual journey',
                        'Mentorship with older believers'
                    ]
                },
                {
                    'id': 'faith-16-02',
                    'title': 'Influencing Others - Being a Light',
                    'description': 'Your faith should inspire others. Show through example.',
                    'key_lessons': [
                        'Your life is a testimony',
                        'Quiet influence is powerful',
                        'Living well is witnessing',
                        'Invite others to faith community'
                    ],
                    'activity': 'Who in your life could benefit from knowing about your faith? Invite them.'
                }
            ]
        }
    }

    # Daily reflection prompts
    DAILY_REFLECTIONS = [
        'Who did I help today? How did that feel?',
        'Did I face any temptation? How did I handle it?',
        'What am I grateful for? Thank God for it.',
        'What was hard today? Pray for strength.',
        'Did I act with integrity? How?',
        'How did I see God\'s love today?',
        'Did I encourage anyone? How?',
        'What sin do I need to confess? Ask God\'s forgiveness.',
        'What did God teach me today?',
        'How can I serve someone tomorrow?'
    ]

    def __init__(self, memory_dir: Path):
        self.memory_dir = memory_dir
        self.progress_file = memory_dir / 'faith_progress.json'
        self.progress_data = self._load_or_create()

    def _load_or_create(self) -> dict:
        """Load or create faith progress tracking."""
        if self.progress_file.exists():
            with open(self.progress_file) as f:
                return json.load(f)
        else:
            return {
                'lessons_completed': [],
                'daily_prayers': [],
                'reflections': [],
                'values_demonstrated': [],
                'church_attendance': 0,
                'spiritual_growth': 'beginning'
            }

    def _save(self) -> None:
        """Save progress to disk."""
        self.progress_file.write_text(json.dumps(self.progress_data, indent=2))

    def get_lessons_for_age(self, age: int) -> list[dict]:
        """Get faith lessons appropriate for age."""
        curriculum = self.FAITH_CURRICULUM.get(age, {})
        return curriculum.get('topics', [])

    def record_prayer(self, prayer_date: str, subject: str) -> None:
        """Record a prayer."""
        self.progress_data['daily_prayers'].append({
            'date': prayer_date,
            'subject': subject,
            'recorded': datetime.now().isoformat()
        })
        self._save()

    def record_reflection(self, reflection_text: str, question: str = None) -> None:
        """Record a daily reflection."""
        self.progress_data['reflections'].append({
            'date': datetime.now().isoformat(),
            'reflection': reflection_text,
            'prompt': question
        })
        self._save()

    def record_value_demonstrated(self, value: str, description: str) -> None:
        """Record when she demonstrates a faith value."""
        self.progress_data['values_demonstrated'].append({
            'date': datetime.now().isoformat(),
            'value': value,  # integrity, courage, kindness, etc
            'description': description
        })
        self._save()

    def get_daily_reflection_prompt(self, day_of_year: int = None) -> str:
        """Get today's reflection prompt."""
        if day_of_year is None:
            day_of_year = datetime.now().timetuple().tm_yday

        index = (day_of_year - 1) % len(self.DAILY_REFLECTIONS)
        return self.DAILY_REFLECTIONS[index]

    def get_spiritual_summary(self, current_age: int) -> dict:
        """Get summary of spiritual development."""
        prayers_this_month = sum(
            1 for p in self.progress_data['daily_prayers']
            if datetime.fromisoformat(p['recorded']).month == datetime.now().month
        )

        values_count = len(self.progress_data['values_demonstrated'])

        return {
            'current_age': current_age,
            'level': self.FAITH_CURRICULUM.get(current_age, {}).get('level', 'UNKNOWN'),
            'lessons_completed': len(self.progress_data['lessons_completed']),
            'available_lessons': len(self.get_lessons_for_age(current_age)),
            'prayers_this_month': prayers_this_month,
            'values_demonstrated': values_count,
            'church_attendance': self.progress_data['church_attendance'],
            'spiritual_growth': self.progress_data['spiritual_growth'],
            'protective_factors': self._assess_protective_factors(),
            'today_reflection': self.get_daily_reflection_prompt()
        }

    def _assess_protective_factors(self) -> dict:
        """Assess protective factors against addiction."""
        prayers_this_month = sum(
            1 for p in self.progress_data['daily_prayers']
            if datetime.fromisoformat(p['recorded']).month == datetime.now().month
        )

        return {
            'faith_foundation': len(self.progress_data['lessons_completed']) > 0,
            'prayer_practice': prayers_this_month > 0,
            'value_demonstration': len(self.progress_data['values_demonstrated']) > 0,
            'church_community': self.progress_data['church_attendance'] > 0,
            'accountability': 'strong' if len(self.progress_data['reflections']) > 10 else 'developing',
            'overall_strength': 'Strong' if sum([
                len(self.progress_data['lessons_completed']) > 0,
                prayers_this_month > 0,
                len(self.progress_data['values_demonstrated']) > 0,
                self.progress_data['church_attendance'] > 0
            ]) >= 3 else 'Developing'
        }

    def get_parent_report(self) -> str:
        """Generate report for parent on spiritual development."""
        summary = self.get_spiritual_summary(10)

        report = f"""
SPIRITUAL DEVELOPMENT REPORT
============================

Current Stage: {summary['level']}
Lessons Completed: {summary['lessons_completed']}/{summary['available_lessons']}

This Month:
  - Prayers recorded: {summary['prayers_this_month']}
  - Values demonstrated: {summary['values_demonstrated']}
  - Church attendance: {summary['church_attendance']}

Protective Factors Against Addiction:
  ✓ Faith foundation: {'Yes' if summary['protective_factors']['faith_foundation'] else 'In progress'}
  ✓ Prayer practice: {'Yes' if summary['protective_factors']['prayer_practice'] else 'In progress'}
  ✓ Values demonstration: {'Yes' if summary['protective_factors']['value_demonstration'] else 'In progress'}
  ✓ Church community: {'Yes' if summary['protective_factors']['church_community'] else 'In progress'}
  ✓ Self-reflection: {summary['protective_factors']['accountability']}

Overall Spiritual Strength: {summary['protective_factors']['overall_strength']}

Research Note: Children with strong faith and regular church attendance show
significantly lower rates of substance abuse and destructive behaviors.

Next Steps:
  - Encourage daily prayer
  - Support church/faith community attendance
  - Help identify her spiritual gifts and purpose
  - Be present for conversations about values and decisions
"""
        return report
