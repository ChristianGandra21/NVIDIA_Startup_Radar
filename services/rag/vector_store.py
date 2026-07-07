"""
Vector store wrapper — ChromaDB com embedding local (sentence-transformers).
Gerencia criação, inserção e consulta da base vetorial de documentos NVIDIA.
"""
from __future__ import annotations

import logging
import os
from pathlib import Path
from typing import Any

import chromadb
from chromadb.config import Settings
from sentence_transformers import SentenceTransformer

os.environ["HF_HUB_DISABLE_SYMLINKS_WARNING"] = "1"
os.environ["TOKENIZERS_PARALLELISM"] = "false"
logging.getLogger("sentence_transformers").setLevel(logging.ERROR)
logging.getLogger("chromadb").setLevel(logging.ERROR)
logging.getLogger("httpx").setLevel(logging.ERROR)

CHROMA_DIR = Path(".cache/chroma")
COLLECTION_NAME = "nvidia_docs"


class NVIDIAVectorStore:
    def __init__(self, model_name: str = "all-MiniLM-L6-v2"):
        CHROMA_DIR.mkdir(parents=True, exist_ok=True)
        self.client = chromadb.PersistentClient(
            path=str(CHROMA_DIR),
            settings=Settings(anonymized_telemetry=False),
        )
        self.model = SentenceTransformer(model_name)
        self.collection = self._get_or_create_collection()

    def _get_or_create_collection(self):
        try:
            return self.client.get_collection(COLLECTION_NAME)
        except Exception:
            return self.client.create_collection(COLLECTION_NAME)

    def embed(self, texts: list[str]) -> list[list[float]]:
        return self.model.encode(texts, show_progress_bar=False).tolist()

    def add_documents(
        self,
        documents: list[dict[str, Any]],
    ) -> None:
        texts = [d["text"] for d in documents]
        metadatas = [d.get("metadata", {}) for d in documents]
        ids = [d["id"] for d in documents]
        embeddings = self.embed(texts)

        self.collection.add(
            ids=ids,
            documents=texts,
            metadatas=metadatas,
            embeddings=embeddings,
        )

    def query(
        self,
        query_text: str,
        n_results: int = 10,
    ) -> list[dict[str, Any]]:
        query_embedding = self.embed([query_text])[0]
        results = self.collection.query(
            query_embeddings=[query_embedding],
            n_results=n_results,
        )
        docs = []
        if results["ids"] and results["ids"][0]:
            for i in range(len(results["ids"][0])):
                docs.append({
                    "id": results["ids"][0][i],
                    "text": results["documents"][0][i],
                    "metadata": results["metadatas"][0][i] if results["metadatas"] else {},
                    "score": results["distances"][0][i] if results["distances"] else 0,
                })
        return docs

    def count(self) -> int:
        return self.collection.count()

    def delete_all(self):
        self.client.delete_collection(COLLECTION_NAME)
        self.collection = self._get_or_create_collection()
