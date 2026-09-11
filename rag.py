"""RAG module for Automatic Code Improver - ChromaDB integration with Ollama embeddings."""

import os
import logging
from typing import List, Optional
import chromadb
from chromadb.config import Settings as ChromaSettings
import requests

from config import get_config

logger = logging.getLogger(__name__)


class RAGClient:
    """Client for RAG operations with ChromaDB and Ollama embeddings."""

    def __init__(self):
        self.config = get_config()
        self._client = None
        self._embedding_cache = {}

    @property
    def client(self) -> chromadb.PersistentClient:
        """Get or create ChromaDB persistent client."""
        if self._client is None:
            os.makedirs(self.config.chromadb.persist_directory, exist_ok=True)
            self._client = chromadb.PersistentClient(
                path=self.config.chromadb.persist_directory,
                settings=ChromaSettings(anonymized_telemetry=False)
            )
            logger.info(f"ChromaDB client initialized at {self.config.chromadb.persist_directory}")
        return self._client

    def _get_collection_name(self, task_name: str) -> str:
        """Get collection name for a task."""
        return f"{self.config.chromadb.collection_prefix}{task_name.replace(' ', '_').lower()}"

    def _generate_embeddings(self, texts: List[str]) -> List[List[float]]:
        """Generate embeddings using Ollama nomic-embed-text model."""
        url = f"{self.config.ollama.base_url}/api/embeddings"
        embeddings = []

        for text in texts:
            # Check cache first
            if text in self._embedding_cache:
                embeddings.append(self._embedding_cache[text])
                continue

            payload = {
                "model": self.config.ollama.embeddings_model,
                "prompt": text
            }

            try:
                response = requests.post(
                    url,
                    json=payload,
                    timeout=self.config.ollama.embeddings_timeout
                )
                response.raise_for_status()
                embedding = response.json()["embedding"]
                self._embedding_cache[text] = embedding
                embeddings.append(embedding)
            except requests.RequestException as e:
                logger.error(f"Failed to generate embedding: {e}")
                raise
            except KeyError as e:
                logger.error(f"Unexpected response format from Ollama: {e}")
                raise

        return embeddings

    def chunk_text(self, text: str, chunk_size: Optional[int] = None, chunk_overlap: Optional[int] = None) -> List[str]:
        """Split text into chunks with overlap."""
        chunk_size = chunk_size or self.config.rag.chunk_size
        chunk_overlap = chunk_overlap or self.config.rag.chunk_overlap

        if len(text) <= chunk_size:
            return [text] if text.strip() else []

        chunks = []
        start = 0
        while start < len(text):
            end = min(start + chunk_size, len(text))
            chunk = text[start:end]
            if chunk.strip():
                chunks.append(chunk)
            start += chunk_size - chunk_overlap
            if start >= len(text):
                break

        return chunks

    def ingest_record(self, task_name: str, record_path: str) -> bool:
        """Ingest an iteration record into ChromaDB with deduplication."""
        try:
            # Read the record file
            with open(record_path, "r", encoding="utf-8") as f:
                content = f.read()

            if not content.strip():
                logger.warning(f"Empty record at {record_path}, skipping ingestion")
                return False

            # Chunk the content
            chunks = self.chunk_text(content)
            if not chunks:
                logger.warning(f"No valid chunks from {record_path}")
                return False

            # Generate embeddings
            embeddings = self._generate_embeddings(chunks)

            # Get or create collection
            collection_name = self._get_collection_name(task_name)
            collection = self.client.get_or_create_collection(name=collection_name)

            # Prepare IDs for deduplication (hash of chunk content)
            ids = [f"{task_name}_{hash(chunk) % 1000000}_{i}" for i, chunk in enumerate(chunks)]

            # Check for existing IDs to avoid duplicates
            existing = collection.get(ids=ids, include=[])
            existing_ids = set(existing["ids"]) if existing["ids"] else set()

            new_chunks = []
            new_embeddings = []
            new_ids = []
            new_metadatas = []

            for i, (chunk, embedding, chunk_id) in enumerate(zip(chunks, embeddings, ids)):
                if chunk_id not in existing_ids:
                    new_chunks.append(chunk)
                    new_embeddings.append(embedding)
                    new_ids.append(chunk_id)
                    new_metadatas.append({
                        "task_name": task_name,
                        "record_path": record_path,
                        "chunk_index": i
                    })

            if new_chunks:
                collection.add(
                    documents=new_chunks,
                    embeddings=new_embeddings,
                    ids=new_ids,
                    metadatas=new_metadatas
                )
                logger.info(f"Ingested {len(new_chunks)} new chunks for task '{task_name}' (skipped {len(chunks) - len(new_chunks)} duplicates)")
            else:
                logger.info(f"No new chunks to ingest for task '{task_name}' (all duplicates)")

            return True

        except Exception as e:
            logger.error(f"Failed to ingest record {record_path}: {e}")
            raise

    def retrieve_context(self, task_name: str, query_text: str, top_k: Optional[int] = None) -> List[dict]:
        """Retrieve relevant context chunks for a task and query."""
        try:
            top_k = top_k or self.config.rag.top_k
            collection_name = self._get_collection_name(task_name)

            # Check if collection exists
            try:
                collection = self.client.get_collection(name=collection_name)
            except Exception:
                logger.info(f"No collection found for task '{task_name}', returning empty context")
                return []

            # Generate embedding for query
            query_embedding = self._generate_embeddings([query_text])[0]

            # Query collection
            results = collection.query(
                query_embeddings=[query_embedding],
                n_results=top_k,
                include=["documents", "metadatas", "distances"]
            )

            # Format results
            chunks = []
            if results["documents"] and results["documents"][0]:
                for i, doc in enumerate(results["documents"][0]):
                    chunks.append({
                        "content": doc,
                        "metadata": results["metadatas"][0][i] if results["metadatas"] else {},
                        "distance": results["distances"][0][i] if results["distances"] else None
                    })

            logger.info(f"Retrieved {len(chunks)} context chunks for task '{task_name}'")
            return chunks

        except Exception as e:
            logger.error(f"Failed to retrieve context for task '{task_name}': {e}")
            # Return empty context on error (graceful degradation)
            return []


# Global instance
_rag_client = None


def get_rag_client() -> RAGClient:
    """Get global RAG client instance."""
    global _rag_client
    if _rag_client is None:
        _rag_client = RAGClient()
    return _rag_client