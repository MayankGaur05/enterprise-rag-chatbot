from __future__ import annotations

from pathlib import Path

from app.services.document_indexer import DocumentIndexer
from app.vectorstore.chroma_db import ChromaVectorStore


class FakeEmbeddingProvider:
    def embed_documents(self, texts: list[str]) -> list[list[float]]:
        # Deterministic, cheap vectors for local smoke testing
        return [[float(len(t)), 1.0, 0.5] for t in texts]

    def embed_query(self, text: str) -> list[float]:
        return [float(len(text)), 1.0, 0.5]


def main() -> None:
    processed_file = Path("data/processed/Azure_Devops_Interview_Questions.chunks.json")
    if not processed_file.exists():
        raise FileNotFoundError(f"Processed file not found: {processed_file}")

    vector_store = ChromaVectorStore(collection_name="sprint3_indexer_smoke")
    indexer = DocumentIndexer(
        embedding_provider=FakeEmbeddingProvider(),
        vector_store=vector_store,
    )

    stats = indexer.index_processed_chunks_file(processed_file)
    print(
        {
            "document_id": stats.document_id,
            "filename": stats.filename,
            "total_chunks": stats.total_chunks,
            "embedded": stats.embedded,
            "indexed": stats.indexed,
            "failed": stats.failed,
            "processing_time_sec": stats.processing_time_sec,
            "vector_count": vector_store.count(),
        }
    )


if __name__ == "__main__":
    main()