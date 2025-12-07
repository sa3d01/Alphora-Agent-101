-- Enable pgvector extension
CREATE EXTENSION IF NOT EXISTS vector;

-- Drop existing table if it exists
DROP TABLE IF EXISTS sops;

-- Create SOPs table with correct structure
CREATE TABLE sops (
                      id SERIAL PRIMARY KEY,
                      tenant_id VARCHAR(255) NOT NULL,
                      title VARCHAR(500) NOT NULL,
                      content TEXT NOT NULL,
                      category VARCHAR(255),
                      chunk_index INTEGER,
                      tags TEXT[],
                      metadata JSONB,
                      embedding vector(384),
                      created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                      updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create indexes
CREATE INDEX idx_sops_tenant ON sops(tenant_id);
CREATE INDEX idx_sops_category ON sops(category);
CREATE INDEX idx_sops_tenant_category ON sops(tenant_id, category);