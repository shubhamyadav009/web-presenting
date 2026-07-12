from typing import List, Dict
import re
import sys
from pathlib import Path
from logging import Logger

# Allow running this module directly (python pipeline.py) from nested paths.
if __package__ in (None, ""):
    project_root = Path(__file__).resolve().parents[3]
    if str(project_root) not in sys.path:
        sys.path.insert(0, str(project_root))

try:
    # Try optimized embedder first (with HuggingFace support)
    try:
        from FinSight.core.rag.embeddings_optimized import EmbeddingGeneratorOptimized as EmbeddingGenerator
    except (ModuleNotFoundError, ImportError):
        # Fallback to original embedder if optimized not available
        from FinSight.core.rag.embeddings import EmbeddingGenerator
    
    from FinSight.services.vector_db_service import VectorDBService
    from FinSight.services.llm_service import LLMService
    from FinSight.core.finance.extractor import FinancialExtractor
    from FinSight.core.finance.ratios import FinancialRatios
    from FinSight.core.finance.insights import FinancialInsights
    from FinSight.core.finance.recommendation import InvestmentRecommendation
    from FinSight.core.citation.citation_engine import CitationEngine
    from FinSight.utils.logger import get_logger
except ModuleNotFoundError:
    # Fallback to relative imports
    try:
        from core.rag.embeddings_optimized import EmbeddingGeneratorOptimized as EmbeddingGenerator
    except (ModuleNotFoundError, ImportError):
        from core.rag.embeddings import EmbeddingGenerator
    
    from services.vector_db_service import VectorDBService
    from services.llm_service import LLMService
    from core.finance.extractor import FinancialExtractor
    from core.finance.ratios import FinancialRatios
    from core.finance.insights import FinancialInsights
    from core.finance.recommendation import InvestmentRecommendation
    from core.citation.citation_engine import CitationEngine
    from utils.logger import get_logger
    from utils.logger import get_logger

logger: Logger = get_logger(__name__)


class RAGPipeline:
    """
    End-to-end pipeline:
    Query → Retrieve → Analyze → Answer
    """

    def __init__(self):
        # RAG components
        try:
            self.embedder = EmbeddingGenerator()
        except Exception as e:
            logger.warning(f"Failed to initialize EmbeddingGenerator: {e}", exc_info=True)
            self.embedder = None

        self.vector_db = VectorDBService()
        try:
            self.llm = LLMService()
        except Exception as e:
            logger.warning(f"Failed to initialize LLMService: {e}", exc_info=True)
            self.llm = None

        # Finance components
        try:
            self.extractor = FinancialExtractor()
            self.ratios = FinancialRatios()
            self.insights = FinancialInsights()
            self.recommendation = InvestmentRecommendation()
        except Exception as e:
            logger.warning(f"Failed to initialize finance components: {e}", exc_info=True)
            self.extractor = None
            self.ratios = None
            self.insights = None
            self.recommendation = None

        # Citation
        try:
            self.citation_engine = CitationEngine()
        except Exception as e:
            logger.warning(f"Failed to initialize CitationEngine: {e}", exc_info=True)
            self.citation_engine = None

    # Main Query Pipeline
    # -------------------------------
    def run_query(self, query: str) -> Dict:
        """
        Main function called by API
        """
        try:
            # Step 1: Convert query → embedding
            query_vector = self.embedder.generate_query_embedding(query) if self.embedder else []
            if not query_vector:
                docs = self._keyword_retrieve(query)
                if not docs:
                    return {
                        "answer": (
                            "Unable to process the query because embeddings could not be generated, "
                            "and no local documents were available for fallback retrieval. "
                            "Check that your selected provider is available and try again."
                        ),
                        "citations": [],
                        "source": "fallback_no_documents"
                    }

                if self.citation_engine:
                    raw_citations = self.citation_engine.extract_citations(docs)
                    unique_citations = self.citation_engine.deduplicate_citations(raw_citations)
                    formatted_citations = self.citation_engine.format_citations(unique_citations)
                else:
                    formatted_citations = []

                return {
                    "answer": self._generate_fallback_answer(query, docs),
                    "citations": formatted_citations,
                    "source": "fallback_local_retrieval"
                }

            # Step 2: Retrieve relevant documents
            docs = self.vector_db.search(query_vector)

            # Step 3: Extract citations
            if self.citation_engine:
                raw_citations = self.citation_engine.extract_citations(docs)
                unique_citations = self.citation_engine.deduplicate_citations(raw_citations)
                formatted_citations = self.citation_engine.format_citations(unique_citations)
            else:
                formatted_citations = []

            # Step 4: Combine content for LLM
            context = "\n".join([doc["content"] for doc in docs])

            # Step 5: Generate answer using LLM
            if self.llm:
                answer = self.llm.generate_answer(query, context)
                source = "llm"
            else:
                answer = self._generate_fallback_answer(query, docs)
                source = "fallback_llm_unavailable"

            if "quota is exceeded" in answer.lower() or answer == "Error generating response":
                answer = self._generate_fallback_answer(query, docs)
                source = "fallback_llm_error"

            return {
                "answer": answer,
                "citations": formatted_citations,
                "source": source
            }
        
        except Exception as e:
            error_msg = str(e) if str(e) else type(e).__name__
            logger.error(f"Error in run_query: {error_msg}", exc_info=True)
            return {
                "answer": f"An error occurred while processing your query: {error_msg}",
                "citations": [],
                "source": "error"
            }

    # -------------------------------
    # Offline fallback retrieval
    # -------------------------------
    def _keyword_retrieve(self, query: str, top_k: int = 5) -> List[Dict]:
        """
        Lightweight retrieval path when embeddings are unavailable.
        Scores documents by token overlap with query.
        """

        documents = getattr(self.vector_db, "documents", [])
        if not documents:
            return []

        query_tokens = set(re.findall(r"[a-zA-Z0-9]+", query.lower()))
        if not query_tokens:
            return documents[:top_k]

        scored = []
        for doc in documents:
            content = doc.get("content", "")
            text_tokens = set(re.findall(r"[a-zA-Z0-9]+", content.lower()))
            score = len(query_tokens.intersection(text_tokens))
            scored.append((score, doc))

        scored.sort(key=lambda item: item[0], reverse=True)
        best_docs = [doc for score, doc in scored if score > 0]

        if not best_docs:
            return documents[:top_k]

        return best_docs[:top_k]

    # -------------------------------
    # Offline fallback answer
    # -------------------------------
    def _generate_fallback_answer(self, query: str, docs: List[Dict]) -> str:
        """
        Produces a concise deterministic answer from retrieved snippets.
        """

        if not docs:
            return "No relevant information found in the local document store."

        snippets = []
        for doc in docs[:3]:
            content = doc.get("content", "").strip().replace("\n", " ")
            if content:
                snippets.append(content[:220])

        if not snippets:
            return "Relevant documents were found, but no readable text snippets were available."

        return (
            f"The configured LLM provider is currently unavailable, so this answer is generated from local retrieval for: '{query}'. "
            f"Key evidence: {' | '.join(snippets)}"
        )

    # -------------------------------
    # Financial Analysis Pipeline
    # -------------------------------
    def run_financial_analysis(self, query: str) -> Dict:
        """
        Advanced pipeline with financial intelligence
        """

        # Step 1: Retrieve documents
        query_vector = self.embedder.generate_query_embedding(query) if self.embedder else []
        if not query_vector:
            return {
                "financials": {},
                "ratios": {},
                "insights": [],
                "recommendation": "Unable to generate financial analysis because embeddings are unavailable.",
                "citations": []
            }
        docs = self.vector_db.search(query_vector)

        # Step 2: Extract financial data
        financials = self.extractor.extract_financials(docs)

        # Step 3: Calculate ratios
        ratios = self.ratios.calculate_ratios(financials)

        # Step 4: Generate insights
        insights = self.insights.generate_insights(financials)

        # Step 5: Generate recommendation
        recommendation = self.recommendation.generate_recommendation(financials, ratios)

        # Step 6: Citations
        raw_citations = self.citation_engine.extract_citations(docs)
        unique_citations = self.citation_engine.deduplicate_citations(raw_citations)
        formatted_citations = self.citation_engine.format_citations(unique_citations)

        return {
            "financials": financials,
            "ratios": ratios,
            "insights": insights,
            "recommendation": recommendation,
            "citations": formatted_citations
        }