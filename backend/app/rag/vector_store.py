"""
Vector store using ChromaDB for semantic document retrieval.
"""
import uuid
from typing import List, Dict, Any, Optional
import structlog

from app.config import settings
from app.services.document_processor import DocumentChunk
from app.services.embedding_service import get_embedding_provider

logger = structlog.get_logger()


class VectorStore:
    """ChromaDB-backed vector store for document chunks."""

    def __init__(self):
        self._client = None
        self._collection = None
        self._embedding_provider = None

    def _get_client(self):
        if self._client is None:
            import chromadb
            from chromadb.config import Settings as ChromaSettings
            self._client = chromadb.PersistentClient(
                path=settings.CHROMA_PERSIST_DIR,
                settings=ChromaSettings(anonymized_telemetry=False),
            )
        return self._client

    def _get_collection(self):
        if self._collection is None:
            client = self._get_client()
            self._collection = client.get_or_create_collection(
                name=settings.CHROMA_COLLECTION_NAME,
                metadata={"hnsw:space": "cosine"},
            )
        return self._collection

    def _get_embedding_provider(self):
        if self._embedding_provider is None:
            self._embedding_provider = get_embedding_provider()
        return self._embedding_provider

    async def add_chunks(self, chunks: List[DocumentChunk]) -> None:
        """Embed and store document chunks in ChromaDB."""
        if not chunks:
            return

        collection = self._get_collection()
        provider = self._get_embedding_provider()

        # Batch processing
        batch_size = 50
        for i in range(0, len(chunks), batch_size):
            batch = chunks[i : i + batch_size]
            texts = [c.text for c in batch]
            embeddings = await provider.embed(texts)

            ids = [c.chunk_id for c in batch]
            metadatas = [
                {
                    "document_id": c.document_id,
                    "page": c.page,
                    "section": c.section,
                    "section_index": c.section_index,
                    "chunk_index": c.chunk_index,
                }
                for c in batch
            ]

            collection.add(
                ids=ids,
                embeddings=embeddings,
                documents=texts,
                metadatas=metadatas,
            )

        logger.info(
            "Chunks added to vector store",
            count=len(chunks),
            document_id=chunks[0].document_id if chunks else None,
        )

    async def query(
        self,
        query_text: str,
        document_id: Optional[str] = None,
        document_ids: Optional[List[str]] = None,
        n_results: int = None,
    ) -> List[Dict[str, Any]]:
        """
        Semantic search with optional document filter.
        Returns ranked list of {text, page, section, document_id, score}.
        """
        if n_results is None:
            n_results = settings.MAX_CHUNKS_PER_QUERY

        collection = self._get_collection()
        provider = self._get_embedding_provider()

        query_embedding = await provider.embed_query(query_text)

        # Build where filter
        where = None
        if document_id:
            where = {"document_id": document_id}
        elif document_ids:
            where = {"document_id": {"$in": document_ids}}

        try:
            results = collection.query(
                query_embeddings=[query_embedding],
                n_results=min(n_results, self._get_collection_count(document_id)),
                where=where,
                include=["documents", "metadatas", "distances"],
            )
        except Exception as e:
            logger.error("ChromaDB query failed", error=str(e))
            return []

        output = []
        if results["documents"] and results["documents"][0]:
            for doc, meta, dist in zip(
                results["documents"][0],
                results["metadatas"][0],
                results["distances"][0],
            ):
                output.append(
                    {
                        "text": doc,
                        "page": meta.get("page", 0),
                        "section": meta.get("section", ""),
                        "document_id": meta.get("document_id", ""),
                        "chunk_index": meta.get("chunk_index", 0),
                        "score": 1 - dist,  # Convert distance to similarity
                    }
                )

        # Sort by score descending
        output.sort(key=lambda x: x["score"], reverse=True)
        return output

    def _get_collection_count(self, document_id: Optional[str] = None) -> int:
        """Get chunk count, used to cap n_results."""
        try:
            collection = self._get_collection()
            count = collection.count()
            return max(1, min(count, settings.MAX_CHUNKS_PER_QUERY))
        except Exception:
            return settings.MAX_CHUNKS_PER_QUERY

    async def delete_document(self, document_id: str) -> None:
        """Remove all chunks for a document."""
        collection = self._get_collection()
        try:
            collection.delete(where={"document_id": document_id})
            logger.info("Document deleted from vector store", document_id=document_id)
        except Exception as e:
            logger.error("Failed to delete from vector store", error=str(e))


# Singleton instance
_vector_store: Optional[VectorStore] = None


def get_vector_store() -> VectorStore:
    global _vector_store
    if _vector_store is None:
        _vector_store = VectorStore()
    return _vector_store
