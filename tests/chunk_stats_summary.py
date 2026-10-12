from pathlib import Path
from statistics import mean

from app.ingestion.chunker import DocumentChunker
from app.ingestion.loader import DocumentLoader
from app.ingestion.metadata import MetadataEnricher


def run_summary(preset: str = "small") -> None:
    raw_dir = Path("data/raw")
    loader = DocumentLoader()
    enricher = MetadataEnricher()
    chunker = DocumentChunker()

    supported = [".txt", ".pdf", ".docx"]
    files = [p for p in raw_dir.iterdir() if p.is_file() and p.suffix.lower() in supported]

    if not files:
        raise SystemExit("No supported files found in data/raw")

    total_documents = 0
    total_pages = 0
    total_chunks = 0
    chunk_lengths: list[int] = []

    for file_path in files:
        docs = loader.load_documents_from_directory(file_path)
        enriched_docs = enricher.enrich(docs, file_path=file_path, include_ids=True)
        chunks, _ = chunker.chunk(enriched_docs, preset=preset)

        total_documents += 1
        total_pages += len(enriched_docs)
        total_chunks += len(chunks)
        chunk_lengths.extend([len(c.page_content) for c in chunks])

    avg_len = round(mean(chunk_lengths), 2) if chunk_lengths else 0
    largest = max(chunk_lengths) if chunk_lengths else 0
    smallest = min(chunk_lengths) if chunk_lengths else 0

    print("\nIngestion Chunk Statistics")
    print(f"Preset: {preset}")
    print(f"Total documents: {total_documents}")
    print(f"Total pages: {total_pages}")
    print(f"Total chunks: {total_chunks}")
    print(f"Average chunk length: {avg_len}")
    print(f"Largest chunk: {largest}")
    print(f"Smallest chunk: {smallest}")


if __name__ == "__main__":
    run_summary("large") # Change preset as needed: "small", "medium", "large"