from sentence_transformers import SentenceTransformer


class EmbeddingService:
    def __init__(self, model: SentenceTransformer):
        self.model = model

    def embed_text(self, text: str) -> list[float]:
        return self.model.encode(text).tolist()
