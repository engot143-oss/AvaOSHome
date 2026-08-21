"""
Financial literacy curriculum for AVA OS.

Progressive money education from age 10-18:
- Age 10-11: Money basics, earning allowance, simple saving
- Age 12-14: Budgeting, rainy day funds, delayed gratification
- Age 15-17: Banking, compound interest, financial goals
- Age 18+: Investing, credit, financial independence

Core values:
- Don't live above your means
- Always save for rainy days
- Earn money through hard work
- Delayed gratification > impulse spending
"""

from __future__ import annotations

import json
from pathlib import Path
from datetime import datetime


class FinancialLiteracy:
    """Manage financial education curriculum."""

    # Age-progressive financial lessons
    FINANCIAL_CURRICULUM = {
        10: {
            'level': 'BEGINNER',
            'topics': [
                {
                    'id': 'finance-10-01',
                    'title': 'What is Money?',
                    'description': 'Money is a tool for trading. Instead of bartering (trading chickens for apples), we use money to buy things we need.',
                    'key_lessons': [
                        'Money has value',
                        'We trade money for goods and services',
                        'Money comes from doing work'
                    ],
                    'activity': 'Think of 5 things money can buy and why you need them'
                },
                {
                    'id': 'finance-10-02',
                    'title': 'Earning Money - Allowance',
                    'description': 'You can earn money by doing chores or jobs. This teaches responsibility and the value of hard work.',
                    'key_lessons': [
                        'Work = money',
                        'Everyone starts with small jobs',
                        'Allowance is earned, not given'
                    ],
                    'activity': 'List chores you can do to earn allowance'
                },
                {
                    'id': 'finance-10-03',
                    'title': 'Saving vs Spending',
                    'description': 'Not all money should be spent right away. Saving money means keeping some for later.',
                    'key_lessons': [
                        'Save before you spend',
                        'Waiting = better purchases',
                        'Savings = security'
                    ],
                    'activity': 'Divide $20 allowance: how much to save vs spend?'
                },
                {
                    'id': 'finance-10-04',
                    'title': 'The Rainy Day Fund',
                    'description': 'Bad things happen sometimes (lost toy, needed medicine, etc). A rainy day fund is money saved for emergencies.',
                    'key_lessons': [
                        'Emergencies happen to everyone',
                        'Prepare now for unexpected costs',
                        'Rainy day fund = peace of mind',
                        'Never touch this money unless truly needed'
                    ],
                    'activity': 'What emergencies might need money? Build your rainy day fund.'
                }
            ]
        },
        12: {
            'level': 'INTERMEDIATE',
            'topics': [
                {
                    'id': 'finance-12-01',
                    'title': 'Living Within Your Means',
                    'description': 'The most important rule: spend only what you earn. Living above your means means buying things you can\'t afford - this leads to debt and stress.',
                    'key_lessons': [
                        'Income: money you earn',
                        'Expenses: money you spend',
                        'Income should be MORE than expenses',
                        'Debt = borrowed money you must repay with interest',
                        'Living above means = financial stress'
                    ],
                    'example': 'If you earn $50/month, spend max $40, save $10 for rainy days',
                    'activity': 'Create a personal budget with income and expenses'
                },
                {
                    'id': 'finance-12-02',
                    'title': 'Wants vs Needs',
                    'description': 'Needs are essential (food, shelter, basics). Wants are nice to have but not necessary.',
                    'key_lessons': [
                        'Needs = food, home, clothes, school supplies',
                        'Wants = games, toys, candy, latest phone',
                        'Priority: needs THEN wants',
                        'Budget first for needs, then wants'
                    ],
                    'activity': 'List 10 things you want - now rank which are needs vs wants'
                },
                {
                    'id': 'finance-12-03',
                    'title': 'Delayed Gratification',
                    'description': 'Waiting to buy something is harder than buying it now. But waiting teaches discipline and often leads to better choices.',
                    'key_lessons': [
                        'Impulse buying = poor choices',
                        'Wait 1 week before big purchases',
                        'Ask yourself: "Do I really need this?"',
                        'Often you\'ll be glad you waited'
                    ],
                    'activity': 'Pick something you want to buy. Wait 1 week. Do you still want it?'
                },
                {
                    'id': 'finance-12-04',
                    'title': 'The 50/30/20 Rule',
                    'description': 'A simple budgeting method: 50% needs, 30% wants, 20% savings',
                    'key_lessons': [
                        '50% of income for NEEDS (food, home, etc)',
                        '30% for WANTS (entertainment, non-essentials)',
                        '20% for SAVINGS (emergency fund, goals)',
                        'This keeps you financially healthy'
                    ],
                    'example': 'Earn $100 → $50 needs, $30 wants, $20 savings',
                    'activity': 'Apply 50/30/20 to your allowance or part-time job earnings'
                }
            ]
        },
        14: {
            'level': 'INTERMEDIATE',
            'topics': [
                {
                    'id': 'finance-14-01',
                    'title': 'Banking 101',
                    'description': 'Banks help you save and grow your money safely.',
                    'key_lessons': [
                        'Savings account = safe place for money',
                        'Checking account = for daily spending',
                        'Interest = bank pays you for keeping money there',
                        'Debit card = spend money you have'
                    ],
                    'activity': 'Open a youth savings account at a bank'
                },
                {
                    'id': 'finance-14-02',
                    'title': 'Interest and Compound Growth',
                    'description': 'Money in savings accounts earns interest. Interest earns interest. This is how wealth grows.',
                    'key_lessons': [
                        'Interest = money banks pay you for saving',
                        'Compound interest = interest on interest',
                        'Small amounts grow big over time',
                        'Start saving young = more growth'
                    ],
                    'example': '$100 at 2% interest/year becomes $102 after 1 year, then $104.04...',
                    'activity': 'Calculate how $100 grows over 10 years at 2% interest'
                },
                {
                    'id': 'finance-14-03',
                    'title': 'Setting Financial Goals',
                    'description': 'Decide what you want to save for and make a plan to reach it.',
                    'key_lessons': [
                        'Goals = clear targets for savings',
                        'Short-term (1 year): new bike, gaming system',
                        'Long-term (5+ years): college, first car',
                        'Write down goals and track progress'
                    ],
                    'activity': 'Set 3 financial goals: short, medium, long-term'
                }
            ]
        },
        16: {
            'level': 'ADVANCED',
            'topics': [
                {
                    'id': 'finance-16-01',
                    'title': 'Credit and Debt',
                    'description': 'Credit is borrowed money. It must be repaid with interest. Good credit = financial opportunity.',
                    'key_lessons': [
                        'Credit card = borrowed money',
                        'Interest = cost of borrowing',
                        'Credit score = your financial reputation',
                        'Good credit = lower interest rates',
                        'Avoid debt when possible'
                    ],
                    'warning': 'Credit card debt is easy to get into and hard to escape',
                    'activity': 'Research credit scores and understand what affects them'
                },
                {
                    'id': 'finance-16-02',
                    'title': 'Part-Time Jobs and Taxes',
                    'description': 'Working part-time teaches responsibility and money skills. Taxes take a portion of earnings.',
                    'key_lessons': [
                        'Net pay = money after taxes',
                        'Taxes pay for schools, roads, services',
                        'W-4 and paycheck stubs',
                        'Save for taxes if self-employed'
                    ],
                    'activity': 'Get a part-time job and understand your first paycheck'
                },
                {
                    'id': 'finance-16-03',
                    'title': 'Investing Basics',
                    'description': 'Making your money work for you through stocks and bonds.',
                    'key_lessons': [
                        'Stock = owning part of a company',
                        'Bond = loan to government/company',
                        'Diversification = don\'t put all eggs in one basket',
                        'Time = your biggest investing advantage'
                    ],
                    'activity': 'Research beginner investing apps and paper trade'
                }
            ]
        },
        18: {
            'level': 'ADVANCED',
            'topics': [
                {
                    'id': 'finance-18-01',
                    'title': 'College Costs and Student Loans',
                    'description': 'Understanding the cost of college and how to minimize student debt.',
                    'key_lessons': [
                        'College costs vary wildly ($20k - $80k+/year)',
                        'Scholarships = free money (apply!)',
                        'Student loans = must be repaid',
                        'In-state college = cheaper',
                        'Community college first = save money'
                    ],
                    'activity': 'Research college costs and scholarship options'
                },
                {
                    'id': 'finance-18-02',
                    'title': 'Building Wealth',
                    'description': 'The long-term path to financial independence.',
                    'key_lessons': [
                        'Wealth = assets - liabilities',
                        'Income > Expenses = wealth building',
                        'Invest early and often',
                        'Compound interest is your friend',
                        'Financial independence = freedom'
                    ],
                    'activity': 'Create a 10-year wealth building plan'
                }
            ]
        }
    }

    # Core family values
    FAMILY_VALUES = {
        'living_within_means': 'We only spend what we earn. Never borrow to show off.',
        'rainy_day_fund': 'Always have emergency savings. Bad things happen to everyone.',
        'hard_work': 'Money comes from work, not luck or gifts. Earn it.',
        'delayed_gratification': 'Wait before buying. Often you\'ll change your mind.',
        'financial_security': 'Money = freedom and options. Build it patiently.',
    }

    def __init__(self, memory_dir: Path):
        self.memory_dir = memory_dir
        self.progress_file = memory_dir / 'financial_progress.json'
        self.progress_data = self._load_or_create()

    def _load_or_create(self) -> dict:
        """Load or create financial progress tracking."""
        if self.progress_file.exists():
            with open(self.progress_file) as f:
                return json.load(f)
        else:
            return {
                'lessons_completed': [],
                'goals': [],
                'rainy_day_fund': 0.0,
                'savings_total': 0.0,
                'milestones': [],
                'family_values_learned': set()
            }

    def _save(self) -> None:
        """Save progress to disk."""
        self.progress_file.write_text(json.dumps(self.progress_data, indent=2, default=str))

    def get_lessons_for_age(self, age: int) -> list[dict]:
        """Get financial lessons appropriate for age."""
        curriculum = self.FINANCIAL_CURRICULUM.get(age, {})
        return curriculum.get('topics', [])

    def complete_lesson(self, lesson_id: str, age: int) -> None:
        """Mark a lesson as completed."""
        self.progress_data['lessons_completed'].append({
            'lesson_id': lesson_id,
            'age': age,
            'completed_date': datetime.now().isoformat()
        })
        self._save()

    def set_financial_goal(self, goal_name: str, amount: float, months_to_save: int) -> None:
        """Add a financial goal."""
        self.progress_data['goals'].append({
            'name': goal_name,
            'target_amount': amount,
            'months_to_save': months_to_save,
            'monthly_savings': amount / months_to_save,
            'created_date': datetime.now().isoformat(),
            'progress': 0.0
        })
        self._save()

    def update_rainy_day_fund(self, amount: float) -> None:
        """Update rainy day fund balance."""
        self.progress_data['rainy_day_fund'] += amount
        self._save()

    def get_financial_summary(self, current_age: int) -> dict:
        """Get comprehensive financial education summary."""
        return {
            'current_age': current_age,
            'lessons_completed': len(self.progress_data['lessons_completed']),
            'available_lessons': len(self.get_lessons_for_age(current_age)),
            'rainy_day_fund': self.progress_data['rainy_day_fund'],
            'total_savings': self.progress_data['savings_total'],
            'goals': self.progress_data['goals'],
            'family_values': self.FAMILY_VALUES,
            'next_lesson': self._get_next_lesson(current_age),
            'milestones_reached': self.progress_data['milestones']
        }

    def _get_next_lesson(self, age: int) -> dict | None:
        """Get the next uncompleted lesson for age."""
        lessons = self.get_lessons_for_age(age)
        completed_ids = {l['lesson_id'] for l in self.progress_data['lessons_completed']}

        for lesson in lessons:
            if lesson['id'] not in completed_ids:
                return lesson

        return None

    def get_family_value_lesson(self, value_key: str) -> str:
        """Get explanation of a family financial value."""
        return self.FAMILY_VALUES.get(value_key, '')
