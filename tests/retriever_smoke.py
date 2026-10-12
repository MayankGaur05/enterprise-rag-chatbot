from app.retrieval.retriever import Retriever
from app.vectorstore.chroma_db import ChromaVectorStore
from tests.document_indexer_smoke import FakeEmbeddingProvider

r= Retriever(
        embedding_provider=FakeEmbeddingProvider(), 
        vector_store=ChromaVectorStore(
            collection_name='sprint3_indexer_smoke'));

out=r.search('Continous Integration and Continous Deployment', top_k=5); print({'results':len(out),'first_score':out[0].score if out else None,'first_filename':(out[0].metadata.get('filename') if out else None)}); print(out[0].content[:160] if out else '')