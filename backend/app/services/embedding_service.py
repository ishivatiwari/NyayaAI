"""
Embedding service: generate embeddings using Google Gemini or OpenAI.
Abstracted behind a common interface.
"""
from abc import ABC, abstractmethod
from typing import List
import structlog

from app.config import settings

logger = structlog.get_logger()


class BaseEmbeddingProvider(ABC):
    @abstractmethod
    async def embed(self, texts: List[str]) -> List[List[float]]:
        pass

    @abstractmethod
    async def embed_query(self, text: str) -> List[float]:
        pass


class GeminiEmbeddingProvider(BaseEmbeddingProvider):
    """Google Gemini embedding provider with automatic model fallback and mock resilience."""

    def __init__(self):
        import google.generativeai as genai
        genai.configure(api_key=settings.GOOGLE_API_KEY)
        self.candidate_models = [
            settings.EMBEDDING_MODEL,
            "gemini-embedding-001",
            "models/gemini-embedding-001",
            "gemini-embedding-2",
            "models/gemini-embedding-2",
            "text-embedding-004",
        ]
        self.working_model = None
        self.mock_fallback = MockEmbeddingProvider()

    def _embed_single(self, genai, text: str, task_type: str) -> List[float]:
        models_to_try = [self.working_model] if self.working_model else self.candidate_models
        last_err = None

        for model_name in models_to_try:
            if not model_name:
                continue
            try:
                res = genai.embed_content(
                    model=model_name,
                    content=text,
                    task_type=task_type,
                )
                if "embedding" in res:
                    self.working_model = model_name
                    return res["embedding"]
            except Exception as e:
                last_err = e
                logger.warning("Embedding attempt failed for model", model=model_name, error=str(e))

        logger.warning("All Gemini embedding models failed, using deterministic embedding fallback", error=str(last_err))
        import hashlib
        h = hashlib.sha256(text.encode()).digest()
        vec = [(b / 255.0) - 0.5 for b in h * (768 // 32 + 1)]
        return vec[:768]

    async def embed(self, texts: List[str]) -> List[List[float]]:
        import google.generativeai as genai
        results = []
        for i in range(0, len(texts), 10):
            batch = texts[i : i + 10]
            for text in batch:
                vec = self._embed_single(genai, text, "retrieval_document")
                results.append(vec)
        return results

    async def embed_query(self, text: str) -> List[float]:
        import google.generativeai as genai
        return self._embed_single(genai, text, "retrieval_query")


class OpenAIEmbeddingProvider(BaseEmbeddingProvider):
    """OpenAI text-embedding-3-small."""

    def __init__(self):
        from openai import AsyncOpenAI
        self.client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)
        self.model = "text-embedding-3-small"

    async def embed(self, texts: List[str]) -> List[List[float]]:
        response = await self.client.embeddings.create(
            model=self.model, input=texts
        )
        return [item.embedding for item in response.data]

    async def embed_query(self, text: str) -> List[float]:
        response = await self.client.embeddings.create(
            model=self.model, input=[text]
        )
        return response.data[0].embedding


class MockEmbeddingProvider(BaseEmbeddingProvider):
    """Mock provider for demo/testing when no API key is available."""

    DIMENSION = 768

    async def embed(self, texts: List[str]) -> List[List[float]]:
        import hashlib
        results = []
        for text in texts:
            h = hashlib.sha256(text.encode()).digest()
            vec = [(b / 255.0) - 0.5 for b in h * (self.DIMENSION // 32 + 1)]
            results.append(vec[: self.DIMENSION])
        return results

    async def embed_query(self, text: str) -> List[float]:
        results = await self.embed([text])
        return results[0]


def get_embedding_provider() -> BaseEmbeddingProvider:
    """Factory: return the appropriate embedding provider."""
    if settings.DEMO_MODE:
        logger.info("Using mock embedding provider (demo mode)")
        return MockEmbeddingProvider()

    provider = settings.LLM_PROVIDER.lower()
    if provider == "gemini" and settings.GOOGLE_API_KEY:
        logger.info("Using Gemini embedding provider")
        return GeminiEmbeddingProvider()
    elif settings.OPENAI_API_KEY:
        logger.info("Using OpenAI embedding provider")
        return OpenAIEmbeddingProvider()
    else:
        logger.warning("No API key found, falling back to mock embedding provider")
        return MockEmbeddingProvider()
