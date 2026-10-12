# enterprise-rag-chatbot
A chatbot application based on RAG pattern

## Run the Streamlit Application

```bash
streamlit run frontend/app.py
```

## Configuration

1. Copy .env.example to .env
2. Update values for your machine

Run backend:

```bash
uvicorn app.api.main:app --host 0.0.0.0 --port 8000 --reload
```

Run frontend:

```bash
streamlit run frontend/app.py
```

Note:
OS-level environment variables override values in .env.

## Test Scripts

Run all test scripts from the repository root:

```powershell
python -m tests.metadataenricher_test
python -m tests.chunker_preset_compare
python -m tests.chunk_stats_summary
python -m tests.pipeline_save_smoke
```

### 1) metadataenricher_test.py

Command:

```powershell
python -m tests.metadataenricher_test
```

Summary:
Validates metadata enrichment output for sample TXT, PDF, and DOCX files. It checks that required metadata fields exist in enriched documents: filename, file_type, page_number, source, created_at, document_id, and chunk_id.

### 2) chunker_preset_compare.py

Command:

```powershell
python -m tests.chunker_preset_compare
```

Summary:
Runs chunking with three presets (small, medium, large) on a sample document and prints a side-by-side comparison of total chunks, average chunk size, largest/smallest chunk, and first chunk preview.

### 3) chunk_stats_summary.py

Command:

```powershell
python -m tests.chunk_stats_summary
```

Summary:
Aggregates ingestion statistics across all supported files in data/raw for a selected preset. It prints total documents, total pages, total chunks, average chunk length, largest chunk, and smallest chunk.

### 4) pipeline_save_smoke.py

Command:

```powershell
python -m tests.pipeline_save_smoke
```

Summary:
Performs an end-to-end smoke run of loader -> metadata enricher -> chunker -> JSON writer for one input document, then saves processed chunk output to data/processed.

## Ingestion API Example

Endpoint:
POST /api/upload?preset=small

Example request (PowerShell):

```powershell
curl.exe -X POST "http://127.0.0.1:8000/api/upload?preset=small" -F "file=@data/raw/MayankGaur-Azure1.pdf"
```

Example success response:

```json
{
	"filename": "MayankGaur-Azure1.pdf",
	"status": "success",
	"pages": 3,
	"chunks": 9,
	"processing_time": 0.161
}
```

Example failure response (empty file):

```json
{
	"detail": "Uploaded file is empty."
}
```

## Known Limitations

- Current ingestion supports only .pdf, .docx, and .txt.
- Scanned or image-only PDFs are not OCR processed in this sprint.
- Uploaded files are saved to data/raw before processing.
- Tests are currently script-style validation runs; a full pytest unit test suite is pending.
