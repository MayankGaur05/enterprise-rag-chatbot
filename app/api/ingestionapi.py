from pathlib import Path

from fastapi import APIRouter, File, HTTPException, UploadFile

from app.config import get_settings
from app.core.logging_config import setup_logging
from app.ingestion.pipeline import IngestionPipeline

router = APIRouter()

logger = setup_logging(get_settings().log_level)
settings = get_settings()

pipeline = IngestionPipeline()

@router.post("/upload", summary="Upload Documents for Ingestion", tags=["Ingestion"])
async def upload_documents(file: UploadFile = File(...), preset: str = "small"):
    """
    Endpoint to upload documents for ingestion.

    Parameters
    ----------
    file : UploadFile
        The uploaded file to be processed.
    preset : str, optional
        The chunking preset to use (default is "small").
    Returns
    -------
    dict
        A dictionary containing the status of the ingestion process.
    """
    try:
        if not file.filename:
            raise HTTPException(status_code=400, detail="No file uploaded")

        if preset not in ["small", "medium", "large"]:
            raise HTTPException(status_code=400, detail="Invalid preset value. Must be 'small', 'medium', or 'large'.")

        file_extension = Path(file.filename).suffix.lower()

        if file_extension not in settings.supported_file_extensions:
            raise HTTPException(status_code=400, detail="Unsupported file type. Only PDF, DOCX, and TXT files are allowed.")

        raw_dir = Path("data/raw")
        raw_dir.mkdir(parents=True, exist_ok=True)

        safe_name = Path(file.filename).name

        target_path = raw_dir / safe_name
        content  = await file.read()

        if not content:
            raise HTTPException(status_code=400, detail="Uploaded file is empty.")
        
        target_path.write_bytes(content)

        
        result = pipeline.process(target_path, preset=preset)

        return {
            "filename": result["filename"],
            "status": result["status"],
            "pages": result["pages"],
            "chunks": result["chunks"],
            "processing_time": result["processing_time"],
        }
    except HTTPException:
        raise
    except Exception as exc:
        logger.error(f"Upload failed | file={getattr(file, 'filename', 'unknown')} | error={exc}")
        raise HTTPException(status_code=500, detail="Failed to process uploaded document.") from exc
                