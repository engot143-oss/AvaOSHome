"""
Interactive budget tracker for AVA OS.

Helps track:
- Income (allowance, jobs, gifts)
- Expenses (wants vs needs)
- Savings goals
- Rainy day fund
- 50/30/20 budget compliance
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from datetime import datetime, timedelta
from enum import Enum


class ExpenseCategory(Enum):
    """Categories of expenses."""
    FOOD = 'food'  # NEED
    TRANSPORTATION = 'transportation'  # NEED
    CLOTHING = 'clothing'  # NEED
    ENTERTAINMENT = 'entertainment'  # WANT
    SNACKS = 'snacks'  # WANT
    TOYS = 'toys'  # WANT
    GAMES = 'games'  # WANT
    SAVINGS = 'savings'  # SAVINGS
    RAINY_DAY = 'rainy_day'  # SAVINGS


class IncomeSource(Enum):
    """Sources of income."""
    ALLOWANCE = 'allowance'
    CHORES = 'chores'
    JOB = 'job'
    GIFT = 'gift'
    BIRTHDAY = 'birthday'


@dataclass
class Transaction:
    """A single income or expense transaction."""
    date: str
    type: str  # 'income' or 'expense'
    amount: float
    category: str
    description: str
    tags: list[str] = None


class BudgetTracker:
    """Track income, expenses, and budget compliance."""

    # Budget rules (in percentages)
    BUDGET_RULES = {
        'needs': 50,      # Food, shelter, clothing, transport
        'wants': 30,      # Entertainment, snacks, toys
        'savings': 20,    # Emergency fund and goals
        'rainy_day_min': 10  # Always keep 10% minimum for emergencies
    }

    # Expense categories classification
    CATEGORY_NEEDS = {ExpenseCategory.FOOD, ExpenseCategory.TRANSPORTATION, ExpenseCategory.CLOTHING}
    CATEGORY_WANTS = {ExpenseCategory.ENTERTAINMENT, ExpenseCategory.SNACKS, ExpenseCategory.TOYS, ExpenseCategory.GAMES}
    CATEGORY_SAVINGS = {ExpenseCategory.SAVINGS, ExpenseCategory.RAINY_DAY}

    def __init__(self, memory_dir: Path):
        self.memory_dir = memory_dir
        self.transactions_file = memory_dir / 'budget_transactions.jsonl'
        self.budget_file = memory_dir / 'budget_settings.json'
        self.budget_settings = self._load_settings()

    def _load_settings(self) -> dict:
        """Load budget settings."""
        if self.budget_file.exists():
            with open(self.budget_file) as f:
                return json.load(f)
        else:
            settings = {
                'monthly_income': 0.0,
                'created_date': datetime.now().isoformat(),
                'currency': 'USD'
            }
            self._save_settings(settings)
            return settings

    def _save_settings(self, settings: dict) -> None:
        """Save budget settings."""
        self.budget_file.write_text(json.dumps(settings, indent=2))

    def set_monthly_income(self, amount: float) -> None:
        """Set expected monthly income (allowance, job, etc)."""
        self.budget_settings['monthly_income'] = amount
        self._save_settings(self.budget_settings)

    def record_transaction(
        self,
        transaction_type: str,
        amount: float,
        category: str,
        description: str,
        date: str | None = None
    ) -> None:
        """Record an income or expense transaction."""
        if date is None:
            date = datetime.now().date().isoformat()

        transaction = {
            'date': date,
            'type': transaction_type,
            'amount': amount,
            'category': category,
            'description': description
        }

        with open(self.transactions_file, 'a') as f:
            f.write(json.dumps(transaction) + '\n')

    def get_transactions(self, days: int = 30) -> list[dict]:
        """Get recent transactions."""
        if not self.transactions_file.exists():
            return []

        cutoff = (datetime.now() - timedelta(days=days)).date().isoformat()
        transactions = []

        with open(self.transactions_file) as f:
            for line in f:
                if line.strip():
                    transaction = json.loads(line)
                    if transaction['date'] >= cutoff:
                        transactions.append(transaction)

        return sorted(transactions, key=lambda x: x['date'], reverse=True)

    def get_monthly_summary(self, month_offset: int = 0) -> dict:
        """Get spending summary for a month."""
        transactions = self.get_transactions(days=60)

        # Filter by target month
        now = datetime.now()
        target_month = (now - timedelta(days=30 * month_offset)).date()

        month_trans = [
            t for t in transactions
            if datetime.fromisoformat(t['date']).date().month == target_month.month
        ]

        # Calculate totals
        total_income = sum(t['amount'] for t in month_trans if t['type'] == 'income')
        total_needs = sum(t['amount'] for t in month_trans if t['type'] == 'expense' and t['category'] in [c.value for c in self.CATEGORY_NEEDS])
        total_wants = sum(t['amount'] for t in month_trans if t['type'] == 'expense' and t['category'] in [c.value for c in self.CATEGORY_WANTS])
        total_savings = sum(t['amount'] for t in month_trans if t['type'] == 'expense' and t['category'] in [c.value for c in self.CATEGORY_SAVINGS])
        total_expenses = total_needs + total_wants + total_savings

        # Calculate percentages
        needs_pct = (total_needs / total_income * 100) if total_income > 0 else 0
        wants_pct = (total_wants / total_income * 100) if total_income > 0 else 0
        savings_pct = (total_savings / total_income * 100) if total_income > 0 else 0

        return {
            'month': target_month.strftime('%B %Y'),
            'total_income': total_income,
            'total_expenses': total_expenses,
            'balance': total_income - total_expenses,
            'breakdown': {
                'needs': {
                    'amount': total_needs,
                    'percentage': needs_pct,
                    'budget': self.BUDGET_RULES['needs']
                },
                'wants': {
                    'amount': total_wants,
                    'percentage': wants_pct,
                    'budget': self.BUDGET_RULES['wants']
                },
                'savings': {
                    'amount': total_savings,
                    'percentage': savings_pct,
                    'budget': self.BUDGET_RULES['savings']
                }
            },
            'on_budget': {
                'needs': needs_pct <= self.BUDGET_RULES['needs'] + 5,
                'wants': wants_pct <= self.BUDGET_RULES['wants'] + 5,
                'savings': savings_pct >= self.BUDGET_RULES['savings'] - 5
            }
        }

    def check_budget_health(self) -> dict:
        """Check overall budget health."""
        summary = self.get_monthly_summary(month_offset=0)
        breakdown = summary['breakdown']
        on_budget = summary['on_budget']

        # Assess health
        if on_budget['needs'] and on_budget['wants'] and on_budget['savings']:
            health = 'excellent'
            advice = 'You\'re nailing the 50/30/20 budget! Keep it up!'
        elif on_budget['needs'] and (on_budget['wants'] or on_budget['savings']):
            health = 'good'
            advice = 'Good job! Slightly adjust wants/savings to match budget.'
        elif on_budget['needs']:
            health = 'fair'
            advice = 'You\'re covering needs but spending too much on wants. Dial it back!'
        else:
            health = 'poor'
            advice = 'You\'re spending more than you earn! Cut expenses immediately.'

        return {
            'health': health,
            'advice': advice,
            'summary': summary,
            'issues': [k for k, v in on_budget.items() if not v]
        }

    def get_spending_trends(self) -> dict:
        """Analyze spending trends."""
        last_3_months = [self.get_monthly_summary(month_offset=i) for i in range(3)]

        wants_trend = [m['breakdown']['wants']['amount'] for m in last_3_months]
        savings_trend = [m['breakdown']['savings']['amount'] for m in last_3_months]

        return {
            'months': [m['month'] for m in last_3_months],
            'wants_spending': wants_trend,
            'savings_trend': savings_trend,
            'wants_trending': 'up' if wants_trend[0] > wants_trend[-1] else 'down' if wants_trend[0] < wants_trend[-1] else 'stable',
            'savings_trending': 'up' if savings_trend[0] > savings_trend[-1] else 'down' if savings_trend[0] < savings_trend[-1] else 'stable'
        }

    def get_rainy_day_fund_status(self) -> dict:
        """Check rainy day fund status."""
        transactions = self.get_transactions(days=365)
        rainy_day_deposits = [
            t['amount'] for t in transactions
            if t['category'] == ExpenseCategory.RAINY_DAY.value and t['type'] == 'expense'
        ]

        total_fund = sum(rainy_day_deposits)
        total_income_yearly = sum(t['amount'] for t in transactions if t['type'] == 'income')
        months_of_expenses = total_fund / (total_income_yearly / 12) if total_income_yearly > 0 else 0

        return {
            'total_fund': total_fund,
            'goal': total_income_yearly * self.BUDGET_RULES['rainy_day_min'] / 100,
            'months_of_expenses': months_of_expenses,
            'healthy': total_fund >= (total_income_yearly * self.BUDGET_RULES['rainy_day_min'] / 100),
            'advice': 'Keep building!' if not total_fund >= (total_income_yearly * self.BUDGET_RULES['rainy_day_min'] / 100) else 'Great emergency fund!'
        }
