import sys
from pathlib import Path

# Allow running this test file directly (python test_finance.py) from nested paths.
if __package__ in (None, ""):
    project_root = Path(__file__).resolve().parents[2]
    if str(project_root) not in sys.path:
        sys.path.insert(0, str(project_root))

import pytest

from FinSight.core.finance.extractor import FinancialExtractor
from FinSight.core.finance.ratios import FinancialRatios
from FinSight.core.finance.insights import FinancialInsights
from FinSight.core.finance.recommendation import InvestmentRecommendation
from FinSight.core.finance.comparator import CompanyComparator


# -------------------------------
# Sample test data
# -------------------------------
@pytest.fixture
def sample_docs():
    return [
        {"content": "Total revenue was 1000 crore", "metadata": {"page": 1}},
        {"content": "Net profit after tax was 200 crore", "metadata": {"page": 2}},
        {"content": "Total debt is 500 crore", "metadata": {"page": 3}},
        {"content": "Total equity is 400 crore", "metadata": {"page": 4}},
        {"content": "EBITDA stood at 250 crore", "metadata": {"page": 5}},
    ]


# -------------------------------
# Test Financial Extraction
# -------------------------------
def test_financial_extraction(sample_docs):
    extractor = FinancialExtractor()
    financials = extractor.extract_financials(sample_docs)

    assert financials["revenue"] == 1000.0
    assert financials["profit"] == 200.0
    assert financials["debt"] == 500.0
    assert financials["equity"] == 400.0
    assert financials["ebitda"] == 250.0


# -------------------------------
# Test Ratio Calculation
# -------------------------------
def test_ratio_calculation():
    ratios_engine = FinancialRatios()

    financials = {
        "revenue": 1000,
        "profit": 200,
        "debt": 500,
        "equity": 400,
        "ebitda": 250
    }

    ratios = ratios_engine.calculate_ratios(financials)

    assert ratios["profit_margin"] == 0.2
    assert ratios["ebitda_margin"] == 0.25
    assert ratios["debt_to_equity"] == 1.25
    assert ratios["return_on_equity"] == 0.5


# -------------------------------
# Test Insights Generation
# -------------------------------
def test_insights_generation():
    insights_engine = FinancialInsights()

    financials = {
        "revenue": 1000,
        "profit": 250,
        "debt": 300,
        "equity": 400,
        "ebitda": 280
    }

    insights = insights_engine.generate_insights(financials)

    assert isinstance(insights, list)
    assert len(insights) > 0


# -------------------------------
# Test Recommendation Engine
# -------------------------------
def test_recommendation():
    rec_engine = InvestmentRecommendation()

    financials = {
        "revenue": 1000,
        "profit": 250,
        "debt": 300,
        "equity": 400,
        "ebitda": 280
    }

    ratios = {
        "profit_margin": 0.25,
        "debt_to_equity": 0.75,
        "return_on_equity": 0.3,
        "ebitda_margin": 0.28
    }

    result = rec_engine.generate_recommendation(financials, ratios)

    assert "recommendation" in result
    assert result["recommendation"] in ["Buy", "Hold", "Sell"]
    assert "confidence" in result
    assert "reasoning" in result


# -------------------------------
# Test Company Comparison
# -------------------------------
def test_comparator():
    comparator = CompanyComparator()

    company_a = {
        "name": "A",
        "revenue": 1000,
        "profit": 200,
        "debt": 500,
        "equity": 400,
        "ebitda": 250
    }

    company_b = {
        "name": "B",
        "revenue": 900,
        "profit": 220,
        "debt": 200,
        "equity": 500,
        "ebitda": 230
    }

    comparison = comparator.compare_metrics(company_a, company_b)

    assert "revenue" in comparison
    assert "profit" in comparison

    analysis = comparator.generate_analysis(comparison, "A", "B")
    verdict = comparator.final_verdict(comparison, "A", "B")

    assert isinstance(analysis, str)
    assert isinstance(verdict, str)