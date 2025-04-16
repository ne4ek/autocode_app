from consts import QDRANT_HOST, QDRANT_PORT, COLLECTION_NAME
from db.qdrant.qdrant_database import QdrantDatabase

qdrant_database = QdrantDatabase(QDRANT_HOST, QDRANT_PORT, COLLECTION_NAME)