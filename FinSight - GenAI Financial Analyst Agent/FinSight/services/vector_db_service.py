import os
import pickle
import sys
from pathlib import Path
from typing import List, Dict
from logging import Logger

# Allow running this module directly (python vector_db_service.py) from nested paths.
if __package__ in (None, ""):
    project_root = Path(__file__).resolve().parents[2]
    if str(project_root) not in sys.path:
        sys.path.insert(0, str(project_root))

import numpy as np
import faiss

try:
    from FinSight.app.config import settings
    from FinSight.utils.logger import get_logger
except ModuleNotFoundError:
    from app.config import settings
    from utils.logger import get_logger

logger: Logger = get_logger(__name__)


class VectorDBService:
    """
    Handles vector storage and similarity search using FAISS
    """

    def __init__(self):
        self.index = None
        self.documents = []  # stores original docs (content + metadata)

        self.index_path = os.path.join(settings.EMBEDDINGS_DIR, "faiss.index")
        self.docstore_path = os.path.join(settings.EMBEDDINGS_DIR, "documents.pkl")

        os.makedirs(settings.EMBEDDINGS_DIR, exist_ok=True)

        # Try loading existing index
        self._load_index()

    # -------------------------------
    # Create index
    # -------------------------------
    def _create_index(self, dimension: int):
        self.index = faiss.IndexFlatL2(dimension)

    # -------------------------------
    # Add documents + embeddings
    # -------------------------------
    def add_documents(self, documents: List[Dict], embeddings: List[List[float]]):
        """
        documents: [{"content": "...", "metadata": {...}}]
        embeddings: [[...], [...]]
        """

        if embeddings:
            vectors = np.array(embeddings).astype("float32")

            if self.index is None:
                self._create_index(vectors.shape[1])

            self.index.add(vectors)

        self.documents.extend(documents)

        self._save_index()

    # -------------------------------
    # Search
    # -------------------------------
    def search(self, query_vector: List[float], top_k: int = None) -> List[Dict]:
        """
        Returns top_k most similar documents
        """

        if self.index is None or len(self.documents) == 0:
            logger.debug("Index or documents empty during search")
            return []

        if top_k is None:
            top_k = settings.TOP_K

        try:
            query = np.array([query_vector]).astype("float32")
            
            # Validate query dimensions
            if query.shape[1] != self.index.d:
                error_msg = (
                    f"Query vector dimension mismatch: "
                    f"query has {query.shape[1]} dimensions but index expects {self.index.d}. "
                    f"This may indicate the FAISS index needs to be rebuilt."
                )
                logger.error(error_msg)
                raise ValueError(error_msg)

            distances, indices = self.index.search(query, top_k)

            results = []
            for idx in indices[0]:
                if idx < len(self.documents):
                    results.append(self.documents[idx])

            logger.debug(f"Search returned {len(results)} results for query vector")
            return results
        
        except Exception as e:
            logger.error(f"Error during vector search: {e}", exc_info=True)
            return []

    # -------------------------------
    # Save index + documents
    # -------------------------------
    def _save_index(self):
        if self.index is not None:
            faiss.write_index(self.index, self.index_path)
        elif os.path.exists(self.index_path):
            os.remove(self.index_path)

        with open(self.docstore_path, "wb") as f:
            pickle.dump(self.documents, f)

    # -------------------------------
    # Load index + documents
    # -------------------------------
    def _load_index(self):
        if os.path.exists(self.index_path):
            try:
                self.index = faiss.read_index(self.index_path)
            except Exception as e:
                print(f"Error loading index: {e}")
                self.index = None

        if os.path.exists(self.docstore_path):
            try:
                with open(self.docstore_path, "rb") as f:
                    self.documents = pickle.load(f)
            except Exception as e:
                print(f"Error loading documents: {e}")
                self.documents = []

    # -------------------------------
    # Reset database (optional)
    # -------------------------------
    def reset(self):
        """
        Clears the entire vector database
        """

        self.index = None
        self.documents = []

        if os.path.exists(self.index_path):
            os.remove(self.index_path)

        if os.path.exists(self.docstore_path):
            os.remove(self.docstore_path)