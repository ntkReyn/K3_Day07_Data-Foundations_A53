from __future__ import annotations

from typing import Any, Callable

from .chunking import _dot, compute_similarity
from .embeddings import _mock_embed
from .models import Document


class EmbeddingStore:
    """
    A vector store for text chunks.

    Tries to use ChromaDB if available; falls back to an in-memory store.
    The embedding_fn parameter allows injection of mock embeddings for tests.
    """

    def __init__(
        self,
        collection_name: str = "documents",
        embedding_fn: Callable[[str], list[float]] | None = None,
    ) -> None:
        self._embedding_fn = embedding_fn or _mock_embed
        self._collection_name = collection_name
        self._use_chroma = False
        self._store: list[dict[str, Any]] = []
        self._collection = None
        self._next_index = 0

        try:
            import chromadb  # noqa: F401

            try:
                from chromadb import Client

                self._collection = Client().get_or_create_collection(name=self._collection_name)
                self._use_chroma = True
            except Exception:
                self._use_chroma = False
                self._collection = None
        except Exception:
            self._use_chroma = False
            self._collection = None

    def _make_record(self, doc: Document) -> dict[str, Any]:
        embedding = self._embedding_fn(doc.content)
        metadata = dict(doc.metadata or {})
        metadata["doc_id"] = doc.id

        return {
            "id": f"{self._collection_name}:{self._next_index}:{doc.id}",
            "content": doc.content,
            "metadata": metadata,
            "embedding": embedding,
            "doc_id": doc.id,
        }

    def _search_records(self, query: str, records: list[dict[str, Any]], top_k: int) -> list[tuple[float, dict[str, Any]]]:
        query_embedding = self._embedding_fn(query)
        scored_records: list[tuple[float, dict[str, Any]]] = []

        for record in records:
            embedding = record.get("embedding", [])
            score = compute_similarity(query_embedding, embedding)
            scored_records.append((score, record))

        scored_records.sort(key=lambda item: item[0], reverse=True)
        return scored_records[:top_k]

    def add_documents(self, docs: list[Document]) -> None:
        """
        Embed each document's content and store it.

        For ChromaDB: use collection.add(ids=[...], documents=[...], embeddings=[...])
        For in-memory: append dicts to self._store
        """
        for doc in docs:
            record = self._make_record(doc)
            if self._use_chroma and self._collection is not None:
                try:
                    self._collection.add(
                        ids=[record["id"]],
                        documents=[doc.content],
                        embeddings=[record["embedding"]],
                        metadatas=[record["metadata"]],
                    )
                except Exception:
                    self._use_chroma = False

            self._store.append(record)
            self._next_index += 1

    def search(self, query: str, top_k: int = 5) -> list[dict[str, Any]]:
        """
        Find the top_k most similar documents to query.

        For in-memory: compute dot product of query embedding vs all stored embeddings.
        """
        if top_k <= 0:
            return []

        results: list[dict[str, Any]] = []
        for score, record in self._search_records(query, self._store, top_k):
            results.append(
                {
                    "id": record["id"],
                    "content": record["content"],
                    "metadata": record["metadata"],
                    "doc_id": record["doc_id"],
                    "score": score,
                }
            )

        return results

    def get_collection_size(self) -> int:
        """Return the total number of stored chunks."""
        return len(self._store)

    def search_with_filter(self, query: str, top_k: int = 3, metadata_filter: dict = None) -> list[dict]:
        """
        Search with optional metadata pre-filtering.

        First filter stored chunks by metadata_filter, then run similarity search.
        """
        if top_k <= 0:
            return []

        if metadata_filter is None:
            candidates = list(self._store)
        else:
            candidates = [
                record
                for record in self._store
                if all(record.get("metadata", {}).get(key) == value for key, value in metadata_filter.items())
            ]

        results: list[dict[str, Any]] = []
        for score, record in self._search_records(query, candidates, top_k):
            results.append(
                {
                    "id": record["id"],
                    "content": record["content"],
                    "metadata": record["metadata"],
                    "doc_id": record["doc_id"],
                    "score": score,
                }
            )

        return results

    def delete_document(self, doc_id: str) -> bool:
        """
        Remove all chunks belonging to a document.

        Returns True if any chunks were removed, False otherwise.
        """
        matching_records = [record for record in self._store if record.get("doc_id") == doc_id]
        if not matching_records:
            return False

        self._store = [record for record in self._store if record.get("doc_id") != doc_id]
        if self._use_chroma and self._collection is not None:
            try:
                self._collection.delete(ids=[record["id"] for record in matching_records])
            except Exception:
                pass

        return True
