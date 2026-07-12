from pathlib import Path
from typing import List

from requests import Response

from requests import Response

from requests import Response

try:
    # Works when running from the project root as a package.
    from FinSight.app.config import settings
except ModuleNotFoundError:
    # Fallback for direct script execution from nested folders.
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


class EmbeddingGenerator:
    """
    Generates vector embeddings for text chunks using Ollama.
    """

    def __init__(self) -> None:
        self.provider: str = settings.LLM_PROVIDER.lower()
        self.model: str = settings.EMBEDDING_MODEL
        self.last_error: str = ""

        if self.provider != "ollama":
            raise ValueError(
                f"Unsupported LLM_PROVIDER: {self.provider}. This project is configured for 'ollama'."
            )

        self.base_url: str = settings.OLLAMA_BASE_URL
        # Test Ollama connection
        try:
            resp: Response = requests.get(f"{self.base_url}/api/tags", timeout=5)
            if resp.status_code != 200:
                print(f"Warning: Ollama server at {self.base_url} is not responding properly")
        except Exception as e:
            print(f"Warning: Could not connect to Ollama at {self.base_url}: {e}")

    # -------------------------------
    # Generate embeddings for list of texts
    # -------------------------------
    def generate_embeddings(self, texts: List[str]) -> List[List[float]]:
        """
        Input:
        ["text chunk 1", "text chunk 2"]

        Output:
        [
            [0.123, 0.456, ...],
            [0.789, 0.111, ...]
        ]
        """

        return self._generate_embeddings_ollama(texts)

    def _generate_embeddings_ollama(self, texts: List[str]) -> List[List[float]]:
        """Generate embeddings using Ollama API"""
        try:
            embeddings = []
            for text in texts:
                payload: dict[str, str] = {
                    "model": self.model,
                    "prompt": text
                }
                response: Response = requests.post(
                    f"{self.base_url}/api/embeddings",
                    json=payload,
                    timeout=120
                )
                response.raise_for_status()
                data = response.json()
                embeddings.append(data.get("embedding", []))

            self.last_error: str = ""
            return embeddings

        except Exception as e:
            self.last_error = str(e)
            print(f"Error generating embeddings (Ollama): {e}")
            return []

    # -------------------------------
    # Generate embedding for single query
    # -------------------------------
    def generate_query_embedding(self, query: str) -> List[float]:
        """
        Used during retrieval (user question)
        """

        return self._generate_query_embedding_ollama(query)

    def _generate_query_embedding_ollama(self, query: str) -> List[float]:
        """Generate query embedding using Ollama API"""
        try:
            payload: dict[str, str] = {
                "model": self.model,
                "prompt": query
            }
            response: Response = requests.post(
                f"{self.base_url}/api/embeddings",
                json=payload,
                timeout=120
            )
            response.raise_for_status()
            data = response.json()
            
            self.last_error: str = ""
            return data.get("embedding", [])

        except Exception as e:
            self.last_error = str(e)
            print(f"Error generating query embedding (Ollama): {e}")
            return []