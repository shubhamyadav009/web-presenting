"""RAG pipeline components"""
try:
	from FinSight.core.rag.pipeline import RAGPipeline
except ModuleNotFoundError:
	from core.rag.pipeline import RAGPipeline

__all__ = ["RAGPipeline"]
