"""
RAG (Retrieval-Augmented Generation) module for Alphora Agent 101.

This module provides semantic search capabilities over SOP documentation
using sentence-transformers for embeddings and pgvector for similarity search.
"""

from .embeddings import EmbeddingService, get_embedding_service
from .ingestion import DocumentChunker, SOPIngester
from .retrieval import SOPRetriever
from .sample_sops import get_sample_sops, get_all_sample_sops

__all__ = [
    'EmbeddingService',
    'get_embedding_service',
    'DocumentChunker',
    'SOPIngester',
    'SOPRetriever',
    'get_sample_sops',
    'get_all_sample_sops',
]

__version__ = '1.0.0'