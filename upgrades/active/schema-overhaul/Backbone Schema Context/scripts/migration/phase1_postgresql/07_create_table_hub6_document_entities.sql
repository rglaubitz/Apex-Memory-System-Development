-- Hub 6 Corporate: Document-Entity relationship table
--
-- Purpose: Track which entities appear in which documents (many-to-many)
-- Supports mention counts and confidence scores for entity extraction
--
-- Database: PostgreSQL 15.4
-- Schema: hub6_corporate

CREATE TABLE IF NOT EXISTS hub6_corporate.document_entities (
    document_uuid UUID NOT NULL REFERENCES hub6_corporate.documents(uuid) ON DELETE CASCADE,
    entity_uuid UUID NOT NULL REFERENCES hub6_corporate.entities(uuid) ON DELETE CASCADE,
    relationship_type VARCHAR(50) NOT NULL DEFAULT 'MENTIONS',

    -- Extraction metadata
    confidence REAL CHECK (confidence >= 0 AND confidence <= 1),
    mention_count INTEGER DEFAULT 1 CHECK (mention_count >= 1),

    -- Tracking
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),

    PRIMARY KEY (document_uuid, entity_uuid, relationship_type)
);

-- Indexes for common queries
CREATE INDEX IF NOT EXISTS idx_hub6_doc_entities_document ON hub6_corporate.document_entities (document_uuid);
CREATE INDEX IF NOT EXISTS idx_hub6_doc_entities_entity ON hub6_corporate.document_entities (entity_uuid);
CREATE INDEX IF NOT EXISTS idx_hub6_doc_entities_type ON hub6_corporate.document_entities (relationship_type);

-- Update timestamp trigger
CREATE OR REPLACE FUNCTION hub6_corporate.update_document_entities_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER update_hub6_document_entities_updated_at
    BEFORE UPDATE ON hub6_corporate.document_entities
    FOR EACH ROW
    EXECUTE FUNCTION hub6_corporate.update_document_entities_updated_at();

COMMENT ON TABLE hub6_corporate.document_entities IS 'Many-to-many relationship linking documents and entities';
COMMENT ON COLUMN hub6_corporate.document_entities.document_uuid IS 'Foreign key to documents table';
COMMENT ON COLUMN hub6_corporate.document_entities.entity_uuid IS 'Foreign key to entities table';
COMMENT ON COLUMN hub6_corporate.document_entities.relationship_type IS 'Type of relationship (MENTIONS, CREATED_BY, etc.)';
COMMENT ON COLUMN hub6_corporate.document_entities.confidence IS 'Extraction confidence score (0.0-1.0)';
COMMENT ON COLUMN hub6_corporate.document_entities.mention_count IS 'Number of times entity is mentioned in document';
COMMENT ON COLUMN hub6_corporate.document_entities.created_at IS 'When relationship was first created';
COMMENT ON COLUMN hub6_corporate.document_entities.updated_at IS 'When relationship was last updated';
