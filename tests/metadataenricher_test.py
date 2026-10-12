from pathlib import Path

from app.ingestion.loader import DocumentLoader
from app.ingestion.metadata import MetadataEnricher

raw_dir = Path("data/raw")
loader = DocumentLoader()
enricher = MetadataEnricher()

required_keys = {
    "filename",
    "file_type",
    "page_number",
    "source",
    "created_at",
    "document_id",
    "chunk_id",
}

test_files = []
for ext in [".txt", ".pdf", ".docx"]:
    matches = list(raw_dir.glob(f"*{ext}"))
    if matches:
        test_files.append(matches[0])

if not test_files:
    raise SystemExit("No test files found in data/raw for txt/pdf/docx")

print("Running metadata enrichment validation...")
for file_path in test_files:
    print(f"\n--- {file_path.name}")
    docs =  loader.load_documents_from_directory(file_path)
    enriched = enricher.enrich(docs, file_path=file_path, include_ids=True)

    print(f"loaded={len(docs)} enriched={len(enriched)}")
    sample = enriched[0].metadata
    missing = sorted(required_keys - set(sample.keys()))
    if missing:
        print(f"FAIL missing keys: {missing}")
    else:
        print("PASS required keys present")
        print({k: sample.get(k) for k in sorted(required_keys)})