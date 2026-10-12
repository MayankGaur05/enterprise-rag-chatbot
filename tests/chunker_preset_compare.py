from pathlib import Path

from app.ingestion.chunker import DocumentChunker
from app.ingestion.loader import DocumentLoader
from app.ingestion.metadata import MetadataEnricher


def run_compare(file_path: Path) -> None:
    loader = DocumentLoader()
    enricher = MetadataEnricher()
    chunker = DocumentChunker()

    docs = loader.load_documents_from_directory(file_path)
    enrich_docs = enricher.enrich(docs,file_path=file_path, include_ids=True)

    print(f"\n--- {file_path.name}")
    print(f"loaded={len(docs)} enriched={len(enrich_docs)}")

    for preset in ["small", "medium", "large"]:
        chunked_docs, stats = chunker.chunk(enrich_docs, preset=preset)
        print(
            f"\nPreset={preset}"
            f"\n  total_chunks={stats.total_chunks}"
            f"\n  average_chunk_length={stats.average_chunk_length}"
            f"\n  largest_chunk={stats.largest_chunk}"
            f"\n  smallest_chunk={stats.smallest_chunk}"
            f"\n  first_chunk_preview={chunked_docs[0].page_content[:120].replace('\\n', ' ') if chunked_docs  else 'N/A'}"
        )

if __name__ == "__main__":
    raw_dir = Path("data/raw")
    print(f"Running chunker preset comparison on files in {raw_dir.resolve()}")

    # Prefer PDF for realistic multi-page behavior
    candidates = list(raw_dir.glob("*.pdf")) or list(raw_dir.glob("*.docx")) or list(raw_dir.glob("*.txt"))
    if not candidates:
        raise SystemExit("No supported files found in data/raw")
    run_compare(candidates[0])


