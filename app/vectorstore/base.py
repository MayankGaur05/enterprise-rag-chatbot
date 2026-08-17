from abc import ABC, abstractmethod
from typing import Any


class VectorStore(ABC):
    """
    Abstract base class for vector stores.
    """

    @abstractmethod
    def upsert(self, 
               ids: list[str], 
               embeddings: list[list[float]],
               metadatas: list[dict[str, Any]] | None = None, 
               documents: list[str] | None = None) -> None:
        """
        Abstract method to upsert documents into the vector store.

        Args:
            ids (list[str]): A list of document IDs to be upserted.
            embeddings (list[list[float]]): A list of embeddings corresponding to the document IDs.
            metadatas (list[dict[str, Any]] | None): Optional metadata for the documents.
            documents (list[str] | None): Optional full documents to be upserted.
        """

    @abstractmethod
    def query(self, query_embedding: list[float], top_k: int = 5) -> list[dict[str, Any]]:
        """
        Abstract method to query the vector store.

        Args:
            query_embedding (list[float]): The embedding of the query.
            top_k (int): The number of top results to return.

        Returns:
            list[dict]: A list of documents that are most similar to the query embedding.
        """

    @abstractmethod
    def delete_by_document_id(self, document_id: str) -> None:
        """
        Abstract method to delete a document from the vector store by its ID.

        Args:
            document_id (str): The ID of the document to be deleted.
        """

    @abstractmethod
    def count(self) -> int:
        """
        Abstract method to count the number of documents in the vector store.

        Returns:
            int: The total number of documents in the vector store.
        """
