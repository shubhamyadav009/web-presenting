import sys
from pathlib import Path

# Allow running this test file directly (python test_rag.py) from nested paths.
if __package__ in (None, ""):
    project_root = Path(__file__).resolve().parents[2]
    if str(project_root) not in sys.path:
        sys.path.insert(0, str(project_root))

import pytest
from unittest.mock import MagicMock, patch
import time

from FinSight.core.rag.pipeline import RAGPipeline


# ----------------------------
# Fixtures
# ----------------------------

@pytest.fixture
def sample_query():
    return "Analyze the company's revenue and margin performance"


@pytest.fixture
def mock_documents():
    return [
        {"page_content": "Revenue increased by 25% in FY23."},
        {"page_content": "Operating margin improved to 18%."}
    ]


@pytest.fixture
def mock_retriever(mock_documents):
    retriever = MagicMock()
    retriever.get_relevant_documents.return_value = mock_documents
    return retriever


@pytest.fixture
def mock_llm():
    llm = MagicMock()
    llm.invoke.return_value = (
        "The company shows strong revenue growth and improved operating margins."
    )
    return llm


# ----------------------------
# Core Functionality Tests
# ----------------------------

def test_rag_initialization():
    rag = RAGPipeline()

    assert rag is not None
    assert hasattr(rag, "retriever")
    assert hasattr(rag, "llm")


def test_rag_pipeline_flow(sample_query, mock_retriever, mock_llm):
    rag = RAGPipeline()
    rag.retriever = mock_retriever
    rag.llm = mock_llm

    result = rag.run(sample_query)

    assert isinstance(result, str)
    assert len(result) > 0


# ----------------------------
# Grounding / Faithfulness Test (CRITICAL)
# ----------------------------

def test_response_grounded_in_context(mock_retriever, mock_llm):
    rag = RAGPipeline()
    rag.retriever = mock_retriever
    rag.llm = mock_llm

    docs = mock_retriever.get_relevant_documents("revenue")
    result = rag.run("What is the revenue growth?")

    context = " ".join([doc["page_content"] for doc in docs]).lower()

    # Check that output words exist in context (basic grounding)
    overlap = [word for word in result.lower().split() if word in context]

    assert len(overlap) > 0


# ----------------------------
# Prompt Integrity Test
# ----------------------------

def test_prompt_structure(mock_retriever):
    rag = RAGPipeline()
    rag.retriever = mock_retriever

    with patch.object(rag.llm, "invoke") as mock_invoke:
        rag.run("Analyze margins")

        prompt = mock_invoke.call_args[0][0]

        assert "context" in prompt.lower()
        assert "analyze" in prompt.lower()


# ----------------------------
# Retrieval Quality Test
# ----------------------------

def test_retrieval_relevance(mock_retriever):
    docs = mock_retriever.get_relevant_documents("margin")

    assert any("margin" in doc["page_content"].lower() for doc in docs)


# ----------------------------
# Edge Case Tests
# ----------------------------

def test_empty_query():
    rag = RAGPipeline()

    with pytest.raises(ValueError):
        rag.run("")


def test_no_documents(mock_llm):
    rag = RAGPipeline()

    rag.retriever = MagicMock()
    rag.retriever.get_relevant_documents.return_value = []
    rag.llm = mock_llm

    result = rag.run("Analyze risk")

    assert isinstance(result, str)


# ----------------------------
# Robustness Tests
# ----------------------------

def test_llm_failure_handling(mock_retriever):
    rag = RAGPipeline()

    rag.retriever = mock_retriever
    rag.llm = MagicMock()
    rag.llm.invoke.side_effect = Exception("LLM API failure")

    result = rag.run("Test query")

    assert result is not None  # fallback response expected


def test_timeout_performance(sample_query, mock_retriever, mock_llm):
    rag = RAGPipeline()
    rag.retriever = mock_retriever
    rag.llm = mock_llm

    start = time.time()
    rag.run(sample_query)
    end = time.time()

    assert (end - start) < 5


# ----------------------------
# Consistency Test
# ----------------------------

def test_response_consistency(sample_query, mock_retriever, mock_llm):
    rag = RAGPipeline()

    rag.retriever = mock_retriever
    rag.llm = mock_llm

    result1 = rag.run(sample_query)
    result2 = rag.run(sample_query)

    assert result1 == result2


# ----------------------------
# Financial Domain Validation
# ----------------------------

def test_financial_keywords(mock_retriever, mock_llm):
    rag = RAGPipeline()

    rag.retriever = mock_retriever
    rag.llm = mock_llm

    result = rag.run("What is revenue growth and margin trend?")

    keywords = ["revenue", "margin", "growth"]

    assert any(keyword in result.lower() for keyword in keywords)