from __future__ import annotations

import time
from collections.abc import Iterable

from openai import (
    APIConnectionError,
    APITimeoutError,
    InternalServerError,
    OpenAI,
    RateLimitError,
)

from app.config import get_settings
from app.core.logging_config import setup_logging
from app.ingestion.exceptions import IngestionError

from .base import EmbeddingProvider


class OpenAIEmbeddingProvider(EmbeddingProvider):
    def __init__(
        self,
        api_key: str | None = None,
        model: str | None = None,
        batch_size: int | None = None,
        max_retries: int | None = None,
    ) -> None:
        settings = get_settings()

        resolved_api_key = api_key or settings.openai_api_key
        if not resolved_api_key:
            raise IngestionError("OPENAI_API_KEY is not configured.")

        self.model = model or settings.embedding_model
        self.batch_size = batch_size or settings.embedding_batch_size
        self.max_retries = max_retries or settings.embedding_max_retries
        self.logger = setup_logging(settings.log_level)
        self.client = OpenAI(api_key=resolved_api_key)

    def embed_documents(self, texts: list[str]) -> list[list[float]]:
        if not texts:
            return []

        cleaned = [t.strip() for t in texts if t and t.strip()]
        if not cleaned:
            return []

        self.logger.info(
            f"Embedding documents started | model={self.model} | texts={len(cleaned)} | batch_size={self.batch_size}"
        )
        start = time.perf_counter()

        vectors: list[list[float]] = []
        for batch in self._batched(cleaned, self.batch_size):
            vectors.extend(self._embed_with_retry(batch))

        latency_ms = (time.perf_counter() - start) * 1000
        self.logger.info(
            f"Embedding documents completed | embedded={len(vectors)} | latency_ms={latency_ms:.2f}"
        )
        return vectors

    def embed_query(self, text: str) -> list[float]:
        if not text or not text.strip():
            raise ValueError("Query text cannot be empty.")

        self.logger.info(f"Embedding query started | model={self.model}")
        start = time.perf_counter()

        vectors = self._embed_with_retry([text.strip()])
        latency_ms = (time.perf_counter() - start) * 1000
        self.logger.info(f"Embedding query completed | latency_ms={latency_ms:.2f}")

        return vectors[0]

    def _embed_with_retry(self, inputs: list[str]) -> list[list[float]]:
        last_error: Exception | None = None

        for attempt in range(1, self.max_retries + 1):
            try:
                response = self.client.embeddings.create(
                    model=self.model,
                    input=inputs,
                )
                return [item.embedding for item in response.data]
            except (APIConnectionError, APITimeoutError, InternalServerError, RateLimitError) as exc:
                last_error = exc
                self.logger.warning(
                    f"Embedding request failed | attempt={attempt}/{self.max_retries} | error={exc}"
                )

        raise IngestionError(f"Embedding failed after {self.max_retries} attempts: {last_error}") from last_error

    @staticmethod
    def _batched(items: list[str], batch_size: int) -> Iterable[list[str]]:
        for i in range(0, len(items), batch_size):
            yield items[i : i + batch_size]