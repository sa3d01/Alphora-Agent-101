"""
RAG Retrieval Module
Performs semantic search over the vector database using pgvector
"""

from typing import List, Dict, Optional
import psycopg2
from psycopg2.extras import RealDictCursor
from .embeddings import get_embedding_service


class SOPRetriever:
    """Retrieves relevant SOPs using vector similarity search."""

    def __init__(self, db_config: Dict[str, str]):
        """
        Args:
            db_config: Database connection parameters
        """
        self.db_config = db_config
        self.embedding_service = get_embedding_service()

    def _get_connection(self):
        """Create database connection with dict cursor."""
        return psycopg2.connect(**self.db_config, cursor_factory=RealDictCursor)

    def search(
            self,
            query: str,
            tenant_id: str,
            top_k: int = 5,
            category_filter: Optional[str] = None,
            similarity_threshold: float = 0.5
    ) -> List[Dict]:
        """
        Perform semantic search for relevant SOPs.

        Args:
            query: Search query (ticket description)
            tenant_id: Tenant ID for data isolation
            top_k: Number of results to return
            category_filter: Optional category filter (e.g., "password_reset")
            similarity_threshold: Minimum similarity score (0-1)

        Returns:
            List of matching SOP chunks with metadata and similarity scores
        """
        # Step 1: Generate query embedding
        query_embedding = self.embedding_service.embed_text(query)

        # Step 2: Perform vector similarity search using pgvector
        conn = self._get_connection()
        cur = conn.cursor()

        try:
            # Build query with optional category filter
            base_query = """
                         SELECT
                             id,
                             tenant_id,
                             title,
                             content,
                             category,
                             chunk_index,
                             tags,
                             metadata,
                             1 - (embedding <=> %s::vector) as similarity
                         FROM sops
                         WHERE tenant_id = %s \
                         """

            params = [query_embedding, tenant_id]

            # Add category filter if provided
            if category_filter:
                base_query += " AND category = %s"
                params.append(category_filter)

            # Add similarity threshold and ordering
            base_query += """
                AND 1 - (embedding <=> %s::vector) >= %s
                ORDER BY embedding <=> %s::vector
                LIMIT %s
            """

            # Add threshold and limit parameters
            params.extend([query_embedding, similarity_threshold, query_embedding, top_k])

            cur.execute(base_query, params)
            results = cur.fetchall()

            # Convert to list of dicts
            return [dict(row) for row in results]

        finally:
            cur.close()
            conn.close()

    def search_by_category(
            self,
            tenant_id: str,
            category: str,
            limit: int = 10
    ) -> List[Dict]:
        """
        Retrieve SOPs by category without semantic search.
        Useful for known workflows.

        Args:
            tenant_id: Tenant ID
            category: Category to filter by
            limit: Maximum number of results

        Returns:
            List of SOP chunks
        """
        conn = self._get_connection()
        cur = conn.cursor()

        try:
            query = """
                    SELECT
                        id, tenant_id, title, content, category,
                        chunk_index, tags, metadata
                    FROM sops
                    WHERE tenant_id = %s AND category = %s
                    ORDER BY chunk_index
                        LIMIT %s \
                    """

            cur.execute(query, (tenant_id, category, limit))
            results = cur.fetchall()
            return [dict(row) for row in results]

        finally:
            cur.close()
            conn.close()

    def get_sop_by_title(
            self,
            tenant_id: str,
            title: str
    ) -> List[Dict]:
        """
        Retrieve all chunks of a specific SOP by title.

        Args:
            tenant_id: Tenant ID
            title: Exact SOP title

        Returns:
            List of chunks ordered by chunk_index
        """
        conn = self._get_connection()
        cur = conn.cursor()

        try:
            query = """
                    SELECT
                        id, tenant_id, title, content, category,
                        chunk_index, tags, metadata
                    FROM sops
                    WHERE tenant_id = %s AND title = %s
                    ORDER BY chunk_index \
                    """

            cur.execute(query, (tenant_id, title))
            results = cur.fetchall()
            return [dict(row) for row in results]

        finally:
            cur.close()
            conn.close()

    def hybrid_search(
            self,
            query: str,
            tenant_id: str,
            category: str,
            top_k: int = 3
    ) -> List[Dict]:
        """
        Hybrid search: first filter by category, then semantic search.
        This is useful when you know the category (from classification)
        and want the most relevant procedure within that category.

        Args:
            query: Search query
            tenant_id: Tenant ID
            category: Category filter
            top_k: Number of results

        Returns:
            List of relevant SOP chunks
        """
        return self.search(
            query=query,
            tenant_id=tenant_id,
            top_k=top_k,
            category_filter=category,
            similarity_threshold=0.3  # Lower threshold when category is known
        )

    def get_statistics(self, tenant_id: str) -> Dict:
        """
        Get statistics about the SOP database for a tenant.

        Args:
            tenant_id: Tenant ID

        Returns:
            Dictionary with statistics
        """
        conn = self._get_connection()
        cur = conn.cursor()

        try:
            query = """
                    SELECT
                        COUNT(DISTINCT title) as total_sops,
                        COUNT(*) as total_chunks,
                        COUNT(DISTINCT category) as total_categories,
                        array_agg(DISTINCT category) as categories
                    FROM sops
                    WHERE tenant_id = %s \
                    """

            cur.execute(query, (tenant_id,))
            result = cur.fetchone()
            return dict(result) if result else {}

        finally:
            cur.close()
            conn.close()