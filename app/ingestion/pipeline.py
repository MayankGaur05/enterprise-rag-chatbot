from __future__ import annotations

import time
from pathlib import Path

from app.config import get_settings
from app.core.logging_config import setup_logging
from app.ingestion.chunker import DocumentChunker
from app.ingestion.loader import DocumentLoader
from app.ingestion.metadata import MetadataEnricher
from app.utils.fileutil import ProcessedChunkWriter


class IngestionPipeline:
    """
    IngestionPipeline class to handle the ingestion of documents from a specified directory.
    """

    def __init__(self) -> None:
        """
            Initialize the IngestionPipeline.
        """
        settings = get_settings() 
        self.logger = setup_logging(settings.log_level)
        self.loader = DocumentLoader()
        self.enricher = MetadataEnricher()
        self.chunker = DocumentChunker()
        self.writer = ProcessedChunkWriter() 
        
    def process(self, file_path: str | Path, preset: str = "small") -> None:
        """
            Process the documents in the specified directory.

            Parameters
            ----------
            file_path : str | Path
                The path to the directory containing documents to be processed.
            preset : str, optional
                The chunking preset to use (default is "small").
        """
        start_time = time.perf_counter()
        path = Path(file_path)

        self.logger.info(f"Ingestion started | file={path.name} | preset={preset}")

        # Load documents from the specified file path
        documents = self.loader.load_documents_from_directory(path)

        # Enrich documents with metadata
        enriched_documents = self.enricher.enrich(documents, file_path)

        # Chunk the enriched documents
        chunks, stats = self.chunker.chunk(enriched_documents, preset=preset)

        output_path = self.writer.save_document_chunks(
            filename=path.name,
            chunks=chunks,
            document_id=enriched_documents[0].metadata.get("document_id"),
        )

        elapsed = round(time.perf_counter() - start_time, 3)

        result = {
            "filename": path.name,
            "status": "success",
            "pages": len(enriched_documents),
            "chunks": stats.total_chunks,
            "processing_time": elapsed,
            "output_file": str(output_path),
        }

        self.logger.info(
            f"Ingestion completed | file={path.name} | pages={result['pages']} | chunks={result['chunks']} | time={elapsed}s"
        )
        return result
