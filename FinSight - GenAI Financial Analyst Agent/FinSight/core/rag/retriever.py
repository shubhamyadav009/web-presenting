from typing import List, Dict
import sys
from pathlib import Path

# Allow running this module directly (python retriever.py) from nested paths.
if __package__ in (None, ""):
    project_root: Path = Path(__file__).resolve().parents[3]
    if str(project_root) not in sys.path:
        sys.path.insert(0, str(project_root))

from FinSight.core.rag.embeddings import EmbeddingGenerator
from FinSight.services.vector_db_service import VectorDBService


class Retriever:
    """
    Handles retrieval of relevant documents using vector similarity
    """

    def __init__(self) -> None:
        self.embedder = EmbeddingGenerator()
        self.vector_db = VectorDBService()

    # -------------------------------
    # Retrieve relevant documents
    # -------------------------------
    def retrieve(self, query: str, top_k: int = 5) -> List[Dict]:
        """
        Input:
        query: user question

        Output:
        [
            {
                "content": "...",
                "metadata": {
                    "source": "file.pdf",
                    "page": 10
                }
            }
        ]
        """

        # Step 1: Convert query → embedding
        query_vector: List[float] = self.embedder.generate_query_embedding(query)

        # Step 2: Search vector DB
        results = self.vector_db.search(query_vector, top_k=top_k)

        return results

    # -------------------------------
    # Retrieve only text (for LLM)
    # -------------------------------
    def retrieve_text(self, query: str, top_k: int = 5) -> str:
        """
        Returns combined text for prompt
        """

        docs = self.retrieve(query, top_k)

        combined_text: str = "\n".join([doc["content"] for doc in docs])

        return combined_text

    # -------------------------------
    # Retrieve with metadata (for citations)
    # -------------------------------
    def retrieve_with_metadata(self, query: str, top_k: int = 5) -> List[Dict]:
        """
        Returns full documents (content + metadata)
        """

        return self.retrieve(query, top_k)