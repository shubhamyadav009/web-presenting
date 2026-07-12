"""
helpers.py

Utility/helper functions for FinSight - GenAI Financial Analyst Agent.
Includes text processing, validation, financial parsing, and logging helpers.
"""

import re
import logging
import sys
from pathlib import Path
from typing import List, Dict, Any

# Allow running this module directly (python helpers.py) from nested paths.
if __package__ in (None, ""):
    project_root: Path = Path(__file__).resolve().parents[2]
    if str(project_root) not in sys.path:
        sys.path.insert(0, str(project_root))

from FinSight.utils.constants import (
    ERROR_EMPTY_QUERY,
    FINANCIAL_KEYWORDS,
    MIN_RESPONSE_LENGTH,
    MAX_RESPONSE_LENGTH,
)

# ----------------------------
# Logging Setup
# ----------------------------

logger: logging.Logger = logging.getLogger(__name__)


# ----------------------------
# Input Validation
# ----------------------------

def validate_query(query: str) -> None:
    """
    Validates user query input.
    Raises ValueError if invalid.
    """
    if not query or not query.strip():
        logger.error("Empty query received.")
        raise ValueError(ERROR_EMPTY_QUERY)


# ----------------------------
# Text Cleaning
# ----------------------------

def clean_text(text: str) -> str:
    """
    Cleans text by removing extra spaces and special characters.
    """
    if not text:
        return ""

    text = re.sub(r"\s+", " ", text)  # remove extra whitespace
    text = text.strip()

    return text


# ----------------------------
# Context Formatter (RAG)
# ----------------------------

def format_documents(docs: List[Dict[str, Any]]) -> str:
    """
    Converts retrieved documents into a single context string.
    """
    if not docs:
        return ""

    return "\n".join([doc.get("page_content", "") for doc in docs])


# ----------------------------
# Financial Keyword Detection
# ----------------------------

def extract_financial_keywords(text: str) -> List[str]:
    """
    Extracts financial keywords present in text.
    """
    text_lower: str = text.lower()
    return [kw for kw in FINANCIAL_KEYWORDS if kw in text_lower]


# ----------------------------
# Response Validation
# ----------------------------

def validate_response(response: str) -> bool:
    """
    Validates LLM response quality based on length.
    """
    if not response:
        return False

    length: int = len(response)

    return MIN_RESPONSE_LENGTH <= length <= MAX_RESPONSE_LENGTH


# ----------------------------
# Basic Grounding Check
# ----------------------------

def check_grounding(response: str, context: str) -> bool:
    """
    Checks if response is grounded in context (basic overlap check).
    """
    if not response or not context:
        return False

    response_words: set[str] = set(response.lower().split())
    context_words: set[str] = set(context.lower().split())

    overlap: set[str] = response_words.intersection(context_words)

    return len(overlap) > 0


# ----------------------------
# Financial Number Extraction
# ----------------------------

def extract_numbers(text: str) -> List[float]:
    """
    Extracts numerical values from financial text.
    """
    numbers: List[Any] = re.findall(r"\d+\.?\d*", text)
    return [float(num) for num in numbers]


# ----------------------------
# Simple Financial Insight Generator
# ----------------------------

def generate_basic_insight(text: str) -> str:
    """
    Generates a basic financial insight based on keywords.
    """
    keywords: List[str] = extract_financial_keywords(text)

    if not keywords:
        return "No significant financial indicators detected."

    return f"Key financial aspects identified: {', '.join(keywords)}."


# ----------------------------
# Safe LLM Call Wrapper
# ----------------------------

def safe_llm_call(llm, prompt: str) -> str:
    """
    Wrapper for safe LLM invocation with error handling.
    """
    try:
        response = llm.invoke(prompt)
        return clean_text(response)

    except Exception as e:
        logger.error(f"LLM call failed: {str(e)}")
        return "Unable to generate response at the moment."


# ----------------------------
# Query Type Detection
# ----------------------------

def is_financial_query(query: str) -> bool:
    """
    Checks if query is finance-related.
    """
    query_lower: str = query.lower()
    # Accept common base finance terms even if they are not in FINANCIAL_KEYWORDS.
    if any(term in query_lower for term in ("finance", "financial", "financing")):
        return True

    return any(keyword in query_lower for keyword in FINANCIAL_KEYWORDS)


# ----------------------------
# Debug Helper
# ----------------------------

def debug_log(message: str) -> None:
    """
    Logs debug messages consistently.
    """
    logger.debug(message)