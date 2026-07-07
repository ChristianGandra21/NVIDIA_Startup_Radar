"""
Retriever híbrido — combina busca vetorial (ChromaDB) com busca lexical (BM25)
e reranking via LLM para retornar os trechos mais relevantes.
"""
from __future__ import annotations

from typing import Any

from rank_bm25 import BM25Okapi

from services.rag.vector_store import NVIDIAVectorStore

RERANK_SYSTEM_PROMPT = """Você é um reranker de trechos de documentação técnica.
Receba uma consulta sobre tecnologias NVIDIA e uma lista de trechos candidatos.
Reordene os trechos por relevância para a consulta.

Retorne APENAS um JSON com os índices na ordem de relevância:
{"ranked_indices": [2, 0, 3, 1, ...]}
Mantenha no máximo 5 trechos mais relevantes."""


class HybridRetriever:
    def __init__(self, vector_store: NVIDIAVectorStore):
        self.vector_store = vector_store
        self._bm25 = None
        self._documents: list[str] = []
        self._doc_ids: list[str] = []

    def _build_bm25(self):
        all_docs = self.vector_store.collection.get()
        if not all_docs["documents"]:
            self._bm25 = None
            return
        self._documents = all_docs["documents"]
        self._doc_ids = all_docs["ids"]
        tokenized = [doc.lower().split() for doc in self._documents]
        self._bm25 = BM25Okapi(tokenized)

    def retrieve(
        self,
        query: str,
        n_vector: int = 15,
        n_final: int = 5,
        use_rerank: bool = True,
    ) -> list[dict[str, Any]]:
        # 1. Vector search
        vector_results = self.vector_store.query(query, n_results=n_vector)
        vector_texts = {r["id"]: r["text"] for r in vector_results}

        # 2. BM25 lexical search
        self._build_bm25()
        bm25_scores = []
        if self._bm25:
            tokenized_query = query.lower().split()
            scores = self._bm25.get_scores(tokenized_query)
            scored = list(zip(self._doc_ids, scores))
            scored.sort(key=lambda x: x[1], reverse=True)
            for doc_id, score in scored[:n_vector]:
                if score > 0:
                    bm25_scores.append({
                        "id": doc_id,
                        "text": self._documents[self._doc_ids.index(doc_id)],
                        "score": float(score),
                    })

        # 3. Merge vector + BM25 (reciprocal rank fusion)
        combined: dict[str, dict[str, Any]] = {}
        for rank, r in enumerate(vector_results):
            doc_id = r["id"]
            rrf_score = 1.0 / (60 + rank + 1)
            combined[doc_id] = {**r, "rrf_score": rrf_score, "text": vector_texts.get(doc_id, r.get("text", ""))}

        for rank, r in enumerate(bm25_scores):
            doc_id = r["id"]
            rrf_score = 1.0 / (60 + rank + 1)
            if doc_id in combined:
                combined[doc_id]["rrf_score"] += rrf_score
            else:
                combined[doc_id] = {**r, "rrf_score": rrf_score}

        merged = sorted(combined.values(), key=lambda x: x["rrf_score"], reverse=True)

        # 4. LLM Reranking (opcional)
        if use_rerank and len(merged) > 1:
            merged = self._rerank(query, merged[:10])

        return merged[:n_final]

    def _rerank(
        self, query: str, candidates: list[dict[str, Any]]
    ) -> list[dict[str, Any]]:
        from services.agents.llm import call_llm

        parts = [f"Consulta: {query}", "\nTrechos:"]
        for i, c in enumerate(candidates):
            text = c.get("text", "")[:200]
            parts.append(f"[{i}] {text}...")

        prompt = "\n".join(parts)
        result = call_llm(RERANK_SYSTEM_PROMPT, prompt, json_mode=True)

        if isinstance(result, dict):
            indices = result.get("ranked_indices", [])
            if indices:
                reranked = []
                for idx in indices:
                    if isinstance(idx, int) and 0 <= idx < len(candidates):
                        reranked.append(candidates[idx])
                if reranked:
                    return reranked

        return candidates
