from db.abstract_database import AbstractDatabase
from qdrant_client import QdrantClient
from qdrant_client.http import models
from icecream import ic
class QdrantDatabase(AbstractDatabase):
    def __init__(self, qdrant_host: str, qdrant_port: int, collection_name: str, recreate_collection: bool = False):
        self.collection_name = collection_name
        self.recreate_collection = recreate_collection
        self.client = QdrantClient(host=qdrant_host, port=qdrant_port)
        self.__create_collection()


    def __create_collection(self):
        if self.recreate_collection:
            self.client.delete_collection(collection_name=self.collection_name)
        try:
            self.client.create_collection(
                collection_name=self.collection_name,
                vectors_config=models.VectorParams(
                    size=384,
                    distance=models.Distance.COSINE
                )
            )
            return 
        except Exception as e:
            return 

    def get_data(self, limit: int = 10, with_payload: bool = True, with_vectors: bool = False) -> dict:
        return self.client.scroll(
            collection_name=self.collection_name,
            limit=limit,
            with_payload=with_payload,
            with_vectors=with_vectors
        )
    
    def save_data(self, points: list[models.PointStruct]):
        ic(points)
        self.client.upsert(
            collection_name=self.collection_name,
            points=points,
            wait=True
        )
        return True


    def search_data(self, query_vector: list[float], limit: int = 10, with_payload: bool = True, with_vectors: bool = False, type: str = "class") -> list[models.PointStruct]:
        # try:
        search_response = self.client.search(
            collection_name=self.collection_name,
            query_vector=query_vector,
            limit=limit,    
            with_payload=with_payload,
            with_vectors=with_vectors,
            query_filter=models.Filter(
                should=[
                    models.FieldCondition(
                        key="type",
                        match=models.MatchValue(value=type)
                    )
                ]
            )
        )
        return search_response
