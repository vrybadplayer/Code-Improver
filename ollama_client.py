"""Ollama client for Automatic Code Improver - HTTP API integration."""

import logging
import requests
from typing import Optional, List, Dict, Any
from config import get_config

logger = logging.getLogger(__name__)


class OllamaClient:
    """Client for Ollama HTTP API calls."""

    def __init__(self):
        self.config = get_config()
        self.base_url = self.config.ollama.base_url.rstrip("/")
        self.session = requests.Session()
        self.session.headers.update({"Content-Type": "application/json"})

    def _make_request(self, endpoint: str, payload: Dict[str, Any], timeout: int) -> Dict[str, Any]:
        """Make HTTP request to Ollama API with error handling."""
        url = f"{self.base_url}{endpoint}"

        try:
            response = self.session.post(url, json=payload, timeout=timeout)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.Timeout:
            logger.error(f"Ollama request timed out after {timeout}s: {url}")
            raise TimeoutError(f"Ollama request timed out after {timeout} seconds")
        except requests.exceptions.ConnectionError:
            logger.error(f"Failed to connect to Ollama at {self.base_url}")
            raise ConnectionError(f"Cannot connect to Ollama at {self.base_url}. Is Ollama running?")
        except requests.exceptions.HTTPError as e:
            logger.error(f"Ollama HTTP error: {e.response.status_code} - {e.response.text}")
            raise
        except requests.exceptions.RequestException as e:
            logger.error(f"Ollama request failed: {e}")
            raise

    def generate_completion(
        self,
        prompt: str,
        model: Optional[str] = None,
        timeout: Optional[int] = None,
        system: Optional[str] = None,
        temperature: float = 0.1,
        **kwargs
    ) -> str:
        """Generate completion using specified model."""
        model = model or self.config.ollama.audit_agent_model
        timeout = timeout or self.config.ollama.audit_agent_timeout

        payload = {
            "model": model,
            "prompt": prompt,
            "stream": False,
            "options": {
                "temperature": temperature,
                **kwargs
            }
        }

        if system:
            payload["system"] = system

        logger.debug(f"Generating completion with model {model}, timeout {timeout}s")
        result = self._make_request("/api/generate", payload, timeout)
        return result.get("response", "")

    def generate_audit_completion(self, prompt: str, system: Optional[str] = None) -> str:
        """Generate completion for Audit Agent (10-min timeout, qwen2.5-coder:14b)."""
        return self.generate_completion(
            prompt=prompt,
            model=self.config.ollama.audit_agent_model,
            timeout=self.config.ollama.audit_agent_timeout,
            system=system
        )

    def generate_coding_completion(self, prompt: str, system: Optional[str] = None) -> str:
        """Generate completion for Coding Agent (5-min timeout, qwen2.5-coder:14b)."""
        return self.generate_completion(
            prompt=prompt,
            model=self.config.ollama.coding_agent_model,
            timeout=self.config.ollama.coding_agent_timeout,
            system=system
        )

    def generate_embeddings(self, texts: List[str]) -> List[List[float]]:
        """Generate embeddings for multiple texts using nomic-embed-text."""
        embeddings = []
        for text in texts:
            payload = {
                "model": self.config.ollama.embeddings_model,
                "prompt": text
            }
            result = self._make_request("/api/embeddings", payload, self.config.ollama.embeddings_timeout)
            embedding = result.get("embedding", [])
            embeddings.append(embedding)
        return embeddings

    def check_health(self) -> bool:
        """Check if Ollama is running and responsive."""
        try:
            response = self.session.get(f"{self.base_url}/api/tags", timeout=5)
            return response.status_code == 200
        except Exception as e:
            logger.warning(f"Ollama health check failed: {e}")
            return False

    def list_models(self) -> List[str]:
        """List available models in Ollama."""
        try:
            response = self.session.get(f"{self.base_url}/api/tags", timeout=10)
            response.raise_for_status()
            data = response.json()
            return [model["name"] for model in data.get("models", [])]
        except Exception as e:
            logger.error(f"Failed to list Ollama models: {e}")
            return []

    def pull_model(self, model_name: str) -> bool:
        """Pull a model in Ollama."""
        try:
            payload = {"name": model_name}
            # Pull can take a long time, use a generous timeout
            response = self.session.post(f"{self.base_url}/api/pull", json=payload, timeout=300)
            response.raise_for_status()
            # Streaming response - check for success
            return True
        except Exception as e:
            logger.error(f"Failed to pull model {model_name}: {e}")
            return False


# Global instance
_ollama_client = None


def get_ollama_client() -> OllamaClient:
    """Get global Ollama client instance."""
    global _ollama_client
    if _ollama_client is None:
        _ollama_client = OllamaClient()
    return _ollama_client