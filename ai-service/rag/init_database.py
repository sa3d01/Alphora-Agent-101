"""
Initialize RAG database with sample SOPs
Run this script once to populate the database
"""

import os
import sys

# Add parent directory to Python path
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, parent_dir)

from rag.ingestion import SOPIngester
from rag.sample_sops import get_all_sample_sops


def init_database():
    """Initialize the database with sample SOPs."""

    # Database configuration (adjust as needed)
    db_config = {
        'host': os.getenv('DB_HOST', 'localhost'),
        'port': os.getenv('DB_PORT', '5432'),
        'database': os.getenv('DB_NAME', 'alphora_agent'),
        'user': os.getenv('DB_USER', 'postgres'),
        'password': os.getenv('DB_PASSWORD', 'postgres')
    }

    print("Initializing RAG database...")
    print(f"Connecting to: {db_config['host']}:{db_config['port']}/{db_config['database']}")

    # Create ingester
    ingester = SOPIngester(db_config)

    # Get sample SOPs
    sops = get_all_sample_sops()
    print(f"\nFound {len(sops)} sample SOPs to ingest")

    # Ingest batch
    print("\nIngesting SOPs...")
    results = ingester.ingest_batch(sops)

    # Print results
    print("\n" + "="*50)
    print("INGESTION COMPLETE")
    print("="*50)
    print(f"Total SOPs: {results['total_sops']}")
    print(f"Successful: {results['successful']}")
    print(f"Failed: {results['failed']}")
    print(f"Total chunks created: {results['total_chunks']}")
    print("="*50)

    if results['failed'] > 0:
        print("\n⚠️  Some SOPs failed to ingest. Check logs above for details.")
        return False

    print("\n✅ Database initialized successfully!")
    return True


if __name__ == "__main__":
    success = init_database()
    exit(0 if success else 1)