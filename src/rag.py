# src/rag.py

import json
from dataclasses import dataclass
from pathlib import Path
from typing import List, Optional, Dict, Any

import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


@dataclass
class SOPDocument:
    id: str
    client_id: str
    title: str
    ticket_types: List[str]
    content: str


@dataclass
class RAGResult:
    sop: SOPDocument
    score: float


class RAGKnowledgeBase:
    """
    Very small, in-memory RAG implementation using TF-IDF.
    Suitable for demo; in real life we'd use embeddings + vector DB.
    """

    def __init__(self, sops: List[SOPDocument]) -> None:
        self.sops = sops
        self.vectorizer = TfidfVectorizer(stop_words="english")
        self._fit()

    @classmethod
    def from_file(cls, path: str) -> "RAGKnowledgeBase":
        raw = json.loads(Path(path).read_text(encoding="utf-8"))
        sops = [
            SOPDocument(
                id=item["id"],
                client_id=item.get("client_id", "default"),
                title=item["title"],
                ticket_types=item.get("ticket_types", []),
                content=item["content"],
            )
            for item in raw
        ]
        return cls(sops)

    def _fit(self) -> None:
        corpus = [doc.content for doc in self.sops]
        if corpus:
            self.doc_matrix = self.vectorizer.fit_transform(corpus)
        else:
            self.doc_matrix = None

    def retrieve(
            self,
            query: str,
            client_id: Optional[str] = None,
            ticket_type: Optional[str] = None,
            top_k: int = 3,
    ) -> List[RAGResult]:
        if self.doc_matrix is None:
            return []

        # filter docs by tenant and ticket type
        filtered_indices = []
        filtered_docs: List[SOPDocument] = []

        for idx, doc in enumerate(self.sops):
            if client_id and doc.client_id not in (client_id, "default"):
                continue
            if ticket_type and ticket_type not in doc.ticket_types:
                continue
            filtered_indices.append(idx)
            filtered_docs.append(doc)

        if not filtered_docs:
            return []

        sub_matrix = self.doc_matrix[filtered_indices]
        q_vec = self.vectorizer.transform([query])
        sims = cosine_similarity(q_vec, sub_matrix)[0]

        top_indices = np.argsort(sims)[::-1][:top_k]

        results: List[RAGResult] = []
        for rank in top_indices:
            score = float(sims[rank])
            if score <= 0:
                continue
            doc = filtered_docs[rank]
            results.append(RAGResult(sop=doc, score=round(score, 3)))

        return results

    def to_dict(self) -> Dict[str, Any]:
        return {
            "num_sops": len(self.sops),
            "clients": sorted({d.client_id for d in self.sops}),
        }
