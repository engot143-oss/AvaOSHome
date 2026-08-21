"""
AVA OS Framework Improvers - Auto-optimization engines for all 20 frameworks.

Each improver monitors its framework and automatically improves it.
"""

# Improver registry
IMPROVERS = {
    1: 'improver_01_hallucination.HallucinationPreventionImprover',
    2: 'improver_02_safety.SafetySystemImprover',
    3: 'improver_03_recommendations.LearningRecommendationsImprover',
    4: 'improver_04_adaptive_difficulty.AdaptiveDifficultyImprover',
    5: 'improver_05_kumon.KumonCurriculumImprover',
    6: 'improver_06_spaced_rep.SpacedRepetitionImprover',
    7: 'improver_07_faith.FaithCurriculumImprover',
    8: 'improver_08_financial.FinancialLiteracyImprover',
    9: 'improver_09_budget.BudgetTrackerImprover',
    10: 'improver_10_memory.MemorySystemImprover',
    11: 'improver_11_security.SecurityMonitoringImprover',
    12: 'improver_12_uncertainty.UncertaintyCommImprover',
    13: 'improver_13_claim_extractor.ClaimExtractorImprover',
    14: 'improver_14_fact_verification.FactVerificationImprover',
    15: 'improver_15_encryption.EncryptionImprover',
    16: 'improver_16_pwa.PWAImprover',
    17: 'improver_17_dashboard.ParentDashboardImprover',
    18: 'improver_18_diary.DiarySystemImprover',
    19: 'improver_19_curriculum_gen.CurriculumGeneratorImprover',
    20: 'improver_20_api_server.APIServerImprover',
}
