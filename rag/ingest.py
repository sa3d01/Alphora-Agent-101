"""
RAG ingestion script.

- Reads SOP documents from rag/docs/
- Builds a simple TF-IDF vector index
- Saves the index to data/embeddings/index.pkl

This is intentionally minimal: clarity > complexity.
"""

import os
import pickle
from pathlib import Path
from typing import List, Tuple

from sklearn.feature_extraction.text import TfidfVectorizer


def load_documents(docs_dir: Path) -> Tuple[List[str], List[str]]:
    """
    Load all .md and .txt files from docs_dir.

    Returns:
        texts: list of document contents
        names: list of filenames (for transparency in logs/UI)
    """
    texts: List[str] = []
    names: List[str] = []

    for fname in os.listdir(docs_dir):
        if not (fname.endswith(".md") or fname.endswith(".txt")):
            continue

        full_path = docs_dir / fname
        with open(full_path, "r", encoding="utf-8") as f:
            texts.append(f.read())
            names.append(fname)

    return texts, names


def build_index():
    # Locate docs and output directory
    project_root = Path(__file__).resolve().parents[1]   # <repo_root>/
    docs_dir = project_root / "rag" / "docs"
    embeddings_dir = project_root / "data" / "embeddings"
    embeddings_dir.mkdir(parents=True, exist_ok=True)

    if not docs_dir.exists():
        raise RuntimeError(f"Docs directory not found: {docs_dir}")

    texts, names = load_documents(docs_dir)

    if not texts:
        raise RuntimeError(f"No .md or .txt files found in {docs_dir}")

    # Simple TF-IDF vectorizer is enough for an MVP RAG
    vectorizer = TfidfVectorizer(stop_words="english")
    matrix = vectorizer.fit_transform(texts)

    index = {
        "vectorizer": vectorizer,
        "matrix": matrix,
        "doc_names": names,
        "doc_texts": texts,
    }

    index_path = embeddings_dir / "index.pkl"
    with open(index_path, "wb") as f:
        pickle.dump(index, f)

    print(f"[ingest] Indexed {len(texts)} documents → {index_path}")


if __name__ == "__main__":
    build_index()
