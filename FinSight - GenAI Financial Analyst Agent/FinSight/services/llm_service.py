import sys
from pathlib import Path

from requests import Response

from requests import Response

# Allow running this module directly (python llm_service.py) from nested paths.
if __package__ in (None, ""):
    project_root: Path = Path(__file__).resolve().parents[2]
    if str(project_root) not in sys.path:
        sys.path.insert(0, str(project_root))

try:
    from FinSight.app.config import settings
    from FinSight.core.rag.prompt_templates import PromptTemplates
except ModuleNotFoundError:
    from app.config import settings
    from core.rag.prompt_templates import PromptTemplates

try:
    import requests
except ImportError:
    requests = None


class LLMService:
    """
    Handles all LLM interactions via Ollama.
    """

    def __init__(self) -> None:
        self.provider: str = settings.LLM_PROVIDER.lower()
        self.model: str = settings.LLM_MODEL
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
    # Core LLM Call
    # -------------------------------
    def _generate(self, prompt: str) -> str:
        """
        Internal function to call LLM
        """
        return self._generate_ollama(prompt)

    def _generate_ollama(self, prompt: str) -> str:
        """Call Ollama local model"""
        try:
            payload = {
                "model": self.model,
                "prompt": prompt,
                "stream": False,
                "temperature": 0.3
            }
            response: Response = requests.post(f"{self.base_url}/api/generate", json=payload, timeout=120)
            response.raise_for_status()
            data = response.json()
            self.last_error: str = ""
            return data.get("response", "").strip()

        except Exception as e:
            self.last_error = str(e)
            print(f"Ollama LLM Error: {e}")
            return f"Error: Could not connect to Ollama. Make sure Ollama is running at {self.base_url}"

    # -------------------------------
    # General Q&A
    # -------------------------------
    def generate_answer(self, query: str, context: str) -> str:
        prompt: str = PromptTemplates.qa_prompt(query, context)
        return self._generate(prompt)

    # -------------------------------
    # Financial Analysis
    # -------------------------------
    def generate_financial_analysis(self, context: str) -> str:
        prompt: str = PromptTemplates.financial_analysis_prompt(context)
        return self._generate(prompt)

    # -------------------------------
    # Comparison Analysis
    # -------------------------------
    def generate_comparison(self, context: str, company_a: str, company_b: str) -> str:
        prompt: str = PromptTemplates.comparison_prompt(context, company_a, company_b)
        return self._generate(prompt)

    # -------------------------------
    # Insights
    # -------------------------------
    def generate_insights(self, context: str) -> str:
        prompt: str = PromptTemplates.insight_prompt(context)
        return self._generate(prompt)

    # -------------------------------
    # Recommendation
    # -------------------------------
    def generate_recommendation(self, context: str) -> str:
        prompt: str = PromptTemplates.recommendation_prompt(context)
        return self._generate(prompt)