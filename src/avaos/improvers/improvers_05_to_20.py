"""Framework Improvers #5-20 - Batch Implementation"""
from .framework_improver_template import BaseFrameworkImprover
from pathlib import Path


class KumonCurriculumImprover(BaseFrameworkImprover):
    """Framework #5: Kumon Curriculum"""
    def __init__(self, memory_dir: Path):
        super().__init__(5, "kumon_curriculum", memory_dir)


class SpacedRepetitionImprover(BaseFrameworkImprover):
    """Framework #6: Spaced Repetition"""
    def __init__(self, memory_dir: Path):
        super().__init__(6, "spaced_repetition", memory_dir)

    def analyze_performance(self):
        metrics = self.get_recent_metrics(100)
        if not metrics:
            return {'status': 'no_data'}

        successful_reviews = sum(1 for m in metrics if m.get('successful', False))
        forgotten = sum(1 for m in metrics if m.get('forgotten', False))
        total = len(metrics)

        return {
            'status': 'analyzed',
            'review_success_rate': successful_reviews / total if total > 0 else 0,
            'forgetting_rate': forgotten / total if total > 0 else 0,
        }


class FaithCurriculumImprover(BaseFrameworkImprover):
    """Framework #7: Faith & Character"""
    def __init__(self, memory_dir: Path):
        super().__init__(7, "faith_curriculum", memory_dir)


class FinancialLiteracyImprover(BaseFrameworkImprover):
    """Framework #8: Financial Literacy"""
    def __init__(self, memory_dir: Path):
        super().__init__(8, "financial_literacy", memory_dir)


class BudgetTrackerImprover(BaseFrameworkImprover):
    """Framework #9: Budget Tracker"""
    def __init__(self, memory_dir: Path):
        super().__init__(9, "budget_tracker", memory_dir)


class MemorySystemImprover(BaseFrameworkImprover):
    """Framework #10: Memory System"""
    def __init__(self, memory_dir: Path):
        super().__init__(10, "memory_system", memory_dir)


class SecurityMonitoringImprover(BaseFrameworkImprover):
    """Framework #11: Security Monitoring"""
    def __init__(self, memory_dir: Path):
        super().__init__(11, "security_monitoring", memory_dir)


class UncertaintyCommImprover(BaseFrameworkImprover):
    """Framework #12: Uncertainty Communication"""
    def __init__(self, memory_dir: Path):
        super().__init__(12, "uncertainty_communication", memory_dir)


class ClaimExtractorImprover(BaseFrameworkImprover):
    """Framework #13: Claim Extractor"""
    def __init__(self, memory_dir: Path):
        super().__init__(13, "claim_extractor", memory_dir)


class FactVerificationImprover(BaseFrameworkImprover):
    """Framework #14: Fact Verification"""
    def __init__(self, memory_dir: Path):
        super().__init__(14, "fact_verification", memory_dir)


class EncryptionImprover(BaseFrameworkImprover):
    """Framework #15: Encryption"""
    def __init__(self, memory_dir: Path):
        super().__init__(15, "encryption", memory_dir)


class PWAImprover(BaseFrameworkImprover):
    """Framework #16: PWA"""
    def __init__(self, memory_dir: Path):
        super().__init__(16, "pwa", memory_dir)


class ParentDashboardImprover(BaseFrameworkImprover):
    """Framework #17: Parent Dashboard"""
    def __init__(self, memory_dir: Path):
        super().__init__(17, "parent_dashboard", memory_dir)


class DiarySystemImprover(BaseFrameworkImprover):
    """Framework #18: Diary System"""
    def __init__(self, memory_dir: Path):
        super().__init__(18, "diary_system", memory_dir)


class CurriculumGeneratorImprover(BaseFrameworkImprover):
    """Framework #19: Curriculum Generator"""
    def __init__(self, memory_dir: Path):
        super().__init__(19, "curriculum_generator", memory_dir)


class APIServerImprover(BaseFrameworkImprover):
    """Framework #20: API Server"""
    def __init__(self, memory_dir: Path):
        super().__init__(20, "api_server", memory_dir)


# Registry of all improvers
ALL_IMPROVERS = {
    1: 'HallucinationPreventionImprover',
    2: 'SafetySystemImprover',
    3: 'LearningRecommendationsImprover',
    4: 'AdaptiveDifficultyImprover',
    5: 'KumonCurriculumImprover',
    6: 'SpacedRepetitionImprover',
    7: 'FaithCurriculumImprover',
    8: 'FinancialLiteracyImprover',
    9: 'BudgetTrackerImprover',
    10: 'MemorySystemImprover',
    11: 'SecurityMonitoringImprover',
    12: 'UncertaintyCommImprover',
    13: 'ClaimExtractorImprover',
    14: 'FactVerificationImprover',
    15: 'EncryptionImprover',
    16: 'PWAImprover',
    17: 'ParentDashboardImprover',
    18: 'DiarySystemImprover',
    19: 'CurriculumGeneratorImprover',
    20: 'APIServerImprover',
}
