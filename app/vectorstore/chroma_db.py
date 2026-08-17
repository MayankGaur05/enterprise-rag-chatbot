from __future__ import annotations

from pathlib import Path
from typing import Any

import chromadb

from app.config import get_settings
from app.core.logging_config import setup_logging
from app.ingestion.exceptions import IngestionError
from app.vectorstore.base import VectorStore

settings = get_settings()
logger = setup_logging(settings.log_level)


class ChromaVectorStore(VectorStore):
    def __init__(
        self,
        collection_name: str | None = None,
        persist_directory: str | Path | None = None,
    ) -> None:
        self.collection_name = collection_name or settings.vector_collection_name
        self.persist_directory = Path(persist_directory or settings.vector_store_dir)
        self.persist_directory.mkdir(parents=True, exist_ok=True)

        self.client = chromadb.PersistentClient(path=str(self.persist_directory))
        self.collection = self.client.get_or_create_collection(
            name=self.collection_name,
            metadata={"hnsw:space": "cosine"},
        )

        logger.info(
            f"Chroma initialized | collection={self.collection_name} | path={self.persist_directory}"
        )

    def upsert(
        self,
        ids: list[str],
        embeddings: list[list[float]],
        metadatas: list[dict[str, Any]] | None = None,
        documents: list[str] | None = None,
    ) -> None:
        if not ids or not embeddings:
            return
        if len(ids) != len(embeddings):
            raise IngestionError("ids and embeddings length mismatch")
        if metadatas is not None and len(metadatas) != len(ids):
            raise IngestionError("metadatas and ids length mismatch")
        if documents is not None and len(documents) != len(ids):
            raise IngestionError("documents and ids length mismatch")
        if metadatas is not None:
            self.validate_metadatas(metadatas)
            self.validate_ids_against_metadatas(ids, metadatas)
            
        self.collection.upsert(
            ids=ids,
            embeddings=embeddings,
            metadatas=metadatas,
            documents=documents,
        )

    def query(self, query_embedding: list[float], top_k: int = 5) -> list[dict[str, Any]]:
        results = self.collection.query(
            query_embeddings=[query_embedding],
            n_results=top_k,
            include=["documents", "metadatas", "distances"],
        )

        docs = (results.get("documents") or [[]])[0]
        metas = (results.get("metadatas") or [[]])[0]
        dists = (results.get("distances") or [[]])[0]

        output: list[dict[str, Any]] = []
        for doc, meta, dist in zip(docs, metas, dists):
            score = 1.0 - float(dist) if dist is not None else 0.0
            output.append(
                {
                    "content": doc or "",
                    "score": score,
                    "metadata": meta or {},
                }
            )
        return output

    def delete_by_document_id(self, document_id: str) -> None:
        self.collection.delete(where={"document_id": document_id})

    def count(self) -> int:
        return int(self.collection.count())

    @staticmethod
    def _is_scalar_serializable(value: Any) -> bool:
        return value is None or isinstance(value, (str, int, float, bool))

    @classmethod
    def validate_metadatas(cls, metadatas: list[dict[str, Any]]) -> bool:
        required_keys = {
            "document_id",
            "chunk_id",
            "filename",
            "file_type",
            "page_number",
            "source",
            "created_at",
        }

        if not isinstance(metadatas, list):
            raise IngestionError("metadatas must be a list of dictionaries")

        for idx, metadata in enumerate(metadatas, start=1):
            if not isinstance(metadata, dict):
                raise IngestionError(f"metadata at index {idx} must be a dictionary")

            missing = sorted(required_keys - set(metadata.keys()))
            if missing:
                raise IngestionError(
                    f"metadata at index {idx} is missing required fields: {missing}"
                )

            document_id = metadata.get("document_id")
            chunk_id = metadata.get("chunk_id")

            if not isinstance(document_id, str) or not document_id.strip():
                raise IngestionError(
                    f"metadata at index {idx} has invalid document_id: must be a non-empty string"
                )

            if not isinstance(chunk_id, str) or not chunk_id.strip():
                raise IngestionError(
                    f"metadata at index {idx} has invalid chunk_id: must be a non-empty string"
                )

            for key, value in metadata.items():
                if not cls._is_scalar_serializable(value):
                    raise IngestionError(
                        f"metadata at index {idx} has non-serializable value for '{key}': {type(value).__name__}"
                    )

        return True

    @staticmethod
    def _expected_vector_id(metadata: dict[str, Any]) -> str:
        return f"{metadata['document_id']}::{metadata['chunk_id']}"

    @classmethod
    def validate_ids_against_metadatas(
        cls,
        ids: list[str],
        metadatas: list[dict[str, Any]],
    ) -> bool:
        if len(ids) != len(metadatas):
            raise IngestionError("ids and metadatas length mismatch")

        for idx, (vector_id, metadata) in enumerate(zip(ids, metadatas), start=1):
            expected = cls._expected_vector_id(metadata)
            if vector_id != expected:
                raise IngestionError(
                    f"id mismatch at index {idx}: expected '{expected}', got '{vector_id}'"
                )
        return True