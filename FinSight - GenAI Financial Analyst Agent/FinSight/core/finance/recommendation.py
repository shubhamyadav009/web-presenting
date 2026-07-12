from typing import Dict


class InvestmentRecommendation:
    """
    Generates Buy / Hold / Sell recommendation based on financial metrics
    """

    def __init__(self):
        pass

    # -------------------------------
    # Main Recommendation Function
    # -------------------------------
    def generate_recommendation(self, financials: Dict, ratios: Dict) -> Dict:
        """
        Input:
        financials: raw numbers
        ratios: calculated financial ratios

        Output:
        {
            "recommendation": "Buy",
            "confidence": "High",
            "reasoning": "Strong profitability, low debt..."
        }
        """

        score = 0
        reasoning = []

        profit_margin = ratios.get("profit_margin", 0)
        d2e = ratios.get("debt_to_equity", 0)
        roe = ratios.get("return_on_equity", 0)
        ebitda_margin = ratios.get("ebitda_margin", 0)

        # -------------------------------
        # Profitability Check
        # -------------------------------
        if profit_margin > 0.2:
            score += 2
            reasoning.append("Strong profitability with high profit margins.")
        elif profit_margin > 0.1:
            score += 1
            reasoning.append("Moderate profitability.")
        else:
            reasoning.append("Low profitability raises concerns.")

        # -------------------------------
        # Debt Check
        # -------------------------------
        if d2e < 1:
            score += 2
            reasoning.append("Low debt levels indicate financial stability.")
        elif d2e < 2:
            score += 1
            reasoning.append("Moderate leverage, manageable risk.")
        else:
            reasoning.append("High debt increases financial risk.")

        # -------------------------------
        # ROE Check
        # -------------------------------
        if roe > 0.2:
            score += 2
            reasoning.append("Strong return on equity indicates efficient capital use.")
        elif roe > 0.1:
            score += 1
            reasoning.append("Moderate return on equity.")
        else:
            reasoning.append("Low ROE suggests weak returns for investors.")

        # -------------------------------
        # EBITDA Margin Check
        # -------------------------------
        if ebitda_margin > 0.25:
            score += 2
            reasoning.append("High EBITDA margin shows strong operational efficiency.")
        elif ebitda_margin > 0.15:
            score += 1
            reasoning.append("Stable operational performance.")
        else:
            reasoning.append("Low EBITDA margin indicates inefficiencies.")

        # -------------------------------
        # Final Decision Logic
        # -------------------------------
        if score >= 6:
            recommendation = "Buy"
            confidence = "High"
        elif score >= 3:
            recommendation = "Hold"
            confidence = "Medium"
        else:
            recommendation = "Sell"
            confidence = "Low"

        return {
            "recommendation": recommendation,
            "confidence": confidence,
            "reasoning": " ".join(reasoning)
        }