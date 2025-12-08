"""
Simple retrieval layer for RAG.

- Loads the TF-IDF index created by ingest.py
- Given a query, returns top-K similar SOPs

This is enough to demonstrate:
- "RAG database"
- "Simple retrieval mechanism"
"""

import pickle
from pathlib import Path
from typing import List

from sklearn.metrics.pairwise import cosine_similarity

from src.models import RetrievalResult  # src is a package; see note below


class Retriever:
    def __init__(self, top_k: int = 2):
        self.top_k = top_k
        self._load_index()

    def _load_index(self):
        project_root = Path(__file__).resolve().parents[1]   # <repo_root>/
        index_path = project_root / "data" / "embeddings" / "index.pkl"

        if not index_path.exists():
            raise RuntimeError(
                f"Embedding index not found at {index_path}. "
                f"Run `python rag/ingest.py` first."
            )

        with open(index_path, "rb") as f:
            index = pickle.load(f)

        self.vectorizer = index["vectorizer"]
        self.matrix = index["matrix"]
        self.doc_names: List[str] = index["doc_names"]
        self.doc_texts: List[str] = index["doc_texts"]

    def retrieve(self, query: str) -> RetrievalResult:
        """
        Retrieve top-K documents relevant to the query.

        Returns:
            RetrievalResult with:
            - documents: list of SOP contents (strings)
            - doc_names: matching filenames
        """
        query = query.strip()
        if not query:
            return RetrievalResult(documents=[], doc_names=[])

        query_vec = self.vectorizer.transform([query])
        similarities = cosine_similarity(query_vec, self.matrix)[0]

        # Rank docs by similarity descending
        ranked_indices = similarities.argsort()[::-1]

        selected_docs: List[str] = []
        selected_names: List[str] = []

        for idx in ranked_indices[: self.top_k]:
            if similarities[idx] <= 0:
                # No useful match; similarity is zero
                continue
            selected_docs.append(self.doc_texts[idx])
            selected_names.append(self.doc_names[idx])

        return RetrievalResult(documents=selected_docs, doc_names=selected_names)
