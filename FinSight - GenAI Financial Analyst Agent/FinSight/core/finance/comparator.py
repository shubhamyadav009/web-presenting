from typing import Dict, Any


class CompanyComparator:
    """
    Compares financial data between two companies
    """

    def __init__(self) -> None:
        pass

    # -------------------------------
    # Compare key financial metrics
    # -------------------------------
    def compare_metrics(self, company_a: Dict[str, Any], company_b: Dict[str, Any]) -> Dict:
        """
        Input format:
        {
            "name": "Company A",
            "revenue": 1000,
            "profit": 200,
            "debt": 500,
            "equity": 400,
            "ebitda": 250
        }
        """

        results = {}

        # Revenue comparison
        results["revenue"] = self._compare_values(
            company_a["revenue"], company_b["revenue"], higher_is_better=True
        )

        # Profit comparison
        results["profit"] = self._compare_values(
            company_a["profit"], company_b["profit"], higher_is_better=True
        )

        # Debt comparison (lower is better)
        results["debt"] = self._compare_values(
            company_a["debt"], company_b["debt"], higher_is_better=False
        )

        # EBITDA comparison
        results["ebitda"] = self._compare_values(
            company_a["ebitda"], company_b["ebitda"], higher_is_better=True
        )

        # Debt to Equity ratio
        d2e_a: Any | int = company_a["debt"] / company_a["equity"] if company_a["equity"] else 0
        d2e_b: Any | int = company_b["debt"] / company_b["equity"] if company_b["equity"] else 0

        results["debt_to_equity"] = self._compare_values(
            d2e_a, d2e_b, higher_is_better=False
        )

        return results

    # -------------------------------
    # Helper: Compare two values
    # -------------------------------
    def _compare_values(self, val_a, val_b, higher_is_better=True):
        if val_a == val_b:
            winner = "Tie"
        else:
            if higher_is_better:
                winner: str = "A" if val_a > val_b else "B"
            else:
                winner: str = "A" if val_a < val_b else "B"

        return {
            "company_a": val_a,
            "company_b": val_b,
            "winner": winner
        }

    # -------------------------------
    # Generate readable analysis
    # -------------------------------
    def generate_analysis(self, comparison: Dict, name_a: str, name_b: str) -> str:
        lines = []

        metric_names: Dict[str, str] = {
            "revenue": "Revenue",
            "profit": "Profit",
            "debt": "Debt",
            "ebitda": "EBITDA",
            "debt_to_equity": "Debt-to-Equity Ratio"
        }

        for key, result in comparison.items():
            metric: str | None = metric_names.get(key, key)

            if result["winner"] == "Tie":
                line: str = f"{metric}: Both companies perform equally."
            elif result["winner"] == "A":
                line: str = f"{metric}: {name_a} performs better."
            else:
                line: str = f"{metric}: {name_b} performs better."

            lines.append(line)

        return "\n".join(lines)

    # -------------------------------
    # Final verdict
    # -------------------------------
    def final_verdict(self, comparison: Dict, name_a: str, name_b: str) -> str:
        score_a = 0
        score_b = 0

        for result in comparison.values():
            if result["winner"] == "A":
                score_a += 1
            elif result["winner"] == "B":
                score_b += 1

        if score_a > score_b:
            return f"{name_a} is financially stronger overall."
        elif score_b > score_a:
            return f"{name_b} is financially stronger overall."
        else:
            return "Both companies show similar financial performance."