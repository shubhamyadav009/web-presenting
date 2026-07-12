"""
constants.py

Central configuration file for FinSight - GenAI Financial Analyst Agent.
Contains all reusable constants for RAG, LLM, financial metrics, and system settings.
"""

# ----------------------------
# Project Metadata
# ----------------------------

PROJECT_NAME = "FinSight"
VERSION = "1.0.0"
AUTHOR = "Shubham Yadav"


# ----------------------------
# File & Directory Paths
# ----------------------------

DATA_DIR = "data/"
VECTOR_DB_DIR = "vector_store/"
LOG_DIR = "logs/"
MODEL_CACHE_DIR = "models/"

DEFAULT_EMBEDDING_MODEL = "nomic-embed-text"
DEFAULT_LLM_MODEL = "mistral"


# ----------------------------
# RAG Configuration
# ----------------------------

TOP_K_RETRIEVAL = 5
MAX_TOKENS = 500
TEMPERATURE = 0.3

SIMILARITY_THRESHOLD = 0.7
CHUNK_SIZE = 500
CHUNK_OVERLAP = 50


# ----------------------------
# Prompt Templates
# ----------------------------

RAG_PROMPT_TEMPLATE = """
You are a financial analyst AI.

Use ONLY the provided context to answer the question.

Context:
{context}

Question:
{question}

Answer in a clear, concise financial analysis format.
"""


# ----------------------------
# Financial Keywords
# ----------------------------

FINANCIAL_KEYWORDS = [
    "revenue",
    "profit",
    "margin",
    "ebitda",
    "growth",
    "expenses",
    "cash flow",
    "net income",
    "operating income"
]


# ----------------------------
# Financial Ratios
# ----------------------------

FINANCIAL_RATIOS = {
    "profit_margin": "Net Profit / Revenue",
    "operating_margin": "Operating Income / Revenue",
    "return_on_assets": "Net Income / Total Assets",
    "return_on_equity": "Net Income / Shareholder Equity",
    "debt_to_equity": "Total Debt / Equity",
    "current_ratio": "Current Assets / Current Liabilities"
}


# ----------------------------
# Error Messages
# ----------------------------

ERROR_EMPTY_QUERY = "Query cannot be empty."
ERROR_NO_DOCUMENTS = "No relevant documents found."
ERROR_LLM_FAILURE = "LLM failed to generate response."
ERROR_INVALID_INPUT = "Invalid input provided."


# ----------------------------
# Logging Configuration
# ----------------------------

LOG_LEVEL = "INFO"
LOG_FORMAT = "%(asctime)s - %(levelname)s - %(message)s"


# ----------------------------
# Evaluation Settings
# ----------------------------

MIN_RESPONSE_LENGTH = 20
MAX_RESPONSE_LENGTH = 1000

RELEVANCE_KEYWORDS_THRESHOLD = 1  # Minimum keyword match


# ----------------------------
# API Configuration (if used)
# ----------------------------

REQUEST_TIMEOUT = 10  # seconds
RETRY_ATTEMPTS = 3
RETRY_DELAY = 2  # seconds


# ----------------------------
# Test Constants
# ----------------------------

TEST_QUERY = "Analyze the company's financial performance"
TEST_EXPECTED_KEYWORDS = ["revenue", "growth", "profit"]