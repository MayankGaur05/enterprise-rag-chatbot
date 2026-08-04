class IngestionError(Exception):
    """Base class for ingestion errors."""
    pass

class UnsupportedFileTypeError(IngestionError):
    """Raised when an unsupported file type is encountered."""
    pass

class DocumentLoadError(IngestionError):
    """Raised when there is an error loading a document."""
    pass

class EmptyDocumentError(IngestionError):
    """Raised when a document is empty."""
    pass