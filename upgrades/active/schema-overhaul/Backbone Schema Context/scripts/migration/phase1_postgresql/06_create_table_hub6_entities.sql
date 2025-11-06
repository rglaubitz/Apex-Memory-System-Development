-- Hub 6 Corporate: Entity storage table
--
-- Purpose: Store extracted entities (people, companies, locations, etc.)
-- from corporate documents for knowledge graph and semantic search
--
-- Database: PostgreSQL 15.4
-- Schema: hub6_corporate
-- Extensions: uuid-ossp, pgvector, pg_trgm

CREATE TABLE IF NOT EXISTS hub6_corporate.entities (
    uuid UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name VARCHAR(500) NOT NULL,
    entity_type VARCHAR(100) NOT NULL,  -- person, organization, location, product, etc.
    summary TEXT,

    -- Extracted from documents
    source_document_uuid UUID REFERENCES hub6_corporate.documents(uuid) ON DELETE CASCADE,
    confidence_score REAL CHECK (confidence_score >= 0 AND confidence_score <= 1),

    -- Semantic search
    embedding vector(1536),  -- OpenAI text-embedding-3-small

    -- Bi-temporal tracking
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    valid_from TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    valid_to TIMESTAMPTZ,

    -- Metadata and attributes
    metadata JSONB DEFAULT '{}'::jsonb
);

-- Indexes for common queries
CREATE INDEX IF NOT EXISTS idx_hub6_entities_name ON hub6_corporate.entities (name);
CREATE INDEX IF NOT EXISTS idx_hub6_entities_type ON hub6_corporate.entities (entity_type);
CREATE INDEX IF NOT EXISTS idx_hub6_entities_source ON hub6_corporate.entities (source_document_uuid);
CREATE INDEX IF NOT EXISTS idx_hub6_entities_embedding ON hub6_corporate.entities USING ivfflat (embedding vector_cosine_ops);
CREATE INDEX IF NOT EXISTS idx_hub6_entities_metadata ON hub6_corporate.entities USING gin (metadata);

-- Trigram index for fuzzy name search
CREATE INDEX IF NOT EXISTS idx_hub6_entities_name_trgm ON hub6_corporate.entities USING gin (name gin_trgm_ops);

-- Update timestamp trigger
CREATE TRIGGER update_hub6_entities_updated_at
    BEFORE UPDATE ON hub6_corporate.entities
    FOR EACH ROW
    EXECUTE FUNCTION hub6_corporate.update_updated_at_column();

COMMENT ON TABLE hub6_corporate.entities IS 'Extracted entities from corporate documents with semantic embeddings and bi-temporal tracking';
COMMENT ON COLUMN hub6_corporate.entities.uuid IS 'Primary key (UUID v4)';
COMMENT ON COLUMN hub6_corporate.entities.name IS 'Entity name/title';
COMMENT ON COLUMN hub6_corporate.entities.entity_type IS 'Type: person, organization, location, product, etc.';
COMMENT ON COLUMN hub6_corporate.entities.summary IS 'Entity description/summary';
COMMENT ON COLUMN hub6_corporate.entities.source_document_uuid IS 'Document where entity was extracted';
COMMENT ON COLUMN hub6_corporate.entities.confidence_score IS 'Extraction confidence (0.0-1.0)';
COMMENT ON COLUMN hub6_corporate.entities.embedding IS 'Semantic embedding vector (1536 dimensions)';
COMMENT ON COLUMN hub6_corporate.entities.created_at IS 'System time: when record was created';
COMMENT ON COLUMN hub6_corporate.entities.updated_at IS 'System time: when record was last updated';
COMMENT ON COLUMN hub6_corporate.entities.valid_from IS 'Business time: when entity became valid';
COMMENT ON COLUMN hub6_corporate.entities.valid_to IS 'Business time: when entity became invalid (NULL = currently valid)';
COMMENT ON COLUMN hub6_corporate.entities.metadata IS 'Additional attributes in JSON format';
