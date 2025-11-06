-- ============================================================
-- Hub 6: Corporate - Document Storage Tables
-- ============================================================
-- Purpose: Store ingested documents (PDFs, DOCXs, etc.) with metadata and embeddings
-- Created: 2025-11-04
-- Part of: 6-Hub Schema Migration - Phase 1
-- ============================================================

-- ===================
-- Core Tables
-- ===================

-- Documents table: Stores document metadata and full-text content
CREATE TABLE IF NOT EXISTS hub6_corporate.documents (
    uuid UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    title VARCHAR(500) NOT NULL,
    content TEXT,
    doc_type VARCHAR(50) NOT NULL,  -- 'pdf', 'docx', 'pptx', 'html', 'markdown', 'text'
    file_size BIGINT CHECK (file_size >= 0),
    file_path VARCHAR(1000),
    author VARCHAR(200),
    chunk_count INTEGER DEFAULT 0 CHECK (chunk_count >= 0),
    language VARCHAR(10) DEFAULT 'en',

    -- Embedding for full document (1536 dimensions for OpenAI text-embedding-3-small)
    embedding vector(1536),

    -- Temporal tracking (bi-temporal pattern)
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    valid_from TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    valid_to TIMESTAMPTZ,  -- NULL = currently valid

    -- Additional metadata
    metadata JSONB DEFAULT '{}'::jsonb  -- Flexible storage for custom metadata
);

-- Chunks table: Stores document chunks with embeddings for semantic search
CREATE TABLE IF NOT EXISTS hub6_corporate.chunks (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    document_uuid UUID NOT NULL REFERENCES hub6_corporate.documents(uuid) ON DELETE CASCADE,
    chunk_index INTEGER NOT NULL CHECK (chunk_index >= 0),
    content TEXT NOT NULL,

    -- Embedding for chunk (1536 dimensions)
    embedding vector(1536),

    -- Temporal tracking
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),

    -- Unique constraint: one chunk per index per document
    UNIQUE(document_uuid, chunk_index)
);

-- ===================
-- Indexes for Performance
-- ===================

-- Documents indexes
CREATE INDEX IF NOT EXISTS idx_documents_doc_type ON hub6_corporate.documents(doc_type);
CREATE INDEX IF NOT EXISTS idx_documents_author ON hub6_corporate.documents(author);
CREATE INDEX IF NOT EXISTS idx_documents_language ON hub6_corporate.documents(language);
CREATE INDEX IF NOT EXISTS idx_documents_created_at ON hub6_corporate.documents(created_at DESC);
CREATE INDEX IF NOT EXISTS idx_documents_temporal ON hub6_corporate.documents(valid_from, valid_to)
    WHERE valid_to IS NULL;  -- Active documents

-- Full-text search index on title + content
CREATE INDEX IF NOT EXISTS idx_documents_fulltext ON hub6_corporate.documents
    USING gin(to_tsvector('english', title || ' ' || COALESCE(content, '')));

-- Vector similarity search index (HNSW for fast approximate nearest neighbor search)
CREATE INDEX IF NOT EXISTS idx_documents_embedding_hnsw ON hub6_corporate.documents
    USING hnsw (embedding vector_cosine_ops);

-- JSONB metadata index
CREATE INDEX IF NOT EXISTS idx_documents_metadata ON hub6_corporate.documents USING gin(metadata);

-- Chunks indexes
CREATE INDEX IF NOT EXISTS idx_chunks_document_uuid ON hub6_corporate.chunks(document_uuid);
CREATE INDEX IF NOT EXISTS idx_chunks_created_at ON hub6_corporate.chunks(created_at DESC);

-- Vector similarity search index for chunks (HNSW)
CREATE INDEX IF NOT EXISTS idx_chunks_embedding_hnsw ON hub6_corporate.chunks
    USING hnsw (embedding vector_cosine_ops);

-- ===================
-- Triggers
-- ===================

-- Auto-update updated_at timestamp on documents
CREATE OR REPLACE FUNCTION hub6_corporate.update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER update_documents_updated_at
    BEFORE UPDATE ON hub6_corporate.documents
    FOR EACH ROW
    EXECUTE FUNCTION hub6_corporate.update_updated_at_column();

-- ===================
-- Comments
-- ===================

COMMENT ON TABLE hub6_corporate.documents IS 'Ingested documents with metadata and embeddings (Hub 6: Corporate knowledge base)';
COMMENT ON TABLE hub6_corporate.chunks IS 'Document chunks with embeddings for semantic search';
COMMENT ON COLUMN hub6_corporate.documents.embedding IS 'Full document embedding (1536 dims, OpenAI text-embedding-3-small)';
COMMENT ON COLUMN hub6_corporate.chunks.embedding IS 'Chunk embedding for semantic search (1536 dims)';
COMMENT ON COLUMN hub6_corporate.documents.valid_from IS 'Business time: When this document version became valid';
COMMENT ON COLUMN hub6_corporate.documents.valid_to IS 'Business time: When this document version became invalid (NULL = currently valid)';

-- ===================
-- Success Message
-- ===================

DO $$
BEGIN
    RAISE NOTICE '✅ Hub 6 document storage tables created successfully';
    RAISE NOTICE '   - hub6_corporate.documents (with vector(1536) embedding)';
    RAISE NOTICE '   - hub6_corporate.chunks (with vector(1536) embedding)';
    RAISE NOTICE '   - 8 indexes (including HNSW vector indexes)';
    RAISE NOTICE '   - 1 trigger (auto-update updated_at)';
END $$;
