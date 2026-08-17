from abc import ABC, abstractmethod


class EmbeddingProvider(ABC):
    """
    Abstract base class for embedding providers.
    """

    @abstractmethod
    def embed_documents(self, texts: list[str]) -> list[list[float]]:
        """
        Abstract method to embed a list of documents.

        Args:
            texts (list[str]): A list of documents to be embedded.

        Returns:
            list[list[float]]: A list of embeddings corresponding to the input documents.
        """

    @abstractmethod   
    def embed_query(self, text: str) -> list[float]:
        """
        Abstract method to embed a single query.

        Args:
            text (str): A single query to be embedded.

        Returns:
            list[float]: An embedding corresponding to the input query.
        """
