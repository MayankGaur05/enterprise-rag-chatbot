from collections.abc import Iterable
from datetime import datetime, timezone
from pathlib import Path
from uuid import uuid4

from langchain_core.documents import Document

from app.config import get_settings
from app.core.logging_config import setup_logging


class MetadataEnricher:
    """
    Methods
    -------
    enrich(
        document: Iterable[Document],
        file_path: str | Path,
        include_ids: bool = True,
    ) -> list[Document]
        Enriches documents with metadata.
    """

    def __init__(self) -> None:
        settings = get_settings()
        self.logger = setup_logging(settings.log_level)

        self.settings = settings

    def enrich(
        self,
        document: Iterable[Document],
        file_path: str | Path,
        include_ids: bool = True,
    ) -> list[Document]:
        path = Path(file_path)
        created_at = datetime.now(timezone.utc).isoformat()
        file_type = path.suffix.lower().strip()
        filename = path.name
        source = str(path.resolve())

        document_id = str(uuid4()) if include_ids else None

        enriched_docs: list[Document] = []
        for index, doc in enumerate(document, start=1):
            metadata = dict(doc.metadata or {})  # Copy existing metadata

            page_number = metadata.get("page_number", index)

            metadata.update(
                {
                    "source": source,
                    "filename": filename,
                    "file_type": file_type,
                    "file_size": path.stat().st_size,
                    "page_number": page_number,
                    "created_at": created_at,
                }
            )

            # Sprint says chunk_id/document_id later.
            if include_ids:
                metadata.setdefault("document_id", document_id)
                metadata.setdefault("chunk_id", None)

            enriched_docs.append(
                Document(
                    page_content=doc.page_content,
                    metadata=metadata,
                )
            )

        self.logger.info(
            f"Metadata enrichment complete | file={filename} | docs={len(enriched_docs)}"
        )
        return enriched_docs


