from qdrant_client import QdrantClient

class MemoryStore:
    def __init__(self, url="http://localhost:6333"):
        self.client = QdrantClient(url=url)

    def store_embedding(self, tag: str, vector: list):
        self.client.upsert(
            collection_name="embeddings",
            points=[{"id": tag, "vector": vector}]
        )
