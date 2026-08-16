from pathlib import Path

from app.ingestion.chunker import DocumentChunker
from app.ingestion.loader import DocumentLoader
from app.ingestion.metadata import MetadataEnricher
from app.utils.fileutil import ProcessedChunkWriter


def run_once(preset: str = "small") -> None:
    raw_dir = Path("data/raw")
    candidates = list(raw_dir.glob("*.pdf")) or list(raw_dir.glob("*.docx")) or list(raw_dir.glob("*.txt"))
    if not candidates:
        raise SystemExit("No supported input file found in data/raw")

    file_path = candidates[0]
    print(f"Using file: {file_path.name}")

    loader = DocumentLoader()
    enricher = MetadataEnricher()
    chunker = DocumentChunker()
    writer = ProcessedChunkWriter()

    # NOTE: use whichever public method exists in your loader class:
    # docs = loader.load(file_path)
    docs = loader.load_documents_from_directory(file_path)

    enriched_docs = enricher.enrich(docs, file_path=file_path, include_ids=True)
    chunks, stats = chunker.chunk(enriched_docs, preset=preset)

    output_path = writer.save_document_chunks(
        filename=file_path.name,
        chunks=chunks,
        document_id=enriched_docs[0].metadata.get("document_id"),
    )

    print("\nSaved successfully")
    print(f"Output: {output_path}")
    print(
        f"Stats -> total_chunks={stats.total_chunks}, "
        f"avg_len={stats.average_chunk_length}, "
        f"largest={stats.largest_chunk}, smallest={stats.smallest_chunk}"
    )


if __name__ == "__main__":
    run_once("small")