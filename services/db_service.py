from db.qdrant.qdrant_database import QdrantDatabase
from qdrant_client.http import models
from services.embedding_service import EmbeddingService
class DBService:
    def __init__(self, qdrant_database: QdrantDatabase, embedding_service: EmbeddingService):
        self.db = qdrant_database
        self.embedding_service = embedding_service

    def search_data(self, text: str, limit: int = 1, type: str = None) -> list[models.PointStruct]:
        query_vector = self.embedding_service.embed_text(text)
        return self.db.search_data(query_vector, limit, with_payload=True, with_vectors=False, type=type)

    def get_payload_from_text(self, text: str, limit: int = 1) -> list[models.PointStruct]:
        similar_objects = self.search_data(text, limit)
        if similar_objects:
            return similar_objects
        return None

    def get_class_payload_from_text(self, text: str, limit: int = 1) -> list[models.PointStruct]:
        similar_objects = self.search_data(text, limit, type="class")
        if similar_objects:
            return similar_objects
        return None
    
    def get_method_payload_from_text(self, text: str, limit: int = 1) -> list[models.PointStruct]:
        similar_objects = self.search_data(text, limit, type="method")
        if similar_objects:
            return similar_objects
        return None

    def save_data(self, text: str, payload: dict):
        pass