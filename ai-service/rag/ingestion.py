"""
RAG Document Ingestion Pipeline
Handles chunking, embedding, and storing SOPs in the vector database
"""

import re
import json
from typing import List, Dict, Optional
from datetime import datetime
import psycopg2
from psycopg2.extras import execute_values, Json
from .embeddings import get_embedding_service


class DocumentChunker:
    """Splits documents into semantic chunks for better retrieval."""

    def __init__(self, chunk_size: int = 500, overlap: int = 50):
        """
        Args:
            chunk_size: Target size of each chunk in characters
            overlap: Number of characters to overlap between chunks
        """
        self.chunk_size = chunk_size
        self.overlap = overlap

    def chunk_by_paragraphs(self, text: str) -> List[str]:
        """
        Split text into chunks, preserving paragraph boundaries where possible.

        Args:
            text: Input document text

        Returns:
            List of text chunks
        """
        # Split by double newlines (paragraphs)
        paragraphs = re.split(r'\n\s*\n', text)

        chunks = []
        current_chunk = ""

        for para in paragraphs:
            para = para.strip()
            if not para:
                continue

            # If adding this paragraph exceeds chunk size, save current and start new
            if len(current_chunk) + len(para) > self.chunk_size and current_chunk:
                chunks.append(current_chunk.strip())
                # Start new chunk with overlap from previous
                current_chunk = current_chunk[-self.overlap:] + " " + para
            else:
                current_chunk += "\n\n" + para if current_chunk else para

        # Add final chunk
        if current_chunk:
            chunks.append(current_chunk.strip())

        return chunks

    def chunk_by_sentences(self, text: str) -> List[str]:
        """Alternative chunking strategy using sentence boundaries."""
        sentences = re.split(r'[.!?]+\s+', text)

        chunks = []
        current_chunk = ""

        for sentence in sentences:
            sentence = sentence.strip()
            if not sentence:
                continue

            if len(current_chunk) + len(sentence) > self.chunk_size and current_chunk:
                chunks.append(current_chunk.strip())
                current_chunk = sentence
            else:
                current_chunk += " " + sentence if current_chunk else sentence

        if current_chunk:
            chunks.append(current_chunk.strip())

        return chunks


class SOPIngester:
    """Ingests and stores SOPs in the vector database."""

    def __init__(self, db_config: Dict[str, str]):
        """
        Args:
            db_config: Database connection parameters
                      {host, port, database, user, password}
        """
        self.db_config = db_config
        self.chunker = DocumentChunker()
        self.embedding_service = get_embedding_service()

    def _get_connection(self):
        """Create database connection."""
        return psycopg2.connect(**self.db_config)

    def ingest_sop(
            self,
            tenant_id: str,
            title: str,
            content: str,
            category: str,
            tags: Optional[List[str]] = None,
            metadata: Optional[Dict] = None
    ) -> int:
        """
        Ingest a single SOP document.

        Args:
            tenant_id: Tenant/MSP identifier for data isolation
            title: SOP title
            content: Full SOP text content
            category: Category (e.g., "password_reset", "system_restart")
            tags: Optional list of tags for filtering
            metadata: Optional metadata dict (client-specific config, etc.)

        Returns:
            Number of chunks created
        """
        # Step 1: Chunk the document
        chunks = self.chunker.chunk_by_paragraphs(content)
        print(f"Created {len(chunks)} chunks for SOP: {title}")

        # Step 2: Generate embeddings for all chunks
        embeddings = self.embedding_service.embed_batch(chunks)

        # Step 3: Store in database
        conn = self._get_connection()
        cur = conn.cursor()

        try:
            # Prepare data for batch insert
            records = []
            for i, (chunk, embedding) in enumerate(zip(chunks, embeddings)):
                records.append((
                    tenant_id,
                    title,
                    chunk,
                    category,
                    i,  # chunk_index
                    tags or [],
                    Json(metadata or {}),  # Use Json adapter for dict
                    embedding,
                    datetime.utcnow()
                ))

            # Batch insert using execute_values for efficiency
            insert_query = """
                           INSERT INTO sops (
                               tenant_id, title, content, category, chunk_index,
                               tags, metadata, embedding, created_at
                           )
                           VALUES %s \
                           """

            execute_values(
                cur,
                insert_query,
                records,
                template="(%s, %s, %s, %s, %s, %s, %s, %s, %s)"
            )

            conn.commit()
            print(f"Successfully ingested {len(chunks)} chunks")
            return len(chunks)

        except Exception as e:
            conn.rollback()
            print(f"Error ingesting SOP: {e}")
            raise
        finally:
            cur.close()
            conn.close()

    def ingest_batch(self, sops: List[Dict]) -> Dict[str, int]:
        """
        Ingest multiple SOPs in batch.

        Args:
            sops: List of SOP dictionaries, each containing:
                  {tenant_id, title, content, category, tags, metadata}

        Returns:
            Dictionary with ingestion statistics
        """
        total_chunks = 0
        successful = 0
        failed = 0

        for sop in sops:
            try:
                chunks = self.ingest_sop(
                    tenant_id=sop['tenant_id'],
                    title=sop['title'],
                    content=sop['content'],
                    category=sop['category'],
                    tags=sop.get('tags'),
                    metadata=sop.get('metadata')
                )
                total_chunks += chunks
                successful += 1
            except Exception as e:
                print(f"Failed to ingest SOP '{sop['title']}': {e}")
                failed += 1

        return {
            'total_sops': len(sops),
            'successful': successful,
            'failed': failed,
            'total_chunks': total_chunks
        }

    def delete_tenant_sops(self, tenant_id: str) -> int:
        """
        Delete all SOPs for a specific tenant.

        Args:
            tenant_id: Tenant identifier

        Returns:
            Number of records deleted
        """
        conn = self._get_connection()
        cur = conn.cursor()

        try:
            cur.execute("DELETE FROM sops WHERE tenant_id = %s", (tenant_id,))
            deleted = cur.rowcount
            conn.commit()
            print(f"Deleted {deleted} SOP chunks for tenant {tenant_id}")
            return deleted
        finally:
            cur.close()
            conn.close()