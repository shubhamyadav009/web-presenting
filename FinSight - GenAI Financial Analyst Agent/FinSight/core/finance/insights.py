from typing import Dict, List


class FinancialInsights:
    """
    Generates business insights from financial data
    """

    def __init__(self):
        pass

    # -------------------------------
    # Generate insights
    # -------------------------------
    def generate_insights(self, financials: Dict) -> List[str]:
        """
        Input:
        {
            "revenue": 1000,
            "profit": 200,
            "debt": 500,
            "equity": 400,
            "ebitda": 250
        }

        Output:
        [
            "Strong revenue performance...",
            "High debt risk...",
            ...
        ]
        """

        insights = []

        revenue = financials.get("revenue", 0)
        profit = financials.get("profit", 0)
        debt = financials.get("debt", 0)
        equity = financials.get("equity", 0)
        ebitda = financials.get("ebitda", 0)

        # -------------------------------
        # Profitability Insight
        # -------------------------------
        if revenue > 0:
            profit_margin = profit / revenue

            if profit_margin > 0.2:
                insights.append("The company demonstrates strong profitability with a high profit margin.")
            elif profit_margin > 0.1:
                insights.append("The company shows moderate profitability with stable margins.")
            else:
                insights.append("The company has low profitability, indicating potential cost or pricing challenges.")

        # -------------------------------
        # Debt Risk Insight
        # -------------------------------
        if equity > 0:
            d2e = debt / equity

            if d2e > 2:
                insights.append("The company has high financial leverage, indicating elevated risk.")
            elif d2e > 1:
                insights.append("The company has moderate leverage, which should be monitored.")
            else:
                insights.append("The company maintains a healthy debt position with low leverage.")

        # -------------------------------
        # EBITDA Performance
        # -------------------------------
        if revenue > 0:
            ebitda_margin = ebitda / revenue

            if ebitda_margin > 0.25:
                insights.append("Strong operational efficiency reflected in a high EBITDA margin.")
            elif ebitda_margin > 0.15:
                insights.append("Moderate operational efficiency with stable EBITDA margins.")
            else:
                insights.append("Low EBITDA margin suggests operational inefficiencies.")

        # -------------------------------
        # Growth Signal (Basic Heuristic)
        # -------------------------------
        if revenue > 0 and profit > 0:
            insights.append("The company is generating positive earnings, indicating a stable business model.")

        # -------------------------------
        # Edge Case
        # -------------------------------
        if not insights:
            insights.append("Insufficient data to generate meaningful insights.")

        return insights