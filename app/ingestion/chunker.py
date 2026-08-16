from dataclasses import dataclass
from statistics import mean

from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter

from app.config import get_settings
from app.core.logging_config import setup_logging


@dataclass
class ChunkStats:
    """
    A dataclass to hold statistics about the chunking process.
    """
    total_chunks: int
    average_chunk_length: float
    largest_chunk: int
    smallest_chunk: int 

class DocumentChunker:
    """
    A class to handle the chunking of documents into smaller pieces.
    """

    def __init__(self) -> None:
            """
            Initialize the DocumentChunker.

            This constructor sets up the logging configuration and initializes the text splitter.
            """
            self.PRESETS = {
                            "small": {"chunk_size": 500, "chunk_overlap": 100},
                            "medium": {"chunk_size": 800, "chunk_overlap": 100},    
                            "large": {"chunk_size": 1000, "chunk_overlap": 200},
                      }
            settings = get_settings()
            self.logger = setup_logging(settings.log_level)

    def chunk(self, documents: list[Document], preset: str = "small")  -> tuple[list[Document], ChunkStats]:
        """
            Chunk the provided documents into smaller pieces based on the specified preset.
        """      
        if preset not in self.PRESETS:
            self.logger.warning(f"Invalid preset '{preset}'. Valid options are: {list(self.PRESETS.keys())}")
            raise ValueError(f"Invalid preset '{preset}'. Valid options are: {list(self.PRESETS.keys())}")

        cfg = self.PRESETS[preset]
        chunk_size = cfg["chunk_size"]
        chunk_overlap = cfg["chunk_overlap"]

        self.logger.info(f"Chunking documents with preset '{preset}': chunk_size={chunk_size}, chunk_overlap={chunk_overlap}")
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            separators=["\n\n", "\n", " ", ""]
        )

        chunks = text_splitter.split_documents(documents)
        chunk_lengths = [len(c.page_content) for c in chunks] if chunks else [0]

        stats = ChunkStats(
            total_chunks=len(chunks),
            average_chunk_length=mean(chunk_lengths) if chunk_lengths else 0,
            largest_chunk=max(chunk_lengths) if chunk_lengths else 0,
            smallest_chunk=min(chunk_lengths) if chunk_lengths else 0,
        )

        self.logger.info(f"Chunking complete: total_chunks={stats.total_chunks}, average_chunk_length={stats.average_chunk_length}, largest_chunk={stats.largest_chunk}, smallest_chunk={stats.smallest_chunk}")   
        return chunks, stats
