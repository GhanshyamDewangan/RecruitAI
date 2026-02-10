
from langchain_community.vectorstores import Chroma
from langchain_huggingface import HuggingFaceEmbeddings
from ..core.config import get_settings
import os
import shutil

settings = get_settings()

class VectorService:
    def __init__(self):
        self.embeddings = HuggingFaceEmbeddings(model_name=settings.embedding_model)
        self.persist_directory = settings.db_persist_dir
        
        # Ensure directory exists or create fresh instance
        if not os.path.exists(self.persist_directory):
            os.makedirs(self.persist_directory)
            
        self.db = Chroma(
            persist_directory=self.persist_directory,
            embedding_function=self.embeddings
        )

    def add_texts(self, texts, metadatas):
        """Add documents to the vector store."""
        return self.db.add_texts(texts=texts, metadatas=metadatas)

    def search(self, query: str, k: int = 5):
        """Perform semantic search."""
        return self.db.similarity_search_with_score(query, k=k)

    def reset(self):
        """Clear the vector database completely."""
        try:
            # Soft reset: Delete collection content instead of folder
            if self.db:
                try:
                    self.db.delete_collection()
                except Exception as e:
                    print(f"Collection delete warning: {e}")
            
            # Re-initialize
            self.db = Chroma(
                persist_directory=self.persist_directory,
                embedding_function=self.embeddings
            )
        except Exception as e:
            print(f"Vector DB Reset Error: {e}")

vector_service = VectorService()
