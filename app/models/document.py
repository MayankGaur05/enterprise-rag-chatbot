from dataclasses import dataclass


@dataclass
class IndexingStats:
    document_id: str
    filename: str
    total_chunks: int
    embedded: int
    indexed: int
    failed: int
    processing_time_sec: float