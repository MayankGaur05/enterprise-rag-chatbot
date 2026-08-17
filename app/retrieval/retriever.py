import time

from app.config import get_settings
from app.core.logging_config import setup_logging
from app.embeddings.base import EmbeddingProvider
from app.ingestion.exceptions import IngestionError
from app.retrieval.model import SearchResult
from app.vectorstore.base import VectorStore


class Retriever:
    def __init__(
        self,
        embedding_provider: EmbeddingProvider,
        vector_store: VectorStore,
        log_level: str = "INFO",
    ) -> None:
        self.settings = get_settings()
        self.embedding_provider = embedding_provider
        self.vector_store = vector_store
        self.logger = setup_logging(self.settings.log_level or log_level)

    def search(self, query:str, top_k:int | None = None) -> list[SearchResult]:
        if not query or not query.strip():
            raise ValueError("Query must be a non-empty string.")

        effective_top_k = top_k if top_k is not None else self.settings.retrieval_default_top_k

        if effective_top_k <= 0:
            raise ValueError("top_k must be a positive integer.")

        if effective_top_k > self.settings.retrieval_max_top_k:
            raise ValueError(f"top_k cannot exceed {self.settings.retrieval_max_top_k}.")   

        embedding_start = time.perf_counter()
        self.logger.info(f"Search started | query={query} | top_k={effective_top_k}")
        self.logger.info(
                    f"Query received | query_len={len(query)} | top_k={effective_top_k}"
        )
        
        try:
            query_embedding = self.embedding_provider.embed_query(query.strip())
            embedding_latency_ms = (time.perf_counter() - embedding_start) * 1000
        except Exception as e:
            raise IngestionError(f"Failed to embed query: {e}") from e
        self.logger.info(f"Query embedding generated | latency_ms={embedding_latency_ms:.2f}")

        retrieval_start = time.perf_counter()
        try:    
            raw_results  = self.vector_store.query(query_embedding, top_k=effective_top_k)
            retrieval_latency_ms = (time.perf_counter() - retrieval_start) * 1000
        except Exception as e:
            raise IngestionError(f"Failed to retrieve results from vector store: {e}") from e
        self.logger.info(f"Results retrieved | latency_ms={retrieval_latency_ms:.2f} | results_count={len(raw_results)}")

        results: list[SearchResult] = []
        for item in raw_results:
            results.append(
                            SearchResult(
                            content=str(item.get("content", "")),
                            score=float(item.get("score", 0.0)),
                            metadata=dict(item.get("metadata", {})),
                        )
            )

        total_latency_ms = (time.perf_counter() - embedding_start) * 1000
        top_score = max((r.score for r in results), default=0.0)
        low_score = min((r.score for r in results), default=0.0)

        self.logger.info(
        "Vector search completed | "
        f"results={len(results)} | top_score={top_score:.4f} | lowest_score={low_score:.4f} | "
        f"retrieval_latency_ms={retrieval_latency_ms:.2f} | total_search_latency_ms={total_latency_ms:.2f}"
        )

        return results