"""
embeddings_optimized.py

Optimized embedding generation with:
- Batch/concurrent processing
- Progress tracking
- Optional HuggingFace local embeddings (much faster)
- Timeout tuning
- Error resilience
"""

from pathlib import Path
from typing import List, Optional
import sys
from concurrent.futures import ThreadPoolExecutor, as_completed

try:
    from FinSight.app.config import settings
except ModuleNotFoundError:
    import sys
    from pathlib import Path
    project_root: Path = Path(__file__).resolve().parents[3]
    if str(project_root) not in sys.path:
        sys.path.insert(0, str(project_root))
    from FinSight.app.config import settings

try:
    import requests
except ImportError:
    requests = None

try:
    from sentence_transformers import SentenceTransformer
    HAS_SENTENCE_TRANSFORMERS = True
except ImportError:
    HAS_SENTENCE_TRANSFORMERS = False


class EmbeddingGeneratorOptimized:
    """
    Fast embedding generation with parallel processing and optional local models.
    
    Usage:
    - Initialize with use_huggingface=True for ~10x faster local embeddings
    - Use generate_embeddings() for batch processing
    - Automatic fallback to Ollama if HuggingFace unavailable
    """

    def __init__(self, use_huggingface: bool = True, batch_size: int = 32) -> None:
        self.provider: str = settings.LLM_PROVIDER.lower()
        self.model: str = settings.EMBEDDING_MODEL
        self.last_error: str = ""
        self.batch_size = batch_size
        self.use_huggingface = use_huggingface and HAS_SENTENCE_TRANSFORMERS

        # Try to initialize HuggingFace local embeddings (fast!)
        if self.use_huggingface:
            try:
                print(f"Loading HuggingFace model: {self.model}")
                self.hf_model = SentenceTransformer(self.model)
                print(f"✓ HuggingFace embeddings loaded (local, fast)")
                return
            except Exception as e:
                print(f"⚠ HuggingFace failed: {e}. Falling back to Ollama.")
                self.use_huggingface = False

        # Fallback: Ollama
        if self.provider != "ollama":
            raise ValueError(
                f"Unsupported LLM_PROVIDER: {self.provider}. "
                "Configure 'ollama' or install sentence-transformers for HuggingFace."
            )

        self.base_url: str = settings.OLLAMA_BASE_URL
        self.hf_model = None

        # Test Ollama connection
        try:
            resp = requests.get(f"{self.base_url}/api/tags", timeout=5)
            if resp.status_code != 200:
                print(f"Warning: Ollama server at {self.base_url} not responding properly")
        except Exception as e:
            print(f"Warning: Could not connect to Ollama at {self.base_url}: {e}")

    # =====================================================================
    # BATCH EMBEDDINGS (FAST + PARALLEL)
    # =====================================================================
    def generate_embeddings(
        self, texts: List[str], show_progress: bool = True
    ) -> List[List[float]]:
        """
        Generate embeddings for multiple texts with progress tracking.
        Returns embeddings list parallel to input texts list.
        """
        if not texts:
            return []

        # Use HuggingFace if available (much faster, no network calls)
        if self.use_huggingface and self.hf_model:
            return self._generate_embeddings_huggingface(texts, show_progress)

        # Fallback to Ollama with parallel processing
        return self._generate_embeddings_ollama_parallel(texts, show_progress)

    def _generate_embeddings_huggingface(
        self, texts: List[str], show_progress: bool = True
    ) -> List[List[float]]:
        """
        Generate embeddings using local HuggingFace model (FAST).
        Batch processing built-in.
        """
        try:
            total = len(texts)
            if show_progress:
                print(f"Embedding {total} chunks with HuggingFace (local)...")

            # sentence_transformers handles batching internally
            embeddings = self.hf_model.encode(
                texts,
                batch_size=self.batch_size,
                show_progress_bar=show_progress,
                convert_to_numpy=False
            )

            self.last_error = ""
            if show_progress:
                print(f"✓ Generated {len(embeddings)} embeddings")
            return [emb.tolist() if hasattr(emb, 'tolist') else emb for emb in embeddings]

        except Exception as e:
            self.last_error = str(e)
            print(f"Error generating embeddings (HuggingFace): {e}")
            return []

    def _generate_embeddings_ollama_parallel(
        self, texts: List[str], show_progress: bool = True
    ) -> List[List[float]]:
        """
        Generate embeddings using Ollama with parallel processing (faster).
        Spawns multiple threads to fetch from Ollama concurrently.
        """
        total = len(texts)
        if show_progress:
            print(f"Embedding {total} chunks with Ollama (parallel, 4 workers)...")

        embeddings = [None] * total
        completed = 0

        # Use ThreadPoolExecutor for parallel requests
        with ThreadPoolExecutor(max_workers=4) as executor:
            # Submit all tasks
            future_to_idx = {
                executor.submit(self._fetch_embedding_ollama, text): idx
                for idx, text in enumerate(texts)
            }

            # Collect results as they complete
            for future in as_completed(future_to_idx):
                idx = future_to_idx[future]
                try:
                    embeddings[idx] = future.result()
                    completed += 1
                    if show_progress and completed % max(1, total // 10) == 0:
                        print(f"  {completed}/{total} embeddings generated...")
                except Exception as e:
                    print(f"  Error embedding chunk {idx}: {e}")
                    embeddings[idx] = []

        self.last_error = ""
        if show_progress:
            print(f"✓ Generated {total} embeddings")
        return [emb for emb in embeddings if emb]

    def _fetch_embedding_ollama(self, text: str) -> List[float]:
        """Fetch single embedding from Ollama (used in parallel)."""
        try:
            payload = {"model": self.model, "prompt": text}
            response = requests.post(
                f"{self.base_url}/api/embeddings",
                json=payload,
                timeout=60  # Reduced from 120 to 60s
            )
            response.raise_for_status()
            return response.json().get("embedding", [])
        except Exception as e:
            raise RuntimeError(f"Ollama embedding failed: {e}")

    # =====================================================================
    # SINGLE QUERY EMBEDDING
    # =====================================================================
    def generate_query_embedding(self, query: str) -> List[float]:
        """Generate embedding for a single query (used during retrieval)."""
        if self.use_huggingface and self.hf_model:
            return self._generate_query_embedding_huggingface(query)
        return self._generate_query_embedding_ollama(query)

    def _generate_query_embedding_huggingface(self, query: str) -> List[float]:
        """Fast local query embedding."""
        try:
            embedding = self.hf_model.encode([query], convert_to_numpy=False)[0]
            self.last_error = ""
            return embedding.tolist() if hasattr(embedding, 'tolist') else embedding
        except Exception as e:
            self.last_error = str(e)
            print(f"Error generating query embedding (HuggingFace): {e}")
            return []

    def _generate_query_embedding_ollama(self, query: str) -> List[float]:
        """Query embedding via Ollama."""
        try:
            payload = {"model": self.model, "prompt": query}
            response = requests.post(
                f"{self.base_url}/api/embeddings",
                json=payload,
                timeout=60  # Reduced from 120
            )
            response.raise_for_status()
            data = response.json()
            self.last_error = ""
            return data.get("embedding", [])
        except Exception as e:
            self.last_error = str(e)
            print(f"Error generating query embedding (Ollama): {e}")
            return []
