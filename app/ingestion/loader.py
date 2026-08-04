from pathlib import Path
from datetime import datetime, timezone
from typing import Callable

from langchain_core.documents import Document

from app.config import get_settings
from app.core.logging_config import setup_logging

from app.ingestion.exceptions import (
    UnsupportedFileTypeError,       
    DocumentLoadError,
    EmptyDocumentError
)


class DocumentLoader:
    """
    A class to load documents from a specified directory using a provided loader function.
    """
    
    SUPPORTED_EXTENSIONS = get_settings().supported_file_extensions
    def __init__(self) -> None:
        """
        Initialize the DocumentLoader.

        This constructor sets up the logging configuration.

        Loads enterprise documents and returns LangChain Document objects.
        """
        settings = get_settings()
        self.logger = setup_logging(settings.log_level)

        # Define a mapping of supported file extensions to their corresponding loader methods.
        self._loaders: dict[str, Callable[[Path], list[Document]]] = {
            ".txt": self._load_txt,
            ".pdf": self._load_pdf,
            ".docx": self._load_docx,
        }

    def _detect_extension(self, file_path: Path) -> str:
        ext = file_path.suffix.lower().strip()
        self.logger.info(f"Detecting file type for: {file_path.name} -> {ext}")
        if ext not in self.SUPPORTED_EXTENSIONS:
            raise UnsupportedFileTypeError(
                f"Unsupported file type: '{ext}'. Supported: {sorted(self.SUPPORTED_EXTENSIONS)}"
            )
        return ext

    # Run 3/4 will implement these methods
    def _load_txt(self, file_path: Path) -> list[Document]:
        self.logger.info(f"Loading TXT document: {file_path.name}")
        try:
            content = file_path.read_text(encoding="utf-8")
        except Exception as e:
            raise DocumentLoadError(f"Failed to load TXT document: {file_path.name}") from e

        if not content or not content.strip():
            self.logger.warning(f"Document is empty: {file_path.name}")
            raise EmptyDocumentError(f"Document is empty: {file_path.name}")

        doc = Document(
            page_content=content,
            metadata={
                "source": str(file_path),
                "filename": file_path.name,
                "file_type": file_path.suffix.lower(),
                "file_size": file_path.stat().st_size,
                "page_number": 1,  # For TXT, we consider it as a single page
                "created_at": datetime.now(timezone.utc).isoformat(),
            },
        )

        return [doc]

    def _load_pdf(self, file_path: Path) -> list[Document]:
        """
        Load a PDF document and return a list of LangChain Document objects, one for each page.
        
        Args:
            file_path (Path): The path to the PDF file.
        """

        self.logger.info(f"Loading PDF document: {file_path.name}")
        try:
            from pypdf import PdfReader
            reader = PdfReader(str(file_path))
            documents = []
            for i, page in enumerate(reader.pages):
                content = page.extract_text() or ""
                if not content.strip():
                    self.logger.warning(f"Skipping empty PDF page {i + 1} in: {file_path.name}")
                    continue

                doc = Document(
                    page_content=content,
                    metadata={
                        "source": str(file_path),
                        "filename": file_path.name,
                        "file_type": file_path.suffix.lower(),
                        "file_size": file_path.stat().st_size,
                        "page_number": i + 1,
                        "created_at": datetime.now(timezone.utc).isoformat()
                    }
                )
                documents.append(doc)
        except Exception as e:
            raise DocumentLoadError(f"Failed to load PDF document: {file_path.name}") from e

        if not documents:
            self.logger.warning(f"PDF has no readable content: {file_path.name}")
            raise EmptyDocumentError(f"Document is empty: {file_path.name}")

        return documents

    def _load_docx(self, file_path: Path) -> list[Document]:
        """
        Load a DOCX document and return a list of LangChain Document objects, one for each paragraph.
        Args:
            file_path (Path): The path to the DOCX file.
        """
        self.logger.info(f"Loading DOCX document: {file_path.name}")
        try:
            import docx2txt
            content = docx2txt.process(str(file_path))
        except Exception as e:
            raise DocumentLoadError(f"Failed to load DOCX document: {file_path.name}") from e

        if not content or not content.strip():
            self.logger.warning(f"Document is empty: {file_path.name}")
            raise EmptyDocumentError(f"Document is empty: {file_path.name}")

        doc = Document(
            page_content=content,
            metadata={
                "source": str(file_path),
                "filename": file_path.name,
                "file_type": file_path.suffix.lower(),
                "file_size": file_path.stat().st_size,
                "page_number": 1,  # For DOCX, we consider it as a single page
                "created_at": datetime.now(timezone.utc).isoformat(),
            }
        )

        return [doc]

def load_documents_from_directory(self, file_path: str | Path) -> list[Document]:
    """
    Load all supported documents from a specified directory.

    Args:
        file_path (Path): The path of the file.
    """

    path = Path(file_path)
    if not path.exists():
        self.logger.warning(f"File not found: {file_path}")
        raise DocumentLoadError(f"File not found: {file_path}")
    if not path.is_file():
        self.logger.warning(f"Path is not a file: {file_path}")
        raise DocumentLoadError(f"Path is not a file: {file_path}")

    ext = self._detect_extension(path)
    self.logger.info(f"Using loader for extension: {ext}")
    loader_fn = self._loaders.get(ext)
    if not loader_fn:
        self.logger.warning(f"No loader found for extension: {ext}")
        raise UnsupportedFileTypeError(f"No loader found for extension: {ext}")

    documents = loader_fn(path)
    if not documents:
            self.logger.warning(f"No document content extracted: {path.name}")
            raise EmptyDocumentError(f"No readable content extracted from: {path.name}")

    self.logger.info(
            f"Loaded document successfully: {path.name} | type={ext} | chunks={len(documents)}"
        )
    return documents