from __future__ import annotations

import json
import time
from pathlib import Path
from typing import Any

from app.core.logging_config import setup_logging
from app.embeddings.base import EmbeddingProvider
from app.ingestion.exceptions import EmptyDocumentError, IngestionError
from app.models.document import IndexingStats
from app.vectorstore.base import VectorStore


class DocumentIndexer:
    def __init__(
        self,
        embedding_provider: EmbeddingProvider,
        vector_store: VectorStore,
        log_level: str = "INFO",
    ) -> None:
        self.embedding_provider = embedding_provider
        self.vector_store = vector_store
        self.logger = setup_logging(log_level)

    def index_processed_chunks_file(self, file_path: str | Path) -> IndexingStats:
        start = time.perf_counter()
        path = Path(file_path)
        rows = json.loads(path.read_text(encoding="utf-8"))

        if not isinstance(rows, list) or not rows:
            raise ValueError("Processed chunk file must contain a non-empty JSON array.")

        first_metadata = rows[0].get("metadata", {})
        document_id = str(first_metadata.get("document_id", "unknown"))
        filename = str(rows[0].get("filename", path.name))

        ids: list[str] = []
        texts: list[str] = []
        metadatas: list[dict[str, Any]] = []

        failed = 0
        for idx, row in enumerate(rows, start=1):
            try:
                metadata = dict(row.get("metadata") or {})
                content = str(row.get("content") or "")
                if not content.strip():
                    raise EmptyDocumentError("empty chunk content")

                chunk_id = str(metadata.get("chunk_id") or "").strip()
                doc_id = str(metadata.get("document_id") or document_id).strip()
                if not doc_id or not chunk_id:
                    raise IngestionError("missing document_id or chunk_id in metadata")

                vector_id = f"{doc_id}::{chunk_id}"
                ids.append(vector_id)
                texts.append(content)
                metadatas.append(metadata)
            except (IngestionError, EmptyDocumentError, TypeError, ValueError) as exc:
                failed += 1
                self.logger.warning(f"Skipping row {idx} during indexing | error={exc}")

        if not texts:
            raise IngestionError("No valid chunks available for indexing.")

        self.logger.info(
            f"Indexing started | file={path.name} | total_rows={len(rows)} | valid_chunks={len(texts)}"
        )

        embeddings = self.embedding_provider.embed_documents(texts)
        if len(embeddings) != len(texts):
            raise ValueError("Embedding count does not match valid chunk count.")

        self.vector_store.upsert(
            ids=ids,
            embeddings=embeddings,
            metadatas=metadatas,
            documents=texts,
        )

        elapsed = time.perf_counter() - start
        stats = IndexingStats(
            document_id=document_id,
            filename=filename,
            total_chunks=len(rows),
            embedded=len(embeddings),
            indexed=len(ids),
            failed=failed,
            processing_time_sec=round(elapsed, 3),
        )

        self.logger.info(
            f"Indexing completed | document_id={stats.document_id} | filename={stats.filename} "
            f"| total_chunks={stats.total_chunks} | embedded={stats.embedded} "
            f"| indexed={stats.indexed} | failed={stats.failed} | time_sec={stats.processing_time_sec}"
        )
        return stats