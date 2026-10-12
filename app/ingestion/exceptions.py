class IngestionError(Exception):
    """Base class for ingestion errors."""

class UnsupportedFileTypeError(IngestionError):
    """Raised when an unsupported file type is encountered."""

class DocumentLoadError(IngestionError):
    """Raised when there is an error loading a document."""

class EmptyDocumentError(IngestionError):
    """Raised when a document is empty."""
