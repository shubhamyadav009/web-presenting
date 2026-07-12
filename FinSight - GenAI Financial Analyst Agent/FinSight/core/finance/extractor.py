import re
from typing import Dict, List


class FinancialExtractor:
    """
    Extracts key financial metrics from text chunks
    """

    def __init__(self) -> None:
        pass

    # -------------------------------
    # Public method
    # -------------------------------
    def extract_financials(self, documents: List[Dict]) -> Dict:
        """
        Input: List of document chunks from RAG

        Each document:
        {
            "content": "...",
            "metadata": {...}
        }

        Output:
        {
            "revenue": value,
            "profit": value,
            "debt": value,
            "equity": value,
            "ebitda": value
        }
        """

        combined_text: str = " ".join([doc.get("content", "") for doc in documents]).lower()

        financials: Dict[str, float] = {
            "revenue": self._extract_value(combined_text, ["revenue", "total income"]),
            "profit": self._extract_value(combined_text, ["net profit", "profit after tax"]),
            "debt": self._extract_value(combined_text, ["total debt", "borrowings"]),
            "equity": self._extract_value(combined_text, ["total equity", "shareholder equity"]),
            "ebitda": self._extract_value(combined_text, ["ebitda"])
        }

        return financials

    # -------------------------------
    # Core extraction logic
    # -------------------------------
    def _extract_value(self, text: str, keywords: List[str]) -> float:
        """
        Extracts numeric value based on keywords
        """

        for keyword in keywords:
            # Regex pattern to find numbers near keyword
            pattern: str = rf"{keyword}[^0-9₹$]*([\d,]+\.?\d*)"
            match: re.Match[str] | None = re.search(pattern, text)

            if match:
                value: str | re.Any = match.group(1)
                return self._clean_number(value)

        return 0.0  # default if not found

    # -------------------------------
    # Clean extracted number
    # -------------------------------
    def _clean_number(self, value: str) -> float:
        """
        Converts string numbers like '1,234.56' → float
        """

        try:
            value = value.replace(",", "")
            return float(value)
        except:
            return 0.0