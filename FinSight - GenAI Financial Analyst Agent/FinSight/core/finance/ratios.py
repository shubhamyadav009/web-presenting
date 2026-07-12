from typing import Dict


class FinancialRatios:
    """
    Calculates key financial ratios from extracted financial data
    """

    def __init__(self):
        pass

    # -------------------------------
    # Main function
    # -------------------------------
    def calculate_ratios(self, financials: Dict) -> Dict:
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
        {
            "profit_margin": 0.2,
            "ebitda_margin": 0.25,
            "debt_to_equity": 1.25,
            "return_on_equity": 0.5
        }
        """

        revenue = financials.get("revenue", 0)
        profit = financials.get("profit", 0)
        debt = financials.get("debt", 0)
        equity = financials.get("equity", 0)
        ebitda = financials.get("ebitda", 0)

        ratios = {}

        # -------------------------------
        # Profit Margin
        # -------------------------------
        ratios["profit_margin"] = self._safe_divide(profit, revenue)

        # -------------------------------
        # EBITDA Margin
        # -------------------------------
        ratios["ebitda_margin"] = self._safe_divide(ebitda, revenue)

        # -------------------------------
        # Debt-to-Equity Ratio
        # -------------------------------
        ratios["debt_to_equity"] = self._safe_divide(debt, equity)

        # -------------------------------
        # Return on Equity (ROE)
        # -------------------------------
        ratios["return_on_equity"] = self._safe_divide(profit, equity)

        return ratios

    # -------------------------------
    # Helper: Safe Division
    # -------------------------------
    def _safe_divide(self, numerator: float, denominator: float) -> float:
        """
        Prevent division by zero
        """
        try:
            if denominator == 0:
                return 0.0
            return round(numerator / denominator, 4)
        except:
            return 0.0