from __future__ import annotations

import json
from pathlib import Path
from typing import Any
from uuid import uuid4

from langchain_core.documents import Document

from app.config import get_settings
from app.core.logging_config import setup_logging


class ProcessedChunkWriter:
    """
    A class to write processed chunks to a JSON file.

    Methods
    -------
    write_chunks(chunks: list[Document], output_file: str | Path) -> None
        Writes the provided chunks to the specified output file in JSON format.
    """

    def __init__(self) -> None:
        """
        Initialize the ProcessedChunkWriter.

        This constructor sets up the logging configuration.
        """
        settings = get_settings()
        self.logger = setup_logging(settings.log_level)
        self.output_dir = Path(settings.data_dir) / "processed"
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def _safe_stem(self, filename: str) -> str:
        """
        Generate a safe stem for the output filename by removing special characters.

        Parameters
        ----------
        filename : str
            The original filename.

        Returns
        -------
        str
            A safe stem for the output filename.
        """
        return Path(filename).stem.replace(" ", "_")

    def _safe_text(self, value: str) -> str:
        # Replace invalid surrogates with safe replacement chars
        return value.encode("utf-8", errors="replace").decode("utf-8")

    def _sanitize_metadata(self, obj):
        if isinstance(obj, str):
            return self._safe_text(obj)
        if isinstance(obj, dict):
            return {k: self._sanitize_metadata(v) for k, v in obj.items()}
        if isinstance(obj, list):
            return [self._sanitize_metadata(v) for v in obj]
        return obj

    def to_serializable(self, chunks: list[Document], document_id: str | None = None) -> list[dict[str, Any]]:
        """
        Convert a list of Document objects to a serializable format.

        Parameters
        ----------
        chunks : list[Document]
            The list of Document objects to convert.

        Returns
        -------
        list[dict[str, Any]]
            A list of dictionaries representing the chunks.
        """
        doc_id = document_id or str(uuid4())
        rows: list[dict[str, Any]] = []

        for idx, chunk in enumerate(chunks, start=1):
            metadata = dict(chunk.metadata or {})
            metadata = self._sanitize_metadata(metadata)

            content = self._safe_text(chunk.page_content or "")
            metadata["document_id"] = metadata.get("document_id") or doc_id

            chunk_id = metadata.get("chunk_id") or f"{metadata['document_id']}_chunk_{idx:05d}"
            metadata["chunk_id"] = chunk_id

            rows.append(
                {
                    "document_id": metadata["document_id"],
                    "chunk_id": chunk_id,
                    "content": content,
                    "metadata": metadata,
                }
            )

        return rows

    def save_document_chunks(
        self,
        filename: str,
        chunks: list[Document],
        document_id: str | None = None,
    ) -> Path:
        rows = self.to_serializable(chunks=chunks, document_id=document_id)
        safe_name = self._safe_stem(filename)
        out_path = self.output_dir / f"{safe_name}.chunks.json"

        out_path.write_text(json.dumps(rows, indent=2, ensure_ascii=False), encoding="utf-8")
        self.logger.info(f"Saved processed chunks | file={filename} | chunks={len(rows)} | path={out_path}")
        return out_path